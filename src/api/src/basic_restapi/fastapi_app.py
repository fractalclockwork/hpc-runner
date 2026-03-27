"""FastAPI REST API for HPC Regression Platform."""

import json
import os
from collections import defaultdict
from typing import Literal

import structlog
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel

from harness import (
    ConfigError,
    load_all,
    run_jobs,
    init_db,
    store_run,
    get_runs,
    get_run_by_id,
    delete_runs,
    get_solver_run_summaries,
    get_metrics_history,
    get_all_metrics_series,
    get_baseline_run,
    set_baseline_run,
    get_baseline_comparison,
    get_config_dir,
    get_db_path,
    get_job_batch_uuids,
)

from . import invocations
from .slurm_tools import query_slurm_job_state

app = FastAPI(title="HPC Regression API", version="0.1.0")
logger = structlog.get_logger()

CONFIG_DIR = get_config_dir()
DB_PATH = get_db_path()


def _normalize_run_row(r: dict) -> None:
    """Decode JSON-ish columns for API responses (mutates dict in place)."""
    if r.get("metrics_json"):
        try:
            r["metrics"] = json.loads(r["metrics_json"])
        except Exception:
            r["metrics"] = {}
    else:
        r["metrics"] = {}
    if r.get("validation_errors") is not None:
        try:
            r["validation_errors"] = json.loads(r["validation_errors"])
        except Exception:
            r["validation_errors"] = []
    else:
        r["validation_errors"] = []
    r["passed"] = bool(r.get("passed"))
    r["is_baseline"] = bool(r.get("is_baseline", False))
    sj = r.get("scheduler_job_ids")
    if isinstance(sj, str):
        try:
            r["scheduler_job_ids"] = json.loads(sj or "[]")
        except Exception:
            r["scheduler_job_ids"] = []
    elif sj is None:
        r["scheduler_job_ids"] = []
    r["scheduler_backend"] = r.get("scheduler_backend") or ""
    r["submit_container"] = r.get("submit_container") or ""


def _load_definitions():
    return load_all(CONFIG_DIR, None)


@app.exception_handler(ConfigError)
def config_error_handler(request, exc: ConfigError):
    return JSONResponse(
        status_code=500,
        content={"error": "Config load failed", "detail": str(exc)},
    )


class RunJobsRequest(BaseModel):
    jobs: list[str] | None = None
    batch_name: str = ""
    background: bool = False
    group_by: Literal["batch", "solver"] = "batch"


class DeleteRunsRequest(BaseModel):
    ids: list[int]


@app.get("/")
def root():
    """Redirect to interactive API docs."""
    return RedirectResponse(url="/docs", status_code=302)


@app.get("/api/health")
@app.get("/health")
def api_health():
    """Health check for Docker/orchestration. Returns 200 when API is ready."""
    return {"status": "ok"}


@app.get("/api/solvers")
def api_solvers():
    """List configured solvers."""
    _, _, solvers, _ = _load_definitions()
    return [

        {
            "name": s.name,
            "version": s.version,
            "allowed_systems": s.allowed_systems,
            "has_parser": s.parser_config is not None,
        }
        for s in solvers.values()
    ]

@app.get("/api/systems")
def api_systems():
    """List configured systems."""
    _, systems, _, _ = _load_definitions()
    return [
        {
            "name": s.name,
            "resources": s.resources,
            "env": s.env,
            "constraints": s.constraints,
            "extra": s.extra,
        }
        for s in systems.values()
    ]

@app.get("/api/jobs")
def api_jobs():
    """List configured jobs."""
    _, _, _, jobs = _load_definitions()
    return [
        {"name": j.name, "solver": j.solver, "system": j.system, "baseline": j.baseline}
        for j in jobs.values()
    ]


@app.post("/api/run_jobs")
def api_run_jobs(body: RunJobsRequest | None = None):
    """Run jobs. Body: jobs, batch_name, background, group_by (batch|solver when background)."""
    _, systems, solvers, jobs = _load_definitions()
    job_names = body.jobs if body and body.jobs else None

    job_list = list(jobs.values())
    if job_names:
        job_list = [j for j in job_list if j.name in job_names]

    if not job_list:
        available = sorted(j.name for j in jobs.values())
        return JSONResponse(
            status_code=400,
            content={
                "error": "No jobs to run",
                "available_jobs": available,
                "results": [],
            },
        )

    batch_name = body.batch_name if body and body.batch_name else ""
    if body and body.background:
        gb = body.group_by if body else "batch"
        if gb == "solver":
            buckets: dict[str, list] = defaultdict(list)
            for j in job_list:
                buckets[j.solver].append(j)
            inv_rows: list[dict] = []
            for solver in sorted(buckets.keys()):
                jl = buckets[solver]
                sub_batch = f"{batch_name}:{solver}" if batch_name.strip() else solver
                inv_id = invocations.start_background_run(
                    jl,
                    solvers,
                    systems,
                    sub_batch,
                    str(DB_PATH),
                    solver_name=solver,
                    job_names=[x.name for x in jl],
                )
                inv_rows.append(
                    {
                        "solver_name": solver,
                        "invocation_id": inv_id,
                        "job_names": [x.name for x in jl],
                    }
                )
            content: dict = {
                "group_by": "solver",
                "status": "queued",
                "invocations": inv_rows,
            }
            if len(inv_rows) == 1:
                content["invocation_id"] = inv_rows[0]["invocation_id"]
            return JSONResponse(status_code=202, content=content)
        inv_id = invocations.start_background_run(
            job_list,
            solvers,
            systems,
            batch_name,
            str(DB_PATH),
            solver_name="",
            job_names=[j.name for j in job_list],
        )
        return JSONResponse(
            status_code=202,
            content={
                "group_by": "batch",
                "status": "queued",
                "invocation_id": inv_id,
                "invocations": [
                    {
                        "solver_name": "",
                        "invocation_id": inv_id,
                        "job_names": [j.name for j in job_list],
                    }
                ],
            },
        )

    results = run_jobs(job_list, solvers, systems, batch_name=batch_name)
    init_db(DB_PATH)
    for r in results:
        store_run(DB_PATH, r)

    response: list[dict] = []
    for r in results:
        item = {
            "job_name": r.job_name,
            "solver_name": r.solver_name,
            "system_name": r.system_name,
            "returncode": r.returncode,
            "passed": r.passed,
            "runtime_seconds": r.runtime_seconds,
            "timestamp": r.timestamp,
            "metrics": r.metrics,
            "processor": r.processor,
            "scheduler_backend": getattr(r, "scheduler_backend", "") or "",
            "scheduler_job_ids": getattr(r, "scheduler_job_ids", None) or [],
            "submit_container": getattr(r, "submit_container", "") or "",
        }
        if hasattr(r, "validation_errors"):
            item["validation_errors"] = r.validation_errors
        item["stdout"] = r.stdout or ""
        item["stderr"] = r.stderr or ""
        response.append(item)
    return response


@app.get("/api/runs")
def api_runs(
    solver: str | None = None,
    processor: str | None = None,
    limit: int = 100,
    offset: int = 0,
):
    """List recent runs, optionally filtered by solver or processor."""
    limit = min(limit, 500)
    init_db(DB_PATH)
    runs = get_runs(DB_PATH, solver=solver, processor=processor, limit=limit, offset=offset)
    for r in runs:
        _normalize_run_row(r)
    return runs


@app.delete("/api/runs")
def api_delete_runs(body: DeleteRunsRequest):
    """Delete stored runs by id. May remove a baseline row (solver then has no baseline)."""
    if not body.ids:
        raise HTTPException(status_code=422, detail="ids must be non-empty")
    init_db(DB_PATH)
    n = delete_runs(DB_PATH, body.ids)
    if n == 0:
        raise HTTPException(status_code=404, detail="No matching run ids")
    return {"deleted": n}


@app.get("/api/runs/{run_id}")
def api_run_detail(run_id: int):
    """Get a single run by id."""
    init_db(DB_PATH)
    run = get_run_by_id(DB_PATH, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    run = dict(run)
    _normalize_run_row(run)
    return run


@app.get("/api/runs/{run_id}/slurm_status")
def api_run_slurm_status(run_id: int):
    """Live squeue/sacct for SLURM job ids on this run (requires RUN_SLURM_E2E + docker/host tools)."""
    init_db(DB_PATH)
    run = get_run_by_id(DB_PATH, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    try:
        jids = json.loads(run.get("scheduler_job_ids") or "[]")
    except json.JSONDecodeError:
        jids = []
    if not jids:
        return {"enabled": True, "job_ids": [], "output": "", "message": "No SLURM job ids recorded for this run"}
    cont = (run.get("submit_container") or "").strip() or None
    return query_slurm_job_state([str(j) for j in jids], cont)


@app.get("/api/invocations")
def api_list_invocations(active_only: bool = False):
    """List background run_jobs invocations (optionally only queued/running)."""
    return invocations.list_invocations(active_only=active_only)


@app.get("/api/invocations/{invocation_id}/slurm_status")
def api_invocation_slurm_status(invocation_id: str):
    """Live squeue/sacct for SLURM job ids observed on this invocation (while running or after)."""
    body = invocations.get_invocation_slurm_status(invocation_id)
    if body is None:
        raise HTTPException(status_code=404, detail="Invocation not found")
    return body


@app.get("/api/invocations/{invocation_id}")
def api_get_invocation(invocation_id: str):
    """Status / results for a background run_jobs invocation."""
    rec = invocations.get_invocation(invocation_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Invocation not found")
    return invocations.invocation_to_dict(rec)


@app.post("/api/invocations/{invocation_id}/cancel")
def api_cancel_invocation(invocation_id: str):
    """Cancel background run: scancel (if known SLURM ids) + terminate local subprocess."""
    ok, code, notes = invocations.cancel_invocation(invocation_id)
    if not ok and code == "not_found":
        raise HTTPException(status_code=404, detail="Invocation not found")
    if not ok:
        return JSONResponse(status_code=400, content={"ok": False, "detail": code, "scancel_notes": notes})
    return {"ok": True, "scancel_notes": notes}


@app.get("/api/solver_summaries")
def api_solver_summaries():
    """Per-solver aggregate stats from stored runs (monitoring)."""
    init_db(DB_PATH)
    return get_solver_run_summaries(DB_PATH)


@app.get("/api/baseline_comparison")
def api_baseline_comparison(solver: str | None = None, limit: int = 50):
    """
    Compare all other runs to the baseline run per solver.
    Returns for each solver: baseline_run, other runs, and per-metric deltas (vs_baseline).
    """
    limit = min(limit, 200)
    init_db(DB_PATH)
    return get_baseline_comparison(DB_PATH, solver_name=solver, limit_per_solver=limit)


@app.get("/api/solvers/{solver_name}/baseline")
def api_solver_baseline(solver_name: str):
    """Return the current baseline run for the given solver, or 404."""
    init_db(DB_PATH)
    run = get_baseline_run(DB_PATH, solver_name)
    if not run:
        raise HTTPException(status_code=404, detail=f"No baseline run for solver '{solver_name}'")
    return run


@app.post("/api/runs/{run_id}/set_baseline")
def api_set_baseline(run_id: int):
    """
    Set a specific run as the baseline for its solver.
    Other runs of the same solver are no longer baseline. Returns the updated run.
    """
    init_db(DB_PATH)
    run = set_baseline_run(DB_PATH, run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return run


@app.get("/api/metrics/{solver_name}/{metric_name}")
def api_metrics_history(
    solver_name: str,
    metric_name: str,
    limit: int = 100,
):
    """Get metric history for trend visualization."""
    limit = min(limit, 500)
    init_db(DB_PATH)
    history: list[tuple[str, str]] = get_metrics_history(DB_PATH, solver_name, metric_name, limit=limit)
    return [{"timestamp": ts, "value": v} for ts, v in history]

@app.get("/api/available_metrics")
def api_available_metrics(
    limit: int = 100,
):
    """Get a list of all metrics/solver combos. by default limits the output to 100"""
    limit = min(limit, 500)
    init_db(DB_PATH)
    available_metrics: list[tuple[str, str]] = get_all_metrics_series(DB_PATH)
    return [{"solver": s, "metric": m} for s, m in available_metrics]

@app.get("/api/get_job_batch_uuids")
def api_job_batch_uuids(limit: int = 100):
    """
    Gets a list of
    """
    init_db(DB_PATH)
    return get_job_batch_uuids(DB_PATH, limit=limit)

def main():
    import uvicorn
    uvicorn.run(
        "basic_restapi.fastapi_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
