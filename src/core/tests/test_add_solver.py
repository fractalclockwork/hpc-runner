# tests/test_add_solver.py - Tests for --add solver functionality

import yaml

from harness.add_solver import derive_name, add_solver, add_job


def test_derive_name_cpuinfo():
    """cat /proc/cpuinfo -> cpuinfo."""
    assert derive_name("cat /proc/cpuinfo") == "cpuinfo"


def test_derive_name_echo_hello():
    """echo hello -> echo-hello or similar."""
    name = derive_name("echo hello")
    assert "-" in name or "echo" in name
    assert len(name) >= 4


def test_derive_name_single_word():
    """Single command -> sanitized."""
    assert derive_name("hostname") == "hostname"


def test_derive_name_empty():
    """Empty command -> cmd."""
    assert derive_name("") == "cmd"
    assert derive_name("   ") == "cmd"


def test_add_solver_creates_files(tmp_path):
    """add_solver creates solver dir, solver.yaml, run.sh."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    (tmp_path / "resources" / "r.yaml").write_text(
        yaml.safe_dump({"resources": [{"name": "r1"}]})
    )
    (tmp_path / "systems" / "s.yaml").write_text(
        yaml.safe_dump({"systems": [{"name": "s1", "resources": ["r1"]}]})
    )
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()

    solver_name, job_name = add_solver(
        tmp_path, solvers_dir, "echo hello", "s1", name="my-solver"
    )
    assert solver_name == "my-solver"
    assert job_name == "my-solver-test"

    solver_dir = solvers_dir / "my-solver"
    assert solver_dir.exists()
    assert (solver_dir / "solver.yaml").exists()
    assert (solver_dir / "run.sh").exists()

    solver_data = yaml.safe_load((solver_dir / "solver.yaml").read_text())
    assert solver_data["name"] == "my-solver"
    assert solver_data["entrypoint"] == "run.sh"
    assert solver_data["allowed_systems"] == ["s1"]

    run_sh = (solver_dir / "run.sh").read_text()
    assert "echo hello" in run_sh
    assert "#!/usr/bin/env bash" in run_sh


def test_add_solver_duplicate_raises(tmp_path):
    """add_solver raises if solver already exists."""
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()
    (solvers_dir / "existing").mkdir()
    (solvers_dir / "existing" / "solver.yaml").write_text("name: existing\n")
    (solvers_dir / "existing" / "run.sh").write_text("echo ok\n")

    import pytest
    with pytest.raises(ValueError, match="already exists"):
        add_solver(tmp_path, solvers_dir, "echo x", "s1", name="existing")


def test_add_job_creates_file(tmp_path):
    """add_job creates added.yaml with job."""
    (tmp_path / "jobs").mkdir()
    add_job(tmp_path, "my-solver", "dev-system", "my-solver-test")

    jobs_file = tmp_path / "jobs" / "added.yaml"
    assert jobs_file.exists()
    data = yaml.safe_load(jobs_file.read_text())
    assert "jobs" in data
    assert len(data["jobs"]) == 1
    assert data["jobs"][0]["name"] == "my-solver-test"
    assert data["jobs"][0]["solver"] == "my-solver"
    assert data["jobs"][0]["system"] == "dev-system"
    assert data["jobs"][0]["success_criteria"]["returncode"] == 0


def test_add_job_appends_to_existing(tmp_path):
    """add_job appends to existing added.yaml."""
    (tmp_path / "jobs").mkdir()
    (tmp_path / "jobs" / "added.yaml").write_text(
        yaml.safe_dump({"jobs": [{"name": "j1", "solver": "s1", "system": "s1"}]})
    )
    add_job(tmp_path, "s2", "s1", "j2")

    data = yaml.safe_load((tmp_path / "jobs" / "added.yaml").read_text())
    assert len(data["jobs"]) == 2
    assert data["jobs"][1]["name"] == "j2"
    assert data["jobs"][1]["solver"] == "s2"


def test_add_job_duplicate_raises(tmp_path):
    """add_job raises if job name already exists."""
    (tmp_path / "jobs").mkdir()
    (tmp_path / "jobs" / "added.yaml").write_text(
        yaml.safe_dump({"jobs": [{"name": "existing-job", "solver": "s1", "system": "s1"}]})
    )

    import pytest
    with pytest.raises(ValueError, match="already exists"):
        add_job(tmp_path, "s2", "s1", "existing-job")


def test_cli_add_requires_system(capsys, tmp_path):
    """CLI --add without --system exits 1."""
    from harness.cli import main
    exit_code = main([str(tmp_path), "--add", "echo hello"])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "--system" in captured.err


def test_cli_add_system_not_found(capsys, tmp_path):
    """CLI --add with unknown system exits 1."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    (tmp_path / "resources" / "r.yaml").write_text(
        yaml.safe_dump({"resources": [{"name": "r1"}]})
    )
    (tmp_path / "systems" / "s.yaml").write_text(
        yaml.safe_dump({"systems": [{"name": "s1", "resources": ["r1"]}]})
    )

    from harness.cli import main
    exit_code = main([
        str(tmp_path), "--add", "echo hello", "--system", "unknown-system"
    ])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err or "unknown-system" in captured.err


def test_cli_add_creates_and_runs(capsys, tmp_path):
    """CLI --add creates solver, job, runs it, prints JSON."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    (tmp_path / "jobs").mkdir()
    (tmp_path / "resources" / "r.yaml").write_text(
        yaml.safe_dump({"resources": [{"name": "r1"}]})
    )
    (tmp_path / "systems" / "s.yaml").write_text(
        yaml.safe_dump({"systems": [{"name": "s1", "resources": ["r1"]}]})
    )

    from harness.cli import main
    exit_code = main([
        str(tmp_path), "--add", "echo hello", "--system", "s1",
        "--name", "hello-solver", "--no-store",
    ])
    assert exit_code == 0

    # Solver and job created
    assert (tmp_path / "solvers" / "hello-solver" / "solver.yaml").exists()
    assert (tmp_path / "solvers" / "hello-solver" / "run.sh").exists()
    assert (tmp_path / "jobs" / "added.yaml").exists()

    captured = capsys.readouterr()
    assert "hello-solver" in captured.out
    assert "hello-solver-test" in captured.out
    assert "passed" in captured.out or "true" in captured.out
