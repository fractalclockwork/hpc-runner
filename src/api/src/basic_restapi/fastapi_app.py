"""FastAPI REST API for HPC Regression Testing Platform."""

from pathlib import Path

import structlog
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
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
)

BASE_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BASE_DIR.parent.parent

app = FastAPI(title="HPC Regression Testing API", version="0.1.0")
logger = structlog.get_logger()

CONFIG_DIR = PROJECT_ROOT / "configs"
SOLVERS_DIR = PROJECT_ROOT / "solvers"
DB_PATH = PROJECT_ROOT / "data" / "harness.db"


def _load_definitions():
    return load_all(CONFIG_DIR, SOLVERS_DIR)


@app.exception_handler(ConfigError)
def config_error_handler(request, exc: ConfigError):
    return JSONResponse(
        status_code=500,
        content={"error": "Config load failed", "detail": str(exc)},
    )


class RunJobsRequest(BaseModel):
    jobs: list[str] | None = None


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


@app.get("/api/jobs")
def api_jobs():
    """List configured jobs."""
    _, _, _, jobs = _load_definitions()
    return [
        {"name": j.name, "solver": j.solver, "system": j.system}
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

    return [
        {
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
        for r in results
    ]


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
            import json
            try:
                r["metrics"] = json.loads(r["metrics_json"])
            except Exception:
                r["metrics"] = {}
        r["passed"] = bool(r.get("passed"))
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
        import json
        try:
            run["metrics"] = json.loads(run["metrics_json"])
        except Exception:
            run["metrics"] = {}
    run["passed"] = bool(run.get("passed"))
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
    history = get_metrics_history(DB_PATH, solver_name, metric_name, limit=limit)
    return [{"timestamp": ts, "value": v} for ts, v in history]


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
