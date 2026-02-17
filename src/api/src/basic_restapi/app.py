"""REST API and Dashboard for HPC Regression Testing Platform."""
from pathlib import Path

import structlog
from flask import Flask, jsonify, render_template, request

from harness import (
    load_all,
    run_jobs,
    init_db,
    store_run,
    get_runs,
    get_run_by_id,
    get_metrics_history,
)

BASE_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BASE_DIR.parent.parent  # DOW-1-26/

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)

logger = structlog.get_logger()

CONFIG_DIR = PROJECT_ROOT / "configs"
SOLVERS_DIR = PROJECT_ROOT / "solvers"
DB_PATH = PROJECT_ROOT / "data" / "harness.db"


def _load_definitions():
    resources, systems, solvers, jobs = load_all(CONFIG_DIR, SOLVERS_DIR)
    return resources, systems, solvers, jobs


@app.route("/")
def root():
    return render_template("index.html")


@app.route("/api/solvers")
def api_solvers():
    """List configured solvers."""
    _, _, solvers, _ = _load_definitions()
    return jsonify([
        {
            "name": s.name,
            "version": s.version,
            "allowed_systems": s.allowed_systems,
            "has_parser": s.parser_config is not None,
        }
        for s in solvers.values()
    ])


@app.route("/api/jobs")
def api_jobs():
    """List configured jobs."""
    _, _, solvers, jobs = _load_definitions()
    return jsonify([
        {
            "name": j.name,
            "solver": j.solver,
            "system": j.system,
        }
        for j in jobs.values()
    ])


@app.route("/api/run_jobs", methods=["GET", "POST"])
def api_run_jobs():
    """Run jobs. POST with optional JSON body: { "jobs": ["job1", "job2"] }."""
    resources, systems, solvers, jobs = _load_definitions()
    job_names = None
    if request.method == "POST" and request.is_json:
        body = request.get_json() or {}
        job_names = body.get("jobs")

    job_list = list(jobs.values())
    if job_names:
        job_list = [j for j in job_list if j.name in job_names]

    if not job_list:
        return jsonify({"error": "No jobs to run", "results": []}), 400

    results = run_jobs(job_list, solvers, systems)

    # Store in DB
    init_db(DB_PATH)
    for r in results:
        store_run(DB_PATH, r)

    return jsonify([
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
    ])


@app.route("/api/runs")
def api_runs():
    """List recent runs, optionally filtered by solver or processor."""
    solver = request.args.get("solver")
    processor = request.args.get("processor")
    limit = min(int(request.args.get("limit", 100)), 500)
    offset = int(request.args.get("offset", 0))
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
    return jsonify(runs)


@app.route("/api/runs/<int:run_id>")
def api_run_detail(run_id):
    """Get a single run by id."""
    init_db(DB_PATH)
    run = get_run_by_id(DB_PATH, run_id)
    if not run:
        return jsonify({"error": "Run not found"}), 404
    run = dict(run)
    if run.get("metrics_json"):
        import json
        try:
            run["metrics"] = json.loads(run["metrics_json"])
        except Exception:
            run["metrics"] = {}
    run["passed"] = bool(run.get("passed"))
    return jsonify(run)


@app.route("/api/metrics/<solver_name>/<metric_name>")
def api_metrics_history(solver_name, metric_name):
    """Get metric history for trend visualization."""
    limit = min(int(request.args.get("limit", 100)), 500)
    init_db(DB_PATH)
    history = get_metrics_history(DB_PATH, solver_name, metric_name, limit=limit)
    return jsonify([{"timestamp": ts, "value": v} for ts, v in history])


def main():
    app.run(host="0.0.0.0", port=8000, debug=True)


if __name__ == "__main__":
    main()
