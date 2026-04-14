# runner.py - Execution-agnostic job runner
from __future__ import annotations

import os
import platform
import re
import subprocess
import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import structlog

from .config import Job, Resource, Solver, System
from .parser import extract_metrics, validate_metrics
from .slurm_elapsed import refine_run_result_runtime_from_slurm

logger = structlog.get_logger()

# Bounded buffer for background-run live stdout (API + UI poll); avoids unbounded memory.
_LIVE_LOG_DEQUE_MAXLEN = 8000


def _live_log_deque_factory() -> deque[str]:
    return deque(maxlen=_LIVE_LOG_DEQUE_MAXLEN)


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
    baseline: bool = False
    job_batch_uuid: str = "" # "" means no batch id is found for the run. don't use null here so we can index, also because "" is guaranteed to not be a valid uuid
    job_batch_date: str | None = None # This could actually be annoying in the future, but jobs don't have to have a batch date since they might not be run as a batch
    job_batch_name: str = ""
    scheduler_backend: str = ""
    scheduler_job_ids: list[str] = field(default_factory=list)
    submit_container: str = ""


@dataclass
class InvocationControl:
    """Used for background runs: cooperative cancel, SLURM job id capture, and live stdout tail."""

    cancel_event: threading.Event = field(default_factory=threading.Event)
    current_proc: subprocess.Popen | None = None
    slurm_job_ids: list[str] = field(default_factory=list)
    submit_container: str | None = None
    jobs_total: int = 0
    jobs_completed: int = 0
    _live_log_lines: deque[str] = field(default_factory=_live_log_deque_factory)
    _live_log_lock: threading.Lock = field(default_factory=threading.Lock)

    def append_live_log_line(self, line: str) -> None:
        with self._live_log_lock:
            self._live_log_lines.append(line)

    def snapshot_live_stdout(self, *, max_chars: int = 512_000) -> str:
        """Thread-safe join of captured lines; tail-truncates if over max_chars (for JSON responses)."""
        with self._live_log_lock:
            text = "".join(self._live_log_lines)
        if len(text) <= max_chars:
            return text
        return "[…truncated, showing last portion]\n" + text[-max_chars:]

    def clear_live_stdout(self) -> None:
        with self._live_log_lock:
            self._live_log_lines.clear()


def _parse_scheduler_metadata(text: str) -> tuple[str, list[str], str]:
    """Parse HARNESS_* lines from solver stdout/stderr (see lammps-slurm run.sh)."""
    backend = ""
    job_ids: list[str] = []
    submit_c = ""
    for line in text.splitlines():
        s = line.strip()
        if m := re.match(r"HARNESS_SCHEDULER_BACKEND=(.+)", s):
            backend = m.group(1).strip()
        elif m := re.match(r"HARNESS_SLURM_JOB_ID=(\d+)", s):
            jid = m.group(1)
            if jid not in job_ids:
                job_ids.append(jid)
        elif m := re.match(r"HARNESS_SUBMIT_CONTAINER=(.+)", s):
            submit_c = m.group(1).strip()
    return backend, job_ids, submit_c


def _merge_scheduler_into_result(
    res: RunResult,
    stdout: str,
    stderr: str,
    invoke: InvocationControl | None,
) -> None:
    comb = (stdout or "") + "\n" + (stderr or "")
    back, ids, sub = _parse_scheduler_metadata(comb)
    if invoke and invoke.slurm_job_ids:
        ids = list(dict.fromkeys(invoke.slurm_job_ids + ids))
    if invoke and invoke.submit_container:
        sub = invoke.submit_container.strip() or sub
    if not back and ids:
        back = "slurm"
    res.scheduler_backend = back
    res.scheduler_job_ids = ids
    res.submit_container = sub or ""


def _run_subprocess_for_job(
    cmd: list[str],
    cwd: str,
    env: dict[str, str],
    timeout_sec: int,
    capture_output: bool,
    invoke_ctl: InvocationControl | None,
) -> subprocess.CompletedProcess[str]:
    """subprocess.run, or Popen + cancel/stream path when invoke_ctl is set."""
    if invoke_ctl is None:
        return subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            capture_output=capture_output,
            text=True,
            timeout=timeout_sec,
        )
    if not capture_output:
        raise ValueError("invoke_ctl requires capture_output=True")
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    invoke_ctl.current_proc = proc
    chunks: list[str] = []

    def reader() -> None:
        assert proc.stdout is not None
        try:
            for line in proc.stdout:
                chunks.append(line)
                invoke_ctl.append_live_log_line(line)
                if m := re.search(r"HARNESS_SLURM_JOB_ID=(\d+)", line):
                    jid = m.group(1)
                    if jid not in invoke_ctl.slurm_job_ids:
                        invoke_ctl.slurm_job_ids.append(jid)
                if m2 := re.search(r"HARNESS_SUBMIT_CONTAINER=(.+)", line.rstrip()):
                    invoke_ctl.submit_container = m2.group(1).strip()
        except Exception:
            pass

    rt = threading.Thread(target=reader, daemon=True)
    rt.start()
    t0 = time.monotonic()
    timed_out = False
    while proc.poll() is None:
        if invoke_ctl.cancel_event.is_set():
            proc.terminate()
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                proc.kill()
            break
        if time.monotonic() - t0 > timeout_sec:
            timed_out = True
            proc.kill()
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                pass
            break
        time.sleep(0.25)
    rt.join(timeout=60)
    out = "".join(chunks)
    rc = proc.returncode if proc.returncode is not None else -1
    if timed_out:
        raise subprocess.TimeoutExpired(cmd, timeout_sec, output=out, stderr=None)
    return subprocess.CompletedProcess(cmd, rc, out, "")


def _build_env(
    system: System,
    solver: Solver,
    resources: dict[str, Resource] | None,
    base_env: dict[str, str] | None = None,
) -> dict[str, str]:
    """Merge env for the solver process: os.environ, then each resource, solver, system (later wins)."""
    env = dict(os.environ)
    if base_env:
        env.update(base_env)
    res_map = resources or {}
    for rname in system.resources:
        r = res_map.get(rname)
        if r is not None:
            env.update(r.env)
    env.update(solver.env)
    env.update(system.env)
    return env


def run_job(
    job: Job,
    solver: Solver,
    system: System,
    *,
    resources: dict[str, Resource] | None = None,
    capture_output: bool = True,
    job_batch_uuid: str = "",
    job_batch_date: str | None = None,
    job_batch_name: str = "",
    invoke_ctl: InvocationControl | None = None,
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
    env = _build_env(system, solver, resources)

    cmd: list[str] = []
    if entrypoint_path.suffix == ".py":
        cmd = ["python3", str(entrypoint_path)]
    elif entrypoint_path.suffix == ".sh":
        cmd = ["bash", str(entrypoint_path)]
    else:
        cmd = [str(entrypoint_path)]

    timeout_sec = job.timeout_seconds if job.timeout_seconds is not None else 3600

    try:
        result = _run_subprocess_for_job(
            cmd,
            str(cwd),
            env,
            timeout_sec,
            capture_output,
            invoke_ctl,
        )
    except subprocess.TimeoutExpired as e:
        end = datetime.now(timezone.utc)
        runtime = (end - start).total_seconds()
        timeout_msg = f"Job timed out after {timeout_sec}s"
        tout = (e.output or "") if getattr(e, "output", None) else ""
        run_result = RunResult(
            job_name=job.name,
            solver_name=solver.name,
            system_name=system.name,
            returncode=-1,
            stdout=tout if capture_output else "",
            stderr=timeout_msg,
            runtime_seconds=runtime,
            timestamp=end.isoformat(),
            validation_errors=[],
            passed=False,
            metrics={"runtime_seconds": runtime},
            processor=processor,
            baseline=job.baseline,
            job_batch_uuid=job_batch_uuid,
            job_batch_date=job_batch_date,
            job_batch_name=job_batch_name,
        )
        _merge_scheduler_into_result(run_result, run_result.stdout, run_result.stderr, invoke_ctl)
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
            baseline=job.baseline,
            job_batch_uuid=job_batch_uuid,
            job_batch_date=job_batch_date,
            job_batch_name=job_batch_name,
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
        baseline=job.baseline,
        job_batch_uuid=job_batch_uuid,
        job_batch_date=job_batch_date,
        job_batch_name=job_batch_name,
    )
    _merge_scheduler_into_result(run_result, run_result.stdout, run_result.stderr, invoke_ctl)
    refine_run_result_runtime_from_slurm(run_result)
    if solver.metrics:
        required = [m.name for m in (solver.metrics or []) if m.required]
        ranges = {m.name: (m.min_, m.max_) for m in (solver.metrics or [])}
        valid, errors = validate_metrics(run_result.metrics, required=required, ranges=ranges)
        if not valid:
            run_result.passed = False
            run_result.validation_errors = errors
        else:
            run_result.validation_errors = []
            expected_rc = (job.success_criteria or {}).get("returncode", 0)
            run_result.passed = result.returncode == expected_rc
    if invoke_ctl and invoke_ctl.cancel_event.is_set():
        run_result.passed = False
        if not run_result.validation_errors:
            run_result.validation_errors = ["Cancelled by user"]

    logger.info(
        "runner.finish",
        job=job.name,
        returncode=result.returncode,
        passed=run_result.passed,
        runtime=run_result.runtime_seconds,
    )
    return run_result


def run_jobs(
    jobs: list[Job],
    solvers: dict[str, Solver],
    systems: dict[str, System],
    resources: dict[str, Resource] | None = None,
    batch_name: str = "",
    invoke_ctl: InvocationControl | None = None,
) -> list[RunResult]:
    """Run multiple jobs and return results."""
    results: list[RunResult] = []
    now = datetime.now(timezone.utc).isoformat()
    batch_uuid = uuid.uuid4().hex
    if invoke_ctl is not None:
        invoke_ctl.jobs_total = len(jobs)
        invoke_ctl.jobs_completed = 0
    for job in jobs:
        try:
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
                        baseline=job.baseline,
                        job_batch_uuid=batch_uuid,
                        job_batch_date=now,
                        job_batch_name=batch_name,
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
                        baseline=job.baseline,
                        job_batch_uuid=batch_uuid,
                        job_batch_date=now,
                        job_batch_name=batch_name,
                    )
                )
                continue
            if invoke_ctl and invoke_ctl.cancel_event.is_set():
                ts = datetime.now(timezone.utc).isoformat()
                logger.info("runner.skip", job=job.name, reason="cancelled_before_start")
                results.append(
                    RunResult(
                        job_name=job.name,
                        solver_name=solver.name,
                        system_name=system.name,
                        returncode=-1,
                        stdout="",
                        stderr="",
                        runtime_seconds=0.0,
                        timestamp=ts,
                        validation_errors=["Cancelled by user"],
                        passed=False,
                        metrics={"runtime_seconds": 0.0},
                        processor=probe_processor(),
                        baseline=job.baseline,
                        job_batch_uuid=batch_uuid,
                        job_batch_date=now,
                        job_batch_name=batch_name,
                    )
                )
                continue
            if invoke_ctl is not None:
                invoke_ctl.append_live_log_line(f"\n=== {job.name} ({solver.name}@{system.name}) ===\n")
            results.append(
                run_job(
                    job,
                    solver,
                    system,
                    resources=resources,
                    job_batch_uuid=batch_uuid,
                    job_batch_date=now,
                    job_batch_name=batch_name,
                    invoke_ctl=invoke_ctl,
                )
            )
        finally:
            if invoke_ctl is not None:
                invoke_ctl.jobs_completed += 1
    return results
