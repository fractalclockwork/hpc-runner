# tests/test_storage.py - SQLite storage
import tempfile
from pathlib import Path

import pytest

from hpc_regression import RunResult
from hpc_regression.storage import init_db, store_run, get_runs, get_run_by_id, get_metrics_history


def _make_result(test_name="t1", solver_name="s1", metrics=None):
    return RunResult(
        test_name=test_name,
        solver_name=solver_name,
        system_name="dev",
        returncode=0,
        stdout="out",
        stderr="err",
        runtime_seconds=1.5,
        timestamp="2026-02-14T12:00:00+00:00",
        passed=True,
        metrics=metrics or {},
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
    store_run(db_path, _make_result(test_name="t1", solver_name="solver-a"))
    store_run(db_path, _make_result(test_name="t2", solver_name="solver-a"))
    store_run(db_path, _make_result(test_name="t3", solver_name="solver-b"))

    runs = get_runs(db_path)
    assert len(runs) == 3

    runs_a = get_runs(db_path, solver="solver-a")
    assert len(runs_a) == 2
    assert all(r["solver_name"] == "solver-a" for r in runs_a)


def test_get_run_by_id(tmp_path):
    """Retrieve single run by id."""
    db_path = tmp_path / "test.db"
    init_db(db_path)
    row_id = store_run(db_path, _make_result(test_name="my-test"))
    run = get_run_by_id(db_path, row_id)
    assert run is not None
    assert run["test_name"] == "my-test"
    assert run["passed"] == 1

    assert get_run_by_id(db_path, 99999) is None


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
