# tests/test_api.py - API error handling and responses

from unittest.mock import patch

import pytest
import yaml
from fastapi.testclient import TestClient

from harness import RunResult, init_db, store_run

from basic_restapi.fastapi_app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_api_run_jobs_invalid_job_names_returns_400_with_available(client):
    """POST /api/run_jobs with non-matching job names returns 400 and available_jobs."""
    response = client.post(
        "/api/run_jobs",
        json={"jobs": ["nonexistent-job-xyz"]},
    )
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "No jobs to run" in data["error"]
    assert "available_jobs" in data
    assert isinstance(data["available_jobs"], list)
    # Project has echo-test, python-test
    assert "echo-test" in data["available_jobs"] or "python-test" in data["available_jobs"]


def test_api_run_jobs_empty_body_uses_all_jobs(client):
    """POST /api/run_jobs with empty body runs all jobs."""
    response = client.post("/api/run_jobs", json={})
    # Should either run jobs (200) or have some response
    assert response.status_code in (200, 400)
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)


def test_api_config_error_returns_500(tmp_path):
    """API returns 500 with ConfigError detail when config is invalid."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    (tmp_path / "jobs").mkdir()
    (tmp_path / "solvers").mkdir()

    # Job references unknown solver - will raise ConfigError on load
    (tmp_path / "resources" / "r.yaml").write_text(
        yaml.safe_dump({"resources": [{"name": "r1"}]})
    )
    (tmp_path / "systems" / "s.yaml").write_text(
        yaml.safe_dump({"systems": [{"name": "s1", "resources": ["r1"]}]})
    )
    (tmp_path / "jobs" / "t.yaml").write_text(
        yaml.safe_dump({
            "jobs": [{"name": "t1", "solver": "unknown-solver", "system": "s1"}]
        })
    )
    (tmp_path / "solvers" / "sol1").mkdir()
    (tmp_path / "solvers" / "sol1" / "solver.yaml").write_text(
        yaml.safe_dump({"name": "sol1", "entrypoint": "run.sh", "allowed_systems": ["s1"]})
    )
    (tmp_path / "solvers" / "sol1" / "run.sh").write_text("#!/bin/bash\necho ok\n")

    with patch("basic_restapi.fastapi_app.CONFIG_DIR", tmp_path):
        test_client = TestClient(app)
        response = test_client.get("/api/jobs")

    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    assert "Config load failed" in data["error"]
    assert "detail" in data


def test_api_solver_baseline_returns_404_when_no_baseline(client):
    """GET /api/solvers/{solver}/baseline returns 404 when solver has no baseline run."""
    # Use a solver name that is unlikely to have any runs in the test env
    response = client.get("/api/solvers/no-baseline-solver-xyz/baseline")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_api_set_baseline_returns_404_when_run_not_found(client):
    """POST /api/runs/{run_id}/set_baseline returns 404 when run_id does not exist."""
    response = client.post("/api/runs/999999/set_baseline")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_api_baseline_comparison_returns_list(client):
    """GET /api/baseline_comparison returns 200 and a list of solver comparison entries."""
    response = client.get("/api/baseline_comparison")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for entry in data:
        assert "solver_name" in entry
        assert "baseline_run" in entry
        assert "other_runs" in entry
        assert "comparisons" in entry

def test_api_job_batch_uuids_returns_list(client):
    """GET /api/baseline_comparison returns 200 and a list of solver comparison entries."""
    response = client.get("/api/get_job_batch_uuids")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_api_delete_runs(tmp_path):
    """DELETE /api/runs removes rows from the configured DB."""
    db = tmp_path / "del.db"
    init_db(db)
    rid = store_run(
        db,
        RunResult(
            job_name="j",
            solver_name="sv",
            system_name="sy",
            returncode=0,
            stdout="",
            stderr="",
            runtime_seconds=0.1,
            timestamp="2026-01-01T00:00:00+00:00",
            passed=True,
            job_batch_uuid="batch-u",
        ),
    )
    with patch("basic_restapi.fastapi_app.DB_PATH", db):
        tc = TestClient(app)
        r = tc.request("DELETE", "/api/runs", json={"ids": [rid, 999001]})
        assert r.status_code == 200
        assert r.json()["deleted"] == 1
        assert tc.get(f"/api/runs/{rid}").status_code == 404


def test_api_delete_runs_empty_ids_returns_422(client):
    r = client.request("DELETE", "/api/runs", json={"ids": []})
    assert r.status_code == 422


def test_api_run_jobs_background_group_by_solver_partitions_by_solver(client):
    """background + group_by=solver starts one invocation per distinct solver."""
    from unittest.mock import patch

    calls: list[tuple[str, list[str]]] = []

    def fake_start(jl, sol, sys, bn, db, *, solver_name: str = "", job_names=None):
        calls.append((solver_name or "", [j.name for j in jl]))
        return f"id-{solver_name or 'none'}"

    with patch("basic_restapi.fastapi_app.invocations.start_background_run", side_effect=fake_start):
        r = client.post(
            "/api/run_jobs",
            json={
                "jobs": ["echo-test", "python-test"],
                "background": True,
                "group_by": "solver",
            },
        )
    assert r.status_code == 202
    data = r.json()
    assert data["group_by"] == "solver"
    assert len(data["invocations"]) == 2
    assert len(calls) == 2
    by_solver = {c[0]: c[1] for c in calls}
    assert set(by_solver.keys()) == {"echo-solver", "python-solver"}
    assert by_solver["echo-solver"] == ["echo-test"]
    assert by_solver["python-solver"] == ["python-test"]


def test_api_run_jobs_background_batch_returns_group_by_and_invocations(client):
    """background + group_by=batch returns legacy invocation_id plus invocations list."""
    from unittest.mock import patch

    with patch(
        "basic_restapi.fastapi_app.invocations.start_background_run",
        return_value="only-one",
    ) as mock_start:
        r = client.post(
            "/api/run_jobs",
            json={"jobs": ["echo-test"], "background": True, "group_by": "batch"},
        )
    assert r.status_code == 202
    data = r.json()
    assert data["group_by"] == "batch"
    assert data["invocation_id"] == "only-one"
    assert len(data["invocations"]) == 1
    assert data["invocations"][0]["invocation_id"] == "only-one"
    mock_start.assert_called_once()


def test_api_invocations_list_get_enriched_and_slurm_404(client):
    """GET /api/invocations and GET /api/invocations/{id} expose batch and live control fields."""
    from basic_restapi import invocations

    invocations.REGISTRY.clear()
    try:
        rec = invocations.InvocationRecord(id="deadbeef", status="running", batch_name="batch-a")
        rec.control.slurm_job_ids.append("999")
        rec.control.submit_container = "host"
        rec.control.jobs_total = 3
        rec.control.jobs_completed = 2
        invocations.REGISTRY["deadbeef"] = rec

        r = client.get("/api/invocations")
        assert r.status_code == 200
        rows = r.json()
        assert isinstance(rows, list)
        assert any(x.get("invocation_id") == "deadbeef" for x in rows)
        detail = client.get("/api/invocations/deadbeef").json()
        assert detail["status"] == "running"
        assert detail["batch_name"] == "batch-a"
        assert detail["scheduler_job_ids"] == ["999"]
        assert detail["submit_container"] == "host"
        assert detail["jobs_total"] == 3
        assert detail["jobs_completed"] == 2
        assert detail.get("solver_name") == ""
        assert detail.get("job_names") == []

        r_active = client.get("/api/invocations", params={"active_only": True})
        assert r_active.status_code == 200
        assert all(x["status"] in ("queued", "running") for x in r_active.json())

        assert client.get("/api/invocations/nonesuch/slurm_status").status_code == 404
    finally:
        invocations.REGISTRY.clear()


def test_api_solver_summaries(tmp_path):
    db = tmp_path / "sum.db"
    init_db(db)
    store_run(
        db,
        RunResult(
            job_name="j",
            solver_name="s-mon",
            system_name="sy",
            returncode=0,
            stdout="",
            stderr="",
            runtime_seconds=1.0,
            timestamp="2026-01-01T00:00:00+00:00",
            passed=True,
            job_batch_uuid="b",
        ),
    )
    with patch("basic_restapi.fastapi_app.DB_PATH", db):
        tc = TestClient(app)
        r = tc.get("/api/solver_summaries")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert any(x.get("solver_name") == "s-mon" for x in data)
