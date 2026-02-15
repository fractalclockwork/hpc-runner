# tests/test_runner.py
import tempfile
from pathlib import Path

import pytest
import yaml

from hpc_regression import load_all, run_tests


def test_run_minimal(tmp_path):
    """Run tests using the Resource->System->Solver->Test config structure."""
    # Create minimal config structure
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    (tmp_path / "tests").mkdir()
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()

    (tmp_path / "resources" / "default.yaml").write_text(yaml.safe_dump({
        "resources": [{"name": "dev", "cpus": 4}]
    }))
    (tmp_path / "systems" / "default.yaml").write_text(yaml.safe_dump({
        "systems": [{"name": "dev-system", "resources": ["dev"]}]
    }))

    # Create a simple solver
    solver_dir = solvers_dir / "echo-solver"
    solver_dir.mkdir()
    (solver_dir / "solver.yaml").write_text(yaml.safe_dump({
        "name": "echo-solver",
        "entrypoint": "run.sh",
        "allowed_systems": ["dev-system"],
    }))
    (solver_dir / "run.sh").write_text("#!/bin/bash\necho hi-from-test\n")

    (tmp_path / "tests" / "sample.yaml").write_text(yaml.safe_dump({
        "tests": [
            {"name": "echo-test", "solver": "echo-solver", "system": "dev-system"}
        ]
    }))

    resources, systems, solvers, tests = load_all(tmp_path, solvers_dir)
    assert "echo-solver" in solvers
    assert "echo-test" in tests

    results = run_tests([tests["echo-test"]], solvers, systems)
    assert len(results) == 1
    assert results[0].passed
    assert "hi-from-test" in results[0].stdout
