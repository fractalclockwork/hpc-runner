# runner.py - Execution-agnostic job runner
from __future__ import annotations

import os
import platform
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import structlog

from .config import Solver, System, Job
from .parser import extract_metrics, validate_metrics

logger = structlog.get_logger()


def probe_processor() -> str:
    """Return CPU architecture of the host (e.g. x86_64, aarch64)."""
    return platform.machine() or "unknown"


@dataclass
class RunResult:
    """Result of a single job run."""
    job_name: str
    solver_name: str
    system_name: str
    returncode: int
    stdout: str
    stderr: str
    runtime_seconds: float
    timestamp: str
    metrics: dict[str, Any] = field(default_factory=dict)
    validation_errors: list[str] = field(default_factory=list)
    passed: bool = False
    raw_logs: str = ""
    processor: str | None = None


def _build_env(system: System, base_env: dict[str, str] | None = None) -> dict[str, str]:
    """Merge system env with base environment."""
    env = dict(os.environ)
    if base_env:
        env.update(base_env)
    env.update(system.env)
    return env


def run_job(
    job: Job,
    solver: Solver,
    system: System,
    *,
    capture_output: bool = True,
) -> RunResult:
    """
    Execute a job by running the solver script with system environment.
    Platform remains scheduler-agnostic; solver script may call SLURM, MPI, etc.
    """
    start = datetime.now(timezone.utc)
    processor = probe_processor()
    logger.info(
        "runner.start",
        job=job.name,
        solver=solver.name,
        system=system.name,
        entrypoint=solver.entrypoint,
    )

    entrypoint_path = Path(solver.entrypoint).resolve()
    cwd = Path(solver.cwd).resolve() if solver.cwd else entrypoint_path.parent
    env = _build_env(system)

    cmd: list[str] = []
    if entrypoint_path.suffix == ".py":
        cmd = ["python3", str(entrypoint_path)]
    elif entrypoint_path.suffix == ".sh":
        cmd = ["bash", str(entrypoint_path)]
    else:
        cmd = [str(entrypoint_path)]

    timeout_sec = job.timeout_seconds if job.timeout_seconds is not None else 3600

    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            env=env,
            capture_output=capture_output,
            text=True,
            timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired as e:
        end = datetime.now(timezone.utc)
        runtime = (end - start).total_seconds()
        timeout_msg = f"Job timed out after {timeout_sec}s"
        run_result = RunResult(
            job_name=job.name,
            solver_name=solver.name,
            system_name=system.name,
            returncode=-1,
            stdout=(e.stdout or "") if capture_output else "",
            stderr=timeout_msg,
            runtime_seconds=runtime,
            timestamp=end.isoformat(),
            validation_errors=[],
            passed=False,
            metrics={"runtime_seconds": runtime},
            processor=processor,
        )
        logger.warning("runner.timeout", job=job.name, runtime=runtime)
        return run_result
    except Exception as e:
        end = datetime.now(timezone.utc)
        runtime = (end - start).total_seconds()
        error_msg = f"Execution failed: {e}"
        run_result = RunResult(
            job_name=job.name,
            solver_name=solver.name,
            system_name=system.name,
            returncode=-1,
            stdout="",
            stderr=error_msg,
            runtime_seconds=runtime,
            timestamp=end.isoformat(),
            validation_errors=[],
            passed=False,
            metrics={"runtime_seconds": runtime},
            processor=processor,
        )
        logger.exception("runner.error", job=job.name, error=str(e))
        return run_result

    end = datetime.now(timezone.utc)
    runtime = (end - start).total_seconds()
    raw_logs = (result.stdout or "") + "\n" + (result.stderr or "")

    # Basic pass/fail from returncode
    success_criteria = job.success_criteria or {}
    expected_rc = success_criteria.get("returncode", 0)
    passed = result.returncode == expected_rc

    # Extract metrics if solver has parser_config (resolve relative to solver dir if needed)
    metrics: dict[str, Any] = {}
    validation_errors: list[str] = []
    parser_config_path = Path(solver.parser_config) if solver.parser_config else None
    if parser_config_path is not None:
        if not parser_config_path.exists():
            parser_config_path = (entrypoint_path.parent / parser_config_path).resolve()
        if parser_config_path.exists():
            metrics = extract_metrics(raw_logs, config_path=parser_config_path)
    # Always include runtime_seconds so all solvers show metrics on the Home page
    metrics["runtime_seconds"] = runtime

    # if defined min/max bounds, check extracted metrics against them
    # fail the job if any metric is outside the bounds
    if solver.metrics:
        required = [m.name for m in (solver.metrics or []) if m.required]
        ranges = {m.name: (m.min_, m.max_) for m in (solver.metrics or [])}
        valid, errors = validate_metrics(metrics, required=required, ranges=ranges)
        if not valid:
            passed = False
            validation_errors = errors
            logger.warning(
                "runner.metrics_invalid",
                job=job.name,
                errors=errors,
                metrics=metrics,
            )
        else:
            validation_errors = []
    run_result = RunResult(
        job_name=job.name,
        solver_name=solver.name,
        system_name=system.name,
        returncode=result.returncode,
        stdout=result.stdout or "",
        stderr=result.stderr or "",
        runtime_seconds=runtime,
        timestamp=end.isoformat(),
        validation_errors=validation_errors,
        passed=passed,
        raw_logs=raw_logs,
        metrics=metrics,
        processor=processor,
    )

    logger.info(
        "runner.finish",
        job=job.name,
        returncode=result.returncode,
        passed=passed,
        runtime=runtime,
    )
    return run_result


def run_jobs(
    jobs: list[Job],
    solvers: dict[str, Solver],
    systems: dict[str, System],
) -> list[RunResult]:
    """Run multiple jobs and return results."""
    results: list[RunResult] = []
    now = datetime.now(timezone.utc).isoformat()
    for job in jobs:
        solver = solvers.get(job.solver)
        system = systems.get(job.system)
        if not solver:
            msg = f"Solver '{job.solver}' not found for job '{job.name}'"
            logger.warning("runner.skip", job=job.name, reason=msg)
            results.append(
                RunResult(
                    job_name=job.name,
                    solver_name=job.solver,
                    system_name=job.system,
                    returncode=-1,
                    stdout="",
                    stderr=msg,
                    runtime_seconds=0.0,
                    timestamp=now,
                    validation_errors=[],
                    passed=False,
                    metrics={"runtime_seconds": 0.0},
                    processor=probe_processor(),
                )
            )
            continue
        if not system:
            msg = f"System '{job.system}' not found for job '{job.name}'"
            logger.warning("runner.skip", job=job.name, reason=msg)
            results.append(
                RunResult(
                    job_name=job.name,
                    solver_name=job.solver,
                    system_name=job.system,
                    returncode=-1,
                    stdout="",
                    stderr=msg,
                    runtime_seconds=0.0,
                    timestamp=now,
                    validation_errors=[],
                    passed=False,
                    metrics={"runtime_seconds": 0.0},
                    processor=probe_processor(),
                )
            )
            continue
        results.append(run_job(job, solver, system))
    return results
