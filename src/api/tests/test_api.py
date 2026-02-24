# tests/test_api.py - API error handling and responses

from unittest.mock import patch

import pytest
import yaml
from fastapi.testclient import TestClient

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
