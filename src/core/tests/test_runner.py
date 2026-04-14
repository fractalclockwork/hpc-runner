# tests/test_runner.py - Test Runner execution

from unittest.mock import patch

import yaml

from harness import load_all, run_jobs
from harness.config import Job, build_jobs_from_solver_specs
from harness.runner import InvocationControl, RunResult


def test_invocation_control_live_stdout_append_snapshot_clear() -> None:
    ctl = InvocationControl()
    assert ctl.snapshot_live_stdout() == ""
    ctl.append_live_log_line("a")
    ctl.append_live_log_line("b\n")
    assert ctl.snapshot_live_stdout() == "ab\n"
    ctl.clear_live_stdout()
    assert ctl.snapshot_live_stdout() == ""


def test_run_minimal(tmp_path):
    """Run jobs using the Resource->System->Solver->Job config structure."""
    # Create minimal config structure
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
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

    resources, systems, solvers = load_all(tmp_path, None)
    assert "echo-solver" in solvers
    jl = build_jobs_from_solver_specs(solvers, systems, [{"name": "echo-solver", "system": None}])
    results = run_jobs(jl, solvers, systems, resources=resources)
    assert len(results) == 1
    assert results[0].passed
    assert "hi-from-test" in results[0].stdout
    assert results[0].processor is not None
    assert len(results[0].processor) > 0


def test_run_jobs_invoke_ctl_live_stdout_mirrors_subprocess(tmp_path):
    """Background-style invoke_ctl path captures stdout into InvocationControl for live APIs."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()

    (tmp_path / "resources" / "default.yaml").write_text(
        yaml.safe_dump({"resources": [{"name": "dev", "cpus": 4}]})
    )
    (tmp_path / "systems" / "default.yaml").write_text(
        yaml.safe_dump({"systems": [{"name": "dev-system", "resources": ["dev"]}]})
    )

    solver_dir = solvers_dir / "echo-solver"
    solver_dir.mkdir()
    (solver_dir / "solver.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "echo-solver",
                "entrypoint": "run.sh",
                "allowed_systems": ["dev-system"],
            }
        )
    )
    (solver_dir / "run.sh").write_text("#!/bin/bash\necho hi-from-test\n")

    _, systems, solvers = load_all(tmp_path, None)
    jl = build_jobs_from_solver_specs(solvers, systems, [{"name": "echo-solver", "system": None}])
    ctl = InvocationControl()
    results = run_jobs(jl, solvers, systems, invoke_ctl=ctl)
    assert len(results) == 1
    assert results[0].passed
    live = ctl.snapshot_live_stdout()
    assert "hi-from-test" in live
    assert "===" in live


def test_run_baseline_job_propagates_baseline_flag(tmp_path):
    """When a job has baseline: true, RunResult.baseline is True."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()

    (tmp_path / "resources" / "default.yaml").write_text(yaml.safe_dump({
        "resources": [{"name": "dev", "cpus": 4}]
    }))
    (tmp_path / "systems" / "default.yaml").write_text(yaml.safe_dump({
        "systems": [{"name": "dev-system", "resources": ["dev"]}]
    }))
    solver_dir = solvers_dir / "echo-solver"
    solver_dir.mkdir()
    (solver_dir / "solver.yaml").write_text(yaml.safe_dump({
        "name": "echo-solver",
        "entrypoint": "run.sh",
        "allowed_systems": ["dev-system"],
        "baseline": True,
    }))
    (solver_dir / "run.sh").write_text("#!/bin/bash\necho hi\n")

    resources, systems, solvers = load_all(tmp_path, None)
    jl = build_jobs_from_solver_specs(solvers, systems, [{"name": "echo-solver", "system": None}])
    assert jl[0].baseline is True

    results = run_jobs(jl, solvers, systems, resources=resources)
    assert len(results) == 1
    assert results[0].baseline is True


def test_run_with_metric_extraction(tmp_path):
    """Run solver with parser_config; verify metrics are extracted."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
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

    resources, systems, solvers = load_all(tmp_path, None)
    jl = build_jobs_from_solver_specs(solvers, systems, [{"name": "metrics-solver", "system": None}])
    results = run_jobs(jl, solvers, systems, resources=resources)
    assert len(results) == 1
    assert results[0].passed
    assert results[0].metrics["mlups"] == 3200000.0
    assert results[0].metrics["runtime"] == 25.5

def test_run_with_metric_validation_failure(tmp_path, caplog):
    """Run solver with metrics spec where value is out of range; validation should fail."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
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

    resources, systems, solvers = load_all(tmp_path, solvers_dir)
    jl = build_jobs_from_solver_specs(solvers, systems, [{"name": "metrics-solver-bad", "system": None}])

    import logging
    with caplog.at_level(logging.WARNING):
        results = run_jobs(jl, solvers, systems, resources=resources)

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

    resources, systems, solvers = load_all(tmp_path, solvers_dir)
    jl = build_jobs_from_solver_specs(solvers, systems, [{"name": "metrics-solver-bad", "system": None}])

    import logging
    with caplog.at_level(logging.WARNING):
        results = run_jobs(jl, solvers, systems, resources=resources)

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

    resources, systems, solvers = load_all(tmp_path, solvers_dir)
    jl = build_jobs_from_solver_specs(solvers, systems, [{"name": "metrics-solver-missing", "system": None}])

    import logging
    with caplog.at_level(logging.WARNING):
        results = run_jobs(jl, solvers, systems, resources=resources)

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

    resources, systems, solvers = load_all(tmp_path, None, validate=False)
    job = Job(name="t1", solver="unknown-solver", system="s1")

    results = run_jobs([job], solvers, systems, resources=resources)
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

    resources, systems, solvers = load_all(tmp_path, None, validate=False)
    job = Job(name="t1", solver="sol1", system="unknown-system")

    results = run_jobs([job], solvers, systems, resources=resources)
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
    (solvers_dir / "sol1" / "run.sh").write_text("#!/bin/bash\nsleep 999\n")

    resources, systems, solvers = load_all(tmp_path, solvers_dir)
    jl = build_jobs_from_solver_specs(solvers, systems, [{"name": "sol1", "system": None}])
    from harness.runner import run_job

    with patch("harness.runner.subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired(
            "sleep 999", 3600, None, None
        )
        result = run_job(jl[0], solvers["sol1"], systems["s1"], resources=resources)

    assert not result.passed
    assert "timed out" in result.stderr
    assert "3600" in result.stderr


def test_run_jobs_cancel_before_start_skips_all_with_same_batch(tmp_path):
    """If cancel_event is set before any run_job, every runnable job is skipped with Cancelled by user."""
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

    resources, systems, solvers = load_all(tmp_path, solvers_dir)
    ctl = InvocationControl()
    ctl.cancel_event.set()
    job_list = [
        Job(name="j1", solver="sol1", system="s1"),
        Job(name="j2", solver="sol1", system="s1"),
    ]
    with patch("harness.runner.run_job") as mock_rj:
        results = run_jobs(job_list, solvers, systems, resources=resources, invoke_ctl=ctl)
        mock_rj.assert_not_called()
    assert len(results) == 2
    for r in results:
        assert r.validation_errors == ["Cancelled by user"]
        assert not r.passed
    assert ctl.jobs_total == 2
    assert ctl.jobs_completed == 2


def test_run_jobs_cancel_after_first_job_skips_second(tmp_path):
    """After the first run_job returns, cancel prevents starting the second job."""
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

    resources, systems, solvers = load_all(tmp_path, solvers_dir)
    ctl = InvocationControl()

    def fake_run_job(j, sol, sys, **kwargs):
        if j.name == "j1":
            ctl.cancel_event.set()
            return RunResult(
                job_name=j.name,
                solver_name=sol.name,
                system_name=sys.name,
                returncode=0,
                stdout="ok",
                stderr="",
                runtime_seconds=0.01,
                timestamp="t1",
                validation_errors=[],
                passed=True,
                processor="x86_64",
                baseline=j.baseline,
                job_batch_uuid=kwargs.get("job_batch_uuid", ""),
                job_batch_date=kwargs.get("job_batch_date"),
                job_batch_name=kwargs.get("job_batch_name", ""),
            )
        raise AssertionError("second job should not run")

    job_list = [
        Job(name="j1", solver="sol1", system="s1"),
        Job(name="j2", solver="sol1", system="s1"),
    ]
    with patch("harness.runner.run_job", side_effect=fake_run_job):
        results = run_jobs(job_list, solvers, systems, resources=resources, invoke_ctl=ctl)
    assert len(results) == 2
    assert results[0].passed
    assert results[0].job_name == "j1"
    assert results[1].validation_errors == ["Cancelled by user"]
    assert results[1].job_name == "j2"


def test_run_job_exception_stderr_message(tmp_path):
    """run_job sets clear stderr when subprocess raises exception."""
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

    resources, systems, solvers = load_all(tmp_path, solvers_dir)
    jl = build_jobs_from_solver_specs(solvers, systems, [{"name": "sol1", "system": None}])
    from harness.runner import run_job

    with patch("harness.runner.subprocess.run") as mock_run:
        mock_run.side_effect = OSError("Exec format error")
        result = run_job(jl[0], solvers["sol1"], systems["s1"], resources=resources)

    assert not result.passed
    assert "Execution failed" in result.stderr
    assert "Exec format error" in result.stderr


def test_env_merge_resource_solver_system(tmp_path):
    """Subprocess env: resource, then solver, then system (later wins on duplicate keys)."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()

    (tmp_path / "resources" / "r.yaml").write_text(
        yaml.safe_dump({"resources": [{"name": "r1", "env": {"A": "res", "RONLY": "r"}}]})
    )
    (tmp_path / "systems" / "s.yaml").write_text(
        yaml.safe_dump({
            "systems": [{"name": "s1", "resources": ["r1"], "env": {"A": "sys", "SONLY": "s"}}],
        })
    )
    solver_dir = solvers_dir / "env-solver"
    solver_dir.mkdir()
    (solver_dir / "solver.yaml").write_text(
        yaml.safe_dump({
            "name": "env-solver",
            "entrypoint": "run.sh",
            "allowed_systems": ["s1"],
            "env": {"A": "sol", "SONLY": "from-solver", "TONLY": "t"},
        })
    )
    (solver_dir / "run.sh").write_text(
        "#!/bin/bash\n"
        'printf "A=%s RONLY=%s SONLY=%s TONLY=%s\\n" "$A" "$RONLY" "$SONLY" "$TONLY"\n'
    )

    resources, systems, solvers = load_all(tmp_path, solvers_dir)
    jl = build_jobs_from_solver_specs(solvers, systems, [{"name": "env-solver", "system": None}])
    results = run_jobs(jl, solvers, systems, resources=resources)
    assert len(results) == 1
    assert results[0].passed
    assert "A=sys" in results[0].stdout
    assert "RONLY=r" in results[0].stdout
    assert "SONLY=s" in results[0].stdout
    assert "TONLY=t" in results[0].stdout
