# tests/test_config.py - Configuration loading
import tempfile
from pathlib import Path

import pytest
import yaml

from hpc_regression.config import (
    load_resources,
    load_systems,
    load_solvers,
    load_tests,
    load_all,
)


def test_load_resources(tmp_path):
    """Load resources from YAML."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "resources" / "default.yaml").write_text(yaml.safe_dump({
        "resources": [
            {"name": "dev", "cpus": 4, "memory_gb": 8},
            {"name": "hpc", "cpus": 64, "gpus": 4, "memory_gb": 256},
        ]
    }))
    resources = load_resources(tmp_path)
    assert len(resources) == 2
    assert resources["dev"].cpus == 4
    assert resources["dev"].memory_gb == 8
    assert resources["hpc"].gpus == 4


def test_load_systems(tmp_path):
    """Load systems from YAML."""
    (tmp_path / "systems").mkdir()
    (tmp_path / "systems" / "default.yaml").write_text(yaml.safe_dump({
        "systems": [
            {"name": "dev-system", "resources": ["dev"], "env": {"FOO": "bar"}},
        ]
    }))
    systems = load_systems(tmp_path)
    assert len(systems) == 1
    assert systems["dev-system"].resources == ["dev"]
    assert systems["dev-system"].env == {"FOO": "bar"}


def test_load_solvers_skips_template(tmp_path):
    """Loader skips directories starting with _ or named template."""
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()

    # Valid solver
    (solvers_dir / "echo-solver").mkdir()
    (solvers_dir / "echo-solver" / "solver.yaml").write_text(yaml.safe_dump({
        "name": "echo-solver",
        "entrypoint": "run.sh",
        "allowed_systems": ["dev-system"],
    }))
    (solvers_dir / "echo-solver" / "run.sh").write_text("#!/bin/bash\necho ok\n")

    # _template should be skipped
    (solvers_dir / "_template").mkdir()
    (solvers_dir / "_template" / "solver.yaml").write_text(yaml.safe_dump({
        "name": "template-solver",
        "entrypoint": "run.sh",
        "allowed_systems": ["dev-system"],
    }))
    (solvers_dir / "_template" / "run.sh").write_text("#!/bin/bash\necho template\n")

    solvers = load_solvers(tmp_path, solvers_dir)
    assert "echo-solver" in solvers
    assert "template-solver" not in solvers
    assert "_template" not in [s.name for s in solvers.values()]


def test_load_tests(tmp_path):
    """Load tests from YAML."""
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "sample.yaml").write_text(yaml.safe_dump({
        "tests": [
            {"name": "t1", "solver": "s1", "system": "sys1", "success_criteria": {"returncode": 0}},
        ]
    }))
    tests = load_tests(tmp_path)
    assert len(tests) == 1
    assert tests["t1"].solver == "s1"
    assert tests["t1"].success_criteria == {"returncode": 0}


def test_load_all(tmp_path):
    """Load all config entities."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    (tmp_path / "tests").mkdir()
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()

    (tmp_path / "resources" / "r.yaml").write_text(yaml.safe_dump({"resources": [{"name": "r1"}]}))
    (tmp_path / "systems" / "s.yaml").write_text(yaml.safe_dump({
        "systems": [{"name": "s1", "resources": ["r1"]}]
    }))
    (tmp_path / "tests" / "t.yaml").write_text(yaml.safe_dump({
        "tests": [{"name": "t1", "solver": "sol1", "system": "s1"}]
    }))
    (solvers_dir / "sol1").mkdir()
    (solvers_dir / "sol1" / "solver.yaml").write_text(yaml.safe_dump({
        "name": "sol1", "entrypoint": "run.sh", "allowed_systems": ["s1"]
    }))
    (solvers_dir / "sol1" / "run.sh").write_text("#!/bin/bash\necho ok\n")

    resources, systems, solvers, tests = load_all(tmp_path, solvers_dir)
    assert "r1" in resources
    assert "s1" in systems
    assert "sol1" in solvers
    assert "t1" in tests
