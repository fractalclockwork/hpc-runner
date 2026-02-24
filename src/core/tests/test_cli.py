# tests/test_cli.py - CLI error handling and messages


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
