"""SLURM runtime refinement: HARNESS_SOLVER_WALL_SECONDS from batch stdout, else sacct (Start/End, Elapsed, ElapsedRaw)."""

from __future__ import annotations

import math
import os
import re
import shlex
import subprocess
from datetime import datetime
from typing import Any

import structlog

logger = structlog.get_logger()

_HARNESS_SOLVER_WALL_RE = re.compile(
    r"^HARNESS_SOLVER_WALL_SECONDS=(.+)$",
    re.MULTILINE,
)

_INVALID_TS = frozenset(
    {"", "unknown", "none", "n/a", "invalid", "1970-01-01t00:00:00"},
)


def _parse_elapsed_string(elapsed: str) -> float | None:
    """Parse sacct Elapsed: [days-]HH:MM:SS[.frac] or MM:SS to seconds."""
    elapsed = elapsed.strip()
    if not elapsed or elapsed in ("N/A", "UNKNOWN"):
        return None
    m = re.match(
        r"^((?P<days>\d+)-)?(?P<hms>(\d+:)?\d+:\d+(\.\d+)?)$",
        elapsed,
    )
    if not m:
        return None
    days = int(m.group("days") or 0)
    hms = m.group("hms")
    parts = hms.split(":")
    try:
        if len(parts) == 3:
            h, mn, sec = parts
            return days * 86400 + int(h) * 3600 + int(mn) * 60 + float(sec)
        if len(parts) == 2:
            mn, sec = parts
            return days * 86400 + int(mn) * 60 + float(sec)
    except ValueError:
        return None
    return None


def _parse_slurm_timestamp(s: str) -> datetime | None:
    """Parse sacct Start/End (ISO-like). Returns naive or aware datetime."""
    s = (s or "").strip()
    if not s or s.lower() in _INVALID_TS:
        return None
    if " " in s and "T" not in s.split(" ", 1)[0]:
        s = s.replace(" ", "T", 1)
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def _parse_sacct_start_end_output(stdout: str) -> float | None:
    """Parse sacct -P -o Start,End lines; return max (End - Start) in seconds."""
    best: float | None = None
    for line in (stdout or "").splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 2:
            continue
        start_s, end_s = parts[-2], parts[-1]
        start = _parse_slurm_timestamp(start_s)
        end = _parse_slurm_timestamp(end_s)
        if start is None or end is None:
            continue
        delta = (end - start).total_seconds()
        if delta < 0:
            continue
        if best is None or delta > best:
            best = delta
    return best


def _parse_sacct_elapsedraw_output(stdout: str) -> float | None:
    """Parse sacct -P -o ElapsedRaw lines; return max seconds."""
    best: float | None = None
    for line in (stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        if "|" in line:
            fields = [f.strip() for f in line.split("|")]
            raw = fields[-1]
        else:
            raw = line
        if not raw or raw in ("N/A", "[NOT_SET]"):
            continue
        try:
            val = float(raw)
        except ValueError:
            continue
        if val < 0:
            continue
        if best is None or val > best:
            best = val
    return best


def _best_elapsed_hms_from_output(stdout: str) -> float | None:
    """Parse sacct -P -o Elapsed lines using _parse_elapsed_string."""
    best: float | None = None
    for line in (stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        field = line.split("|")[-1].strip() if "|" in line else line
        parsed = _parse_elapsed_string(field)
        if parsed is None:
            continue
        if best is None or parsed > best:
            best = parsed
    return best


def _run_sacct_in_env(script: str, timeout: int) -> subprocess.CompletedProcess[str]:
    """Run a bash one-liner on host or inside DOCKER_SLURM* container."""
    cont = (
        os.environ.get("DOCKER_SLURM_SUBMIT_CONTAINER", "").strip()
        or os.environ.get("DOCKER_SLURM_CONTAINER", "").strip()
    )
    if cont and cont != "host":
        return subprocess.run(
            ["docker", "exec", cont, "bash", "-lc", script],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    return subprocess.run(
        ["bash", "-lc", script],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _sacct_raw_output(
    cont: str,
    jid_arg: str,
    format_fields: str,
    timeout: int,
) -> str:
    """Run sacct with -o format_fields; return stdout (may be empty)."""
    inner = (
        f"sacct -j {shlex.quote(jid_arg)} -n -X -P -o {format_fields} 2>/dev/null || true"
    )
    if cont and cont != "host":
        p = subprocess.run(
            ["docker", "exec", cont, "bash", "-lc", inner],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    elif cont == "host":
        p = subprocess.run(
            ["bash", "-lc", inner],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    else:
        p = _run_sacct_in_env(inner, timeout)
    return p.stdout or ""


def fetch_slurm_elapsed_seconds(
    job_ids: list[str],
    submit_container: str | None,
    *,
    timeout: int = 120,
) -> float | None:
    """
    Return best-effort Slurm wall time in seconds, or None.

    Preference order (first non-None wins): Start/End delta, Elapsed (HMS),
    ElapsedRaw (integer seconds on many sites).
    """
    if not job_ids:
        return None
    safe_ids = [str(j).strip() for j in job_ids if str(j).strip().isdigit()]
    if not safe_ids:
        return None
    jid_arg = ",".join(safe_ids[:32])
    cont = (submit_container or "").strip()

    out_se = _sacct_raw_output(cont, jid_arg, "Start,End", timeout)
    delta = _parse_sacct_start_end_output(out_se)
    if delta is not None:
        logger.debug("slurm_elapsed.start_end", job_ids=safe_ids, elapsed_seconds=delta)
        return delta

    out_e = _sacct_raw_output(cont, jid_arg, "Elapsed", timeout)
    elapsed = _best_elapsed_hms_from_output(out_e)
    if elapsed is not None:
        logger.debug("slurm_elapsed.elapsed_hms", job_ids=safe_ids, elapsed_seconds=elapsed)
        return elapsed

    out_er = _sacct_raw_output(cont, jid_arg, "ElapsedRaw", timeout)
    raw = _parse_sacct_elapsedraw_output(out_er)
    if raw is not None:
        logger.debug("slurm_elapsed.elapsed_raw", job_ids=safe_ids, elapsed_seconds=raw)
    return raw


def parse_harness_solver_wall_seconds(stdout: str, stderr: str) -> float | None:
    """
    Parse HARNESS_SOLVER_WALL_SECONDS=<float> from combined solver output (local run.sh or
    slurm-%j.out text cat'd into stdout).
    """
    comb = (stdout or "") + "\n" + (stderr or "")
    m = _HARNESS_SOLVER_WALL_RE.search(comb)
    if not m:
        return None
    try:
        val = float(m.group(1).strip())
    except ValueError:
        return None
    if not math.isfinite(val) or val < 0:
        return None
    return val


def refine_run_result_runtime_from_slurm(result: Any) -> None:
    """Prefer HARNESS_SOLVER_WALL_SECONDS (local or Slurm batch stdout); else sacct when Slurm ids exist."""
    out = getattr(result, "stdout", "") or ""
    err = getattr(result, "stderr", "") or ""
    inner = parse_harness_solver_wall_seconds(out, err)
    if inner is not None:
        old = float(getattr(result, "runtime_seconds", 0.0) or 0.0)
        result.runtime_seconds = float(inner)
        metrics = getattr(result, "metrics", None)
        if isinstance(metrics, dict):
            metrics["runtime_seconds"] = float(inner)
        ids_log: list[str] = list(getattr(result, "scheduler_job_ids", None) or [])
        logger.info(
            "slurm_elapsed.refined",
            job_name=getattr(result, "job_name", ""),
            job_ids=ids_log,
            runtime_wall_seconds=old,
            runtime_slurm_seconds=inner,
            source="harness_solver_wall",
        )
        return

    backend = (getattr(result, "scheduler_backend", None) or "").strip().lower()
    ids: list[str] = list(getattr(result, "scheduler_job_ids", None) or [])
    if not ids:
        return
    if backend and backend != "slurm":
        return

    sub = getattr(result, "submit_container", None)
    elapsed = fetch_slurm_elapsed_seconds(ids, sub)
    if elapsed is None:
        logger.debug("slurm_elapsed.skip", reason="sacct_unavailable", job_ids=ids)
        return
    old = float(getattr(result, "runtime_seconds", 0.0) or 0.0)
    result.runtime_seconds = float(elapsed)
    metrics = getattr(result, "metrics", None)
    if isinstance(metrics, dict):
        metrics["runtime_seconds"] = float(elapsed)
    logger.info(
        "slurm_elapsed.refined",
        job_name=getattr(result, "job_name", ""),
        job_ids=ids,
        runtime_wall_seconds=old,
        runtime_slurm_seconds=elapsed,
        source="sacct",
    )
