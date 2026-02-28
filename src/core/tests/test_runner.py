# tests/test_runner.py - Test Runner execution

from unittest.mock import patch

import yaml

from harness import load_all, run_jobs
from harness.config import Job


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

    resources, systems, solvers, jobs = load_all(tmp_path, None)
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

    resources, systems, solvers, jobs = load_all(tmp_path, None)
    results = run_jobs([jobs["metrics-test"]], solvers, systems)
    assert len(results) == 1
    assert results[0].passed
    assert results[0].metrics["mlups"] == 3200000.0
    assert results[0].metrics["runtime"] == 25.5

def test_run_with_metric_validation_failure(tmp_path, caplog):
    """Run solver with metrics spec where value is out of range; validation should fail."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    (tmp_path / "jobs").mkdir()
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()

    # Minimal resource/system config
    (tmp_path / "resources" / "default.yaml").write_text(yaml.safe_dump({
        "resources": [{"name": "dev", "cpus": 4}]
    }))
    (tmp_path / "systems" / "default.yaml").write_text(yaml.safe_dump({
        "systems": [{"name": "dev-system", "resources": ["dev"]}]
    }))

    # Solver with parser_config AND a metrics spec that will fail validation
    solver_dir = solvers_dir / "metrics-solver-bad"
    solver_dir.mkdir()
    (solver_dir / "solver.yaml").write_text(yaml.safe_dump({
        "name": "metrics-solver-bad",
        "entrypoint": "run.py",
        "allowed_systems": ["dev-system"],
        "parser_config": "parser_config.yaml",
        "metrics": [
            {
                "name": "mlups",
                "unit": "MLUPS",
                "min": 0,
                "max": 1.0e6,   # deliberately lower than what run.py prints
                "required": True,
            }
        ],
    }))
    (solver_dir / "parser_config.yaml").write_text(yaml.safe_dump({
        "patterns": [
            {"name": "mlups", "regex": r"MLUPS:\s*([\d.e+-]+)", "type": "float"},
        ]
    }))
    (solver_dir / "run.py").write_text(
        "print('MLUPS: 3.2e6')\n"  # 3.2e6 > max 1.0e6, should fail validation
    )

    (tmp_path / "jobs" / "sample.yaml").write_text(yaml.safe_dump({
        "jobs": [{"name": "metrics-test-bad", "solver": "metrics-solver-bad", "system": "dev-system"}]
    }))

    resources, systems, solvers, jobs = load_all(tmp_path, solvers_dir)

    import logging
    with caplog.at_level(logging.WARNING):
        results = run_jobs([jobs["metrics-test-bad"]], solvers, systems)

    assert len(results) == 1
    result = results[0]

    # Metric was extracted correctly
    assert result.metrics["mlups"] == 3_200_000.0

    # But validation should have failed and forced passed = False
    assert result.passed is False

    # And a warning should have been logged with our validation errors
    assert "runner.metrics_invalid" in caplog.text
    assert "mlups" in caplog.text

def test_run_with_metric_validation_success(tmp_path, caplog):
    """Run solver with metrics spec where value is in range; validation should pass."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    (tmp_path / "jobs").mkdir()
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()

    # Minimal resource/system config
    (tmp_path / "resources" / "default.yaml").write_text(yaml.safe_dump({
        "resources": [{"name": "dev", "cpus": 4}]
    }))
    (tmp_path / "systems" / "default.yaml").write_text(yaml.safe_dump({
        "systems": [{"name": "dev-system", "resources": ["dev"]}]
    }))

    # Solver with parser_config AND a metrics spec that will fail validation
    solver_dir = solvers_dir / "metrics-solver-bad"
    solver_dir.mkdir()
    (solver_dir / "solver.yaml").write_text(yaml.safe_dump({
        "name": "metrics-solver-bad",
        "entrypoint": "run.py",
        "allowed_systems": ["dev-system"],
        "parser_config": "parser_config.yaml",
        "metrics": [
            {
                "name": "mlups",
                "unit": "MLUPS",
                "min": 0,
                "max": 5.0e6,   # deliberately higher than what run.py prints
                "required": True,
            }
        ],
    }))
    (solver_dir / "parser_config.yaml").write_text(yaml.safe_dump({
        "patterns": [
            {"name": "mlups", "regex": r"MLUPS:\s*([\d.e+-]+)", "type": "float"},
        ]
    }))
    (solver_dir / "run.py").write_text(
        "print('MLUPS: 3.2e6')\n"  # 3.2e6 < max 5.0e6, should pass validation
    )

    (tmp_path / "jobs" / "sample.yaml").write_text(yaml.safe_dump({
        "jobs": [{"name": "metrics-test-bad", "solver": "metrics-solver-bad", "system": "dev-system"}]
    }))

    resources, systems, solvers, jobs = load_all(tmp_path, solvers_dir)

    import logging
    with caplog.at_level(logging.WARNING):
        results = run_jobs([jobs["metrics-test-bad"]], solvers, systems)

    assert len(results) == 1
    result = results[0]

    # Metric was extracted correctly
    assert result.metrics["mlups"] == 3_200_000.0

    # But validation should have passed and forced passed = True
    assert result.passed is True

    assert "runner.metrics_invalid" not in caplog.text
    assert "mlups" not in caplog.text

def test_run_with_missing_required_metric(tmp_path, caplog):
    """Validation fails when a required metric is not present in extracted metrics."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    (tmp_path / "jobs").mkdir()
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()

    # Minimal resource/system config
    (tmp_path / "resources" / "default.yaml").write_text(yaml.safe_dump({
        "resources": [{"name": "dev", "cpus": 4}]
    }))
    (tmp_path / "systems" / "default.yaml").write_text(yaml.safe_dump({
        "systems": [{"name": "dev-system", "resources": ["dev"]}]
    }))

    # Solver requires two metrics (mlups and runtime), but parser only extracts mlups
    solver_dir = solvers_dir / "metrics-solver-missing"
    solver_dir.mkdir()
    (solver_dir / "solver.yaml").write_text(yaml.safe_dump({
        "name": "metrics-solver-missing",
        "entrypoint": "run.py",
        "allowed_systems": ["dev-system"],
        "parser_config": "parser_config.yaml",
        "metrics": [
            {
                "name": "mlups",
                "unit": "MLUPS",
                "min": 0,
                "required": True,
            },
            {
                "name": "runtime",
                "unit": "s",
                "required": True,  # will be missing from extracted metrics
            },
        ],
    }))
    # Parser only knows how to extract mlups, not runtime
    (solver_dir / "parser_config.yaml").write_text(yaml.safe_dump({
        "patterns": [
            {"name": "mlups", "regex": r"MLUPS:\s*([\d.e+-]+)", "type": "float"},
        ]
    }))
    # Log only contains mlups, no runtime line
    (solver_dir / "run.py").write_text(
        "print('MLUPS: 3.2e6')\n"
    )

    (tmp_path / "jobs" / "sample.yaml").write_text(yaml.safe_dump({
        "jobs": [{"name": "metrics-test-missing", "solver": "metrics-solver-missing", "system": "dev-system"}]
    }))

    resources, systems, solvers, jobs = load_all(tmp_path, solvers_dir)

    import logging
    with caplog.at_level(logging.WARNING):
        results = run_jobs([jobs["metrics-test-missing"]], solvers, systems)

    assert len(results) == 1
    result = results[0]

    # Only mlups was extracted
    assert result.metrics["mlups"] == 3_200_000.0
    assert "runtime" not in result.metrics

    # Validation should fail because required runtime metric is missing
    assert result.passed is False

    # Warning should mention validation failure and the missing metric
    assert "runner.metrics_invalid" in caplog.text
    assert "Missing required metric: runtime" in caplog.text

def test_run_jobs_missing_solver_returns_result_with_stderr(tmp_path):
    """run_jobs with missing solver returns RunResult with passed=False and clear stderr."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()

    (tmp_path / "resources" / "r.yaml").write_text(
        yaml.safe_dump({"resources": [{"name": "r1"}]})
    )
    (tmp_path / "systems" / "s.yaml").write_text(
        yaml.safe_dump({"systems": [{"name": "s1", "resources": ["r1"]}]})
    )
    (solvers_dir / "sol1").mkdir()
    (solvers_dir / "sol1" / "solver.yaml").write_text(
        yaml.safe_dump({"name": "sol1", "entrypoint": "run.sh", "allowed_systems": ["s1"]})
    )
    (solvers_dir / "sol1" / "run.sh").write_text("#!/bin/bash\necho ok\n")

    _, systems, solvers, _ = load_all(tmp_path, None, validate=False)
    job = Job(name="t1", solver="unknown-solver", system="s1")

    results = run_jobs([job], solvers, systems)
    assert len(results) == 1
    assert not results[0].passed
    assert results[0].returncode == -1
    assert "unknown-solver" in results[0].stderr
    assert "not found" in results[0].stderr


def test_run_jobs_missing_system_returns_result_with_stderr(tmp_path):
    """run_jobs with missing system returns RunResult with passed=False and clear stderr."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()

    (tmp_path / "resources" / "r.yaml").write_text(
        yaml.safe_dump({"resources": [{"name": "r1"}]})
    )
    (tmp_path / "systems" / "s.yaml").write_text(
        yaml.safe_dump({"systems": [{"name": "s1", "resources": ["r1"]}]})
    )
    (solvers_dir / "sol1").mkdir()
    (solvers_dir / "sol1" / "solver.yaml").write_text(
        yaml.safe_dump({"name": "sol1", "entrypoint": "run.sh", "allowed_systems": ["s1"]})
    )
    (solvers_dir / "sol1" / "run.sh").write_text("#!/bin/bash\necho ok\n")

    _, systems, solvers, _ = load_all(tmp_path, None, validate=False)
    job = Job(name="t1", solver="sol1", system="unknown-system")

    results = run_jobs([job], solvers, systems)
    assert len(results) == 1
    assert not results[0].passed
    assert results[0].returncode == -1
    assert "unknown-system" in results[0].stderr
    assert "not found" in results[0].stderr


def test_run_job_timeout_stderr_message(tmp_path):
    """run_job sets clear stderr when subprocess times out."""
    import subprocess

    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    (tmp_path / "jobs").mkdir()
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()

    (tmp_path / "resources" / "r.yaml").write_text(
        yaml.safe_dump({"resources": [{"name": "r1"}]})
    )
    (tmp_path / "systems" / "s.yaml").write_text(
        yaml.safe_dump({"systems": [{"name": "s1", "resources": ["r1"]}]})
    )
    (tmp_path / "jobs" / "t.yaml").write_text(
        yaml.safe_dump({"jobs": [{"name": "t1", "solver": "sol1", "system": "s1"}]})
    )
    (solvers_dir / "sol1").mkdir()
    (solvers_dir / "sol1" / "solver.yaml").write_text(
        yaml.safe_dump({"name": "sol1", "entrypoint": "run.sh", "allowed_systems": ["s1"]})
    )
    (solvers_dir / "sol1" / "run.sh").write_text("#!/bin/bash\nsleep 999\n")

    _, systems, solvers, jobs = load_all(tmp_path, solvers_dir)
    from harness.runner import run_job

    with patch("harness.runner.subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired(
            "sleep 999", 3600, None, None
        )
        result = run_job(jobs["t1"], solvers["sol1"], systems["s1"])

    assert not result.passed
    assert "timed out" in result.stderr
    assert "3600" in result.stderr


def test_run_job_exception_stderr_message(tmp_path):
    """run_job sets clear stderr when subprocess raises exception."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    (tmp_path / "jobs").mkdir()
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()

    (tmp_path / "resources" / "r.yaml").write_text(
        yaml.safe_dump({"resources": [{"name": "r1"}]})
    )
    (tmp_path / "systems" / "s.yaml").write_text(
        yaml.safe_dump({"systems": [{"name": "s1", "resources": ["r1"]}]})
    )
    (tmp_path / "jobs" / "t.yaml").write_text(
        yaml.safe_dump({"jobs": [{"name": "t1", "solver": "sol1", "system": "s1"}]})
    )
    (solvers_dir / "sol1").mkdir()
    (solvers_dir / "sol1" / "solver.yaml").write_text(
        yaml.safe_dump({"name": "sol1", "entrypoint": "run.sh", "allowed_systems": ["s1"]})
    )
    (solvers_dir / "sol1" / "run.sh").write_text("#!/bin/bash\necho ok\n")

    _, systems, solvers, jobs = load_all(tmp_path, solvers_dir)
    from harness.runner import run_job

    with patch("harness.runner.subprocess.run") as mock_run:
        mock_run.side_effect = OSError("Exec format error")
        result = run_job(jobs["t1"], solvers["sol1"], systems["s1"])

    assert not result.passed
    assert "Execution failed" in result.stderr
    assert "Exec format error" in result.stderr
