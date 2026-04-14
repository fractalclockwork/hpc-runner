# tests/test_solver_matrix.py - Repo configs: portable solvers on all production systems

from __future__ import annotations

from pathlib import Path

import pytest

from harness import load_all, run_jobs
from harness.config import build_jobs_from_solver_specs

REPO_CONFIG_DIR = Path(__file__).resolve().parents[3] / "configs"

SOLVERS = ("echo-solver", "python-solver")
SYSTEMS = ("dev-system", "hpc-cluster-01", "sci-slurm-lammps")


@pytest.mark.parametrize("solver_name", SOLVERS)
@pytest.mark.parametrize("system_name", SYSTEMS)
def test_portable_solver_passes_on_each_system(solver_name: str, system_name: str) -> None:
    """Smoke matrix: echo-solver and python-solver run and pass on each defined system."""
    resources, systems, solvers = load_all(REPO_CONFIG_DIR, None)
    assert solver_name in solvers
    assert system_name in systems

    specs = [{"name": solver_name, "system": system_name}]
    job_list = build_jobs_from_solver_specs(solvers, systems, specs)
    results = run_jobs(job_list, solvers, systems, resources=resources)
    assert len(results) == 1
    r = results[0]
    assert r.passed, f"{r.job_name}: {r.validation_errors} stderr={r.stderr!r}"
    assert r.returncode == 0
    assert r.job_name == f"{solver_name}@{system_name}"
    if solver_name == "echo-solver":
        assert "solver_finished" in r.metrics
    else:
        assert "runtime_seconds" in r.metrics
