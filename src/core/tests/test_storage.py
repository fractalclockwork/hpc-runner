# tests/test_storage.py - SQLite storage

import json

from harness import RunResult
from harness.storage import (
    init_db,
    store_run,
    get_runs,
    get_run_by_id,
    get_all_metrics_series,
    get_metrics_history,
)


def _make_result(
    job_name="t1",
    solver_name="s1",
    metrics=None,
    processor="x86_64",
    validation_errors=None,
):
    return RunResult(
        job_name=job_name,
        solver_name=solver_name,
        system_name="dev",
        returncode=0,
        stdout="out",
        stderr="err",
        runtime_seconds=1.5,
        timestamp="2026-02-14T12:00:00+00:00",
        validation_errors=validation_errors if validation_errors is not None else [],
        passed=True,
        metrics=metrics or {},
        processor=processor,
    )


def test_init_db_and_store_run(tmp_path):
    """Initialize DB and store a run."""
    db_path = tmp_path / "test.db"
    init_db(db_path)
    result = _make_result(metrics={"mlups": 1.5e6})
    row_id = store_run(db_path, result)
    assert row_id > 0


def test_get_runs(tmp_path):
    """Retrieve runs with optional solver filter."""
    db_path = tmp_path / "test.db"
    init_db(db_path)
    store_run(db_path, _make_result(job_name="t1", solver_name="solver-a"))
    store_run(db_path, _make_result(job_name="t2", solver_name="solver-a"))
    store_run(db_path, _make_result(job_name="t3", solver_name="solver-b"))

    runs = get_runs(db_path)
    assert len(runs) == 3

    runs_a = get_runs(db_path, solver="solver-a")
    assert len(runs_a) == 2
    assert all(r["solver_name"] == "solver-a" for r in runs_a)


def test_get_runs_filter_by_processor(tmp_path):
    """Retrieve runs filtered by processor."""
    db_path = tmp_path / "test.db"
    init_db(db_path)
    store_run(db_path, _make_result(job_name="t1", solver_name="s1", processor="x86_64"))
    store_run(db_path, _make_result(job_name="t2", solver_name="s1", processor="x86_64"))
    store_run(db_path, _make_result(job_name="t3", solver_name="s1", processor="aarch64"))

    runs_x86 = get_runs(db_path, processor="x86_64")
    assert len(runs_x86) == 2
    assert all(r["processor"] == "x86_64" for r in runs_x86)

    runs_arm = get_runs(db_path, processor="aarch64")
    assert len(runs_arm) == 1
    assert runs_arm[0]["processor"] == "aarch64"


def test_get_run_by_id(tmp_path):
    """Retrieve single run by id."""
    db_path = tmp_path / "test.db"
    init_db(db_path)
    row_id = store_run(db_path, _make_result(job_name="my-test", processor="x86_64"))
    run = get_run_by_id(db_path, row_id)
    assert run is not None
    assert run["job_name"] == "my-test"
    assert run["passed"] == 1
    assert run["processor"] == "x86_64"

    assert get_run_by_id(db_path, 99999) is None


def test_validation_errors_stored_and_retrieved(tmp_path):
    """Store a run with validation_errors and assert they round-trip correctly."""
    db_path = tmp_path / "test.db"
    init_db(db_path)
    errors = ["output mismatch on line 42", "max residual exceeded"]
    result = _make_result(
        job_name="val-test",
        validation_errors=errors,
    )
    row_id = store_run(db_path, result)
    run = get_run_by_id(db_path, row_id)
    assert run is not None
    assert run.get("validation_errors") is not None
    stored_errors = json.loads(run["validation_errors"])
    assert stored_errors == errors


def test_get_all_metrics_series(tmp_path):
    """Discover all (solver, metric) pairs with data."""
    db_path = tmp_path / "test.db"
    init_db(db_path)
    store_run(db_path, _make_result(solver_name="s1", metrics={"mlups": 1.0, "runtime": 0.5}))
    store_run(db_path, _make_result(solver_name="s1", metrics={"mlups": 2.0}))
    store_run(db_path, _make_result(solver_name="s2", metrics={"throughput": 100}))

    series = get_all_metrics_series(db_path)
    assert ("s1", "mlups") in series
    assert ("s1", "runtime") in series
    assert ("s2", "throughput") in series
    assert len(series) == 3


def test_get_metrics_history(tmp_path):
    """Retrieve metric history for trend visualization."""
    db_path = tmp_path / "test.db"
    init_db(db_path)
    store_run(db_path, _make_result(solver_name="s1", metrics={"mlups": 1.0}))
    store_run(db_path, _make_result(solver_name="s1", metrics={"mlups": 2.0}))
    store_run(db_path, _make_result(solver_name="s1", metrics={}))

    history = get_metrics_history(db_path, "s1", "mlups")
    assert len(history) == 2
    values = [v for _, v in history]
    assert 1.0 in values
    assert 2.0 in values
