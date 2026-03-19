"""FastAPI REST API for HPC Regression Platform."""

import json

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
    get_metrics_history,
    get_all_metrics_series,
    get_baseline_run,
    set_baseline_run,
    get_baseline_comparison,
    get_config_dir,
    get_db_path,
)

app = FastAPI(title="HPC Regression API", version="0.1.0")
logger = structlog.get_logger()

CONFIG_DIR = get_config_dir()
DB_PATH = get_db_path()


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
    """List configured solvers."""
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
    """Run jobs. Optional body: { "jobs": ["job1", "job2"] }."""
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

    results = run_jobs(job_list, solvers, systems)
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
        }
        if hasattr(r, "validation_errors"):
            item["validation_errors"] = r.validation_errors
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
        if r.get("metrics_json"):
            try:
                r["metrics"] = json.loads(r["metrics_json"])
            except Exception:
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
    return runs


@app.get("/api/runs/{run_id}")
def api_run_detail(run_id: int):
    """Get a single run by id."""
    init_db(DB_PATH)
    run = get_run_by_id(DB_PATH, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    run = dict(run)
    if run.get("metrics_json"):
        try:
            run["metrics"] = json.loads(run["metrics_json"])
        except Exception:
            run["metrics"] = {}
    if run.get("validation_errors") is not None:
        try:
            run["validation_errors"] = json.loads(run["validation_errors"])
        except Exception:
            run["validation_errors"] = []
    else:
        run["validation_errors"] = []
    run["passed"] = bool(run.get("passed"))
    run["is_baseline"] = bool(run.get("is_baseline", False))
    return run


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
