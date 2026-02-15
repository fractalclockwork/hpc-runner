"""REST API and Dashboard for HPC Regression Testing Platform."""
from pathlib import Path

import structlog
from flask import Flask, jsonify, render_template, request

from hpc_regression import (
    load_all,
    run_tests,
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
DB_PATH = PROJECT_ROOT / "hpc_regression.db"


def _load_definitions():
    resources, systems, solvers, tests = load_all(CONFIG_DIR, SOLVERS_DIR)
    return resources, systems, solvers, tests


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


@app.route("/api/tests")
def api_tests():
    """List configured tests."""
    _, _, solvers, tests = _load_definitions()
    return jsonify([
        {
            "name": t.name,
            "solver": t.solver,
            "system": t.system,
        }
        for t in tests.values()
    ])


@app.route("/api/run_tests", methods=["GET", "POST"])
def api_run_tests():
    """Run tests. POST with optional JSON body: { "tests": ["test1", "test2"] }."""
    resources, systems, solvers, tests = _load_definitions()
    test_names = None
    if request.method == "POST" and request.is_json:
        body = request.get_json() or {}
        test_names = body.get("tests")

    test_list = list(tests.values())
    if test_names:
        test_list = [t for t in test_list if t.name in test_names]

    if not test_list:
        return jsonify({"error": "No tests to run", "results": []}), 400

    results = run_tests(test_list, solvers, systems)

    # Store in DB
    init_db(DB_PATH)
    for r in results:
        store_run(DB_PATH, r)

    return jsonify([
        {
            "test_name": r.test_name,
            "solver_name": r.solver_name,
            "system_name": r.system_name,
            "returncode": r.returncode,
            "passed": r.passed,
            "runtime_seconds": r.runtime_seconds,
            "timestamp": r.timestamp,
            "metrics": r.metrics,
        }
        for r in results
    ])


@app.route("/api/runs")
def api_runs():
    """List recent runs, optionally filtered by solver."""
    solver = request.args.get("solver")
    limit = min(int(request.args.get("limit", 100)), 500)
    offset = int(request.args.get("offset", 0))
    init_db(DB_PATH)
    runs = get_runs(DB_PATH, solver=solver, limit=limit, offset=offset)
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
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()
