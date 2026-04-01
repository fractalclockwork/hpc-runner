# add_solver.py - Create solver and job from a shell command
from __future__ import annotations

import re
import yaml
from pathlib import Path


def derive_name(cmd: str) -> str:
    """Derive a valid solver name from a command string.

    Examples:
        'cat /proc/cpuinfo' -> 'cpuinfo'
        'echo hello' -> 'echo-hello'
    """
    # Take last path component if path-like, else join tokens with hyphen
    parts = cmd.strip().split()
    if not parts:
        return "cmd"
    last = parts[-1]
    # If last part looks like a path, use its stem
    if "/" in last:
        name = Path(last).name
    else:
        name = last
    # Sanitize: alphanumeric and hyphen only
    name = re.sub(r"[^a-zA-Z0-9_-]", "-", name)
    name = re.sub(r"-+", "-", name).strip("-")
    if len(parts) > 1 and "/" not in last:
        # Multiple tokens: use first and last
        first = re.sub(r"[^a-zA-Z0-9_-]", "-", parts[0])[:16]
        name = f"{first}-{name}" if first != name else name
    return name or "cmd"


def add_solver(
    config_dir: Path,
    solvers_dir: Path,
    cmd: str,
    system: str,
    name: str | None = None,
) -> str:
    """Create a minimal solver that runs the given command. Returns solver_name."""
    solver_name = name or derive_name(cmd)

    solver_dir = solvers_dir / solver_name
    if solver_dir.exists():
        raise ValueError(
            f"Solver '{solver_name}' already exists at {solver_dir}. "
            "Use --name to specify a different name."
        )

    solver_dir.mkdir(parents=True, exist_ok=True)

    # solver.yaml
    solver_yaml = {
        "name": solver_name,
        "version": "0.0.0",
        "entrypoint": "run.sh",
        "allowed_systems": [system],
        "default_system": system,
        "metrics": [
            {"name": "runtime_seconds", "unit": "s", "required": False},
        ],
        "log_names": [],
    }
    (solver_dir / "solver.yaml").write_text(
        yaml.safe_dump(solver_yaml, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )

    # run.sh
    run_sh = f"""#!/usr/bin/env bash
set -e
{cmd}
"""
    (solver_dir / "run.sh").write_text(run_sh, encoding="utf-8")
    (solver_dir / "run.sh").chmod(0o755)

    return solver_name


def add_job(
    config_dir: Path,
    solver_name: str,
    system: str,
    job_name: str,
) -> None:
    """Append a job to config_dir/jobs/added.yaml."""
    jobs_dir = config_dir / "jobs"
    jobs_dir.mkdir(parents=True, exist_ok=True)
    jobs_file = jobs_dir / "added.yaml"

    new_job = {
        "name": job_name,
        "solver": solver_name,
        "system": system,
        "parameters": {},
        "success_criteria": {"returncode": 0},
    }

    if jobs_file.exists():
        data = yaml.safe_load(jobs_file.read_text(encoding="utf-8")) or {}
        jobs_list = data.get("jobs", [])
        if any(j.get("name") == job_name for j in jobs_list):
            raise ValueError(
                f"Job '{job_name}' already exists in {jobs_file}. "
                "Use --name to specify a different name."
            )
        jobs_list.append(new_job)
        data["jobs"] = jobs_list
    else:
        data = {"jobs": [new_job]}

    jobs_file.write_text(
        yaml.safe_dump(data, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )
