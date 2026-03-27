"""Shared SLURM squeue/sacct helpers for run rows and live invocations."""

from __future__ import annotations

import os
import subprocess

_QUERY_SCRIPT_TEMPLATE = (
    "squeue -j {jids} 2>/dev/null || true; echo '---'; "
    "sacct -j {jids} -n -X -o JobID,State,ExitCode 2>/dev/null || true"
)


def slurm_status_query_enabled() -> bool:
    """True when RUN_SLURM_E2E=1 (same gate as persisted-run slurm status)."""
    return os.environ.get("RUN_SLURM_E2E") == "1"


def query_slurm_job_state(
    job_ids: list[str],
    submit_container: str | None,
) -> dict:
    """
    Return squeue/sacct output for job_ids.

    When not enabled or missing ids/container, returns a structured message
    without shelling out.
    """
    if not slurm_status_query_enabled():
        return {
            "enabled": False,
            "message": "Set RUN_SLURM_E2E=1 and SLURM tooling to query job state",
        }
    if not job_ids:
        return {"enabled": True, "job_ids": [], "output": "", "message": "No SLURM job ids"}
    cont = (submit_container or "").strip() or os.environ.get("DOCKER_SLURM_SUBMIT_CONTAINER") or os.environ.get(
        "DOCKER_SLURM_CONTAINER", ""
    )
    jid_csv = ",".join(str(j) for j in job_ids)
    script = _QUERY_SCRIPT_TEMPLATE.format(jids=jid_csv)
    if cont == "host":
        p = subprocess.run(
            ["bash", "-lc", script],
            capture_output=True,
            text=True,
            timeout=60,
        )
    elif cont:
        p = subprocess.run(
            ["docker", "exec", cont, "bash", "-lc", script],
            capture_output=True,
            text=True,
            timeout=120,
        )
    else:
        return {
            "enabled": True,
            "job_ids": job_ids,
            "output": "",
            "message": "No submit_container hint and DOCKER_SLURM_CONTAINER unset",
        }
    return {
        "enabled": True,
        "job_ids": job_ids,
        "submit_container": cont or None,
        "output": (p.stdout or "") + (p.stderr or ""),
    }
