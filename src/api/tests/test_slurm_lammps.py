"""SLURM + LAMMPS integration test — gated by RUN_SLURM_E2E=1 (see docs/slurm_lammps_e2e.md)."""

import os

import pytest
from fastapi.testclient import TestClient

from basic_restapi.fastapi_app import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.slurm
def test_api_run_jobs_lammps_slurm_smoke(client: TestClient) -> None:
    """POST /api/run_jobs for lammps-slurm-smoke when SLURM is configured."""
    if os.environ.get("RUN_SLURM_E2E") != "1":
        pytest.skip("Set RUN_SLURM_E2E=1 and DOCKER_SLURM_CONTAINER or host SLURM (see docs/slurm_lammps_e2e.md)")

    response = client.post("/api/run_jobs", json={"jobs": ["lammps-slurm-smoke"]})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["job_name"] == "lammps-slurm-smoke"
    assert data[0]["passed"] is True
    assert data[0]["returncode"] == 0
