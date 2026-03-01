# tests/test_cli.py - CLI error handling and messages

import json
import yaml

from harness.cli import main


def test_cli_config_error_exits_1(capsys, tmp_path):
    """CLI exits 1 and prints ConfigError to stderr when config dir not found."""
    exit_code = main([str(tmp_path / "nonexistent"), "--list"])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Configuration error" in captured.err
    assert "not found" in captured.err or "nonexistent" in captured.err


def test_cli_no_jobs_message(capsys, tmp_path):
    """CLI prints helpful message when no jobs exist."""
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
    # Empty jobs - no job definitions
    (solvers_dir / "sol1").mkdir()
    (solvers_dir / "sol1" / "solver.yaml").write_text(
        yaml.safe_dump({"name": "sol1", "entrypoint": "run.sh", "allowed_systems": ["s1"]})
    )
    (solvers_dir / "sol1" / "run.sh").write_text("#!/bin/bash\necho ok\n")

    exit_code = main([str(tmp_path), "--no-store"])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "No jobs to run" in captured.err
    assert "Config dir" in captured.err or str(tmp_path) in captured.err


def test_cli_no_matching_jobs_shows_available(capsys, tmp_path):
    """CLI prints requested vs available when --job filters to empty."""
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

    exit_code = main([
        str(tmp_path),
        "--job", "nonexistent-job",
        "--no-store",
    ])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "No matching jobs" in captured.err
    assert "nonexistent-job" in captured.err
    assert "t1" in captured.err
    assert "Available" in captured.err or "available" in captured.err


def test_cli_list_success(capsys, tmp_path):
    """CLI --list prints available jobs on success."""
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

    exit_code = main([str(tmp_path), "--list"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Available jobs:" in captured.out
    assert "t1" in captured.out


def test_cli_run_output_includes_validation_errors(capsys, tmp_path):
    """CLI JSON output includes validation_errors (list) on every result."""
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

    exit_code = main([str(tmp_path), "--no-store"])
    assert exit_code == 0
    out = json.loads(capsys.readouterr().out)
    assert len(out) == 1
    assert "validation_errors" in out[0]
    assert out[0]["validation_errors"] == []
    assert isinstance(out[0]["validation_errors"], list)


def test_cli_run_with_validation_failure_shows_validation_errors(capsys, tmp_path):
    """When metric validation fails, CLI output includes non-empty validation_errors and exits 1."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    (tmp_path / "jobs").mkdir()
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()

    (tmp_path / "resources" / "default.yaml").write_text(
        yaml.safe_dump({"resources": [{"name": "dev", "cpus": 4}]})
    )
    (tmp_path / "systems" / "default.yaml").write_text(
        yaml.safe_dump({"systems": [{"name": "dev-system", "resources": ["dev"]}]})
    )
    solver_dir = solvers_dir / "metrics-solver-bad"
    solver_dir.mkdir()
    (solver_dir / "solver.yaml").write_text(yaml.safe_dump({
        "name": "metrics-solver-bad",
        "entrypoint": "run.py",
        "allowed_systems": ["dev-system"],
        "parser_config": "parser_config.yaml",
        "metrics": [
            {"name": "mlups", "unit": "MLUPS", "min": 0, "max": 1.0e6, "required": True},
        ],
    }))
    (solver_dir / "parser_config.yaml").write_text(yaml.safe_dump({
        "patterns": [{"name": "mlups", "regex": r"MLUPS:\s*([\d.e+-]+)", "type": "float"}],
    }))
    (solver_dir / "run.py").write_text("print('MLUPS: 3.2e6')\n")

    (tmp_path / "jobs" / "sample.yaml").write_text(yaml.safe_dump({
        "jobs": [{"name": "metrics-test-bad", "solver": "metrics-solver-bad", "system": "dev-system"}],
    }))

    exit_code = main([str(tmp_path), "--no-store"])
    assert exit_code == 1
    out = json.loads(capsys.readouterr().out)
    assert len(out) == 1
    assert "validation_errors" in out[0]
    assert isinstance(out[0]["validation_errors"], list)
    assert len(out[0]["validation_errors"]) > 0
    assert out[0]["passed"] is False


def test_cli_list_runs_shows_validation_error_count(capsys, tmp_path):
    """--list-runs shows validation error count when a run has validation_errors."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    (tmp_path / "jobs").mkdir()
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()

    (tmp_path / "resources" / "default.yaml").write_text(
        yaml.safe_dump({"resources": [{"name": "dev", "cpus": 4}]})
    )
    (tmp_path / "systems" / "default.yaml").write_text(
        yaml.safe_dump({"systems": [{"name": "dev-system", "resources": ["dev"]}]})
    )
    (tmp_path / "jobs" / "t.yaml").write_text(yaml.safe_dump({
        "jobs": [{"name": "t1", "solver": "sol1", "system": "dev-system"}],
    }))
    (solvers_dir / "sol1").mkdir()
    (solvers_dir / "sol1" / "solver.yaml").write_text(yaml.safe_dump({
        "name": "sol1",
        "entrypoint": "run.py",
        "allowed_systems": ["dev-system"],
        "parser_config": "parser_config.yaml",
        "metrics": [{"name": "mlups", "unit": "MLUPS", "min": 0, "max": 1.0e6, "required": True}],
    }))
    (solvers_dir / "sol1" / "parser_config.yaml").write_text(yaml.safe_dump({
        "patterns": [{"name": "mlups", "regex": r"MLUPS:\s*([\d.e+-]+)", "type": "float"}],
    }))
    (solvers_dir / "sol1" / "run.py").write_text("print('MLUPS: 5e6')\n")

    db_path = tmp_path / "harness.db"
    exit_code = main([str(tmp_path), "--db", str(db_path)])
    assert exit_code == 1
    exit_code = main([str(tmp_path), "--db", str(db_path), "--list-runs"])
    assert exit_code == 0
    captured = capsys.readouterr().out
    assert "validation error" in captured
