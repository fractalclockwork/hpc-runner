# tests/test_runner.py - Test Runner execution

import yaml

from harness import load_all, run_jobs


def test_run_minimal(tmp_path):
    """Run jobs using the Resource->System->Solver->Job config structure."""
    # Create minimal config structure
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    (tmp_path / "jobs").mkdir()
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

    (tmp_path / "jobs" / "sample.yaml").write_text(yaml.safe_dump({
        "jobs": [
            {"name": "echo-test", "solver": "echo-solver", "system": "dev-system"}
        ]
    }))

    resources, systems, solvers, jobs = load_all(tmp_path, solvers_dir)
    assert "echo-solver" in solvers
    assert "echo-test" in jobs

    results = run_jobs([jobs["echo-test"]], solvers, systems)
    assert len(results) == 1
    assert results[0].passed
    assert "hi-from-test" in results[0].stdout
    assert results[0].processor is not None
    assert len(results[0].processor) > 0


def test_run_with_metric_extraction(tmp_path):
    """Run solver with parser_config; verify metrics are extracted."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    (tmp_path / "jobs").mkdir()
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()

    (tmp_path / "resources" / "default.yaml").write_text(yaml.safe_dump({
        "resources": [{"name": "dev", "cpus": 4}]
    }))
    (tmp_path / "systems" / "default.yaml").write_text(yaml.safe_dump({
        "systems": [{"name": "dev-system", "resources": ["dev"]}]
    }))

    solver_dir = solvers_dir / "metrics-solver"
    solver_dir.mkdir()
    (solver_dir / "solver.yaml").write_text(yaml.safe_dump({
        "name": "metrics-solver",
        "entrypoint": "run.py",
        "allowed_systems": ["dev-system"],
        "parser_config": "parser_config.yaml",
    }))
    (solver_dir / "parser_config.yaml").write_text(yaml.safe_dump({
        "patterns": [
            {"name": "mlups", "regex": r"MLUPS:\s*([\d.e+-]+)", "type": "float"},
            {"name": "runtime", "regex": r"runtime:\s*([\d.]+)", "type": "float"},
        ]
    }))
    (solver_dir / "run.py").write_text("""
import sys
print("MLUPS: 3.2e6")
print("runtime: 25.5")
sys.exit(0)
""")

    (tmp_path / "jobs" / "sample.yaml").write_text(yaml.safe_dump({
        "jobs": [{"name": "metrics-test", "solver": "metrics-solver", "system": "dev-system"}]
    }))

    resources, systems, solvers, jobs = load_all(tmp_path, solvers_dir)
    results = run_jobs([jobs["metrics-test"]], solvers, systems)
    assert len(results) == 1
    assert results[0].passed
    assert results[0].metrics["mlups"] == 3200000.0
    assert results[0].metrics["runtime"] == 25.5
