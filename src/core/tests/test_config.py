# tests/test_config.py - Configuration loading

import pytest
import yaml

from harness.config import (
    ConfigError,
    load_resources,
    load_systems,
    load_solvers,
    load_jobs,
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

    solvers = load_solvers(tmp_path, None)
    assert "echo-solver" in solvers
    assert "template-solver" not in solvers
    assert "_template" not in [s.name for s in solvers.values()]


def test_load_jobs(tmp_path):
    """Load jobs from YAML."""
    (tmp_path / "jobs").mkdir()
    (tmp_path / "jobs" / "sample.yaml").write_text(yaml.safe_dump({
        "jobs": [
            {"name": "t1", "solver": "s1", "system": "sys1", "success_criteria": {"returncode": 0}},
        ]
    }))
    jobs = load_jobs(tmp_path)
    assert len(jobs) == 1
    assert jobs["t1"].solver == "s1"
    assert jobs["t1"].success_criteria == {"returncode": 0}


def test_load_jobs_baseline(tmp_path):
    """Job with baseline: true is loaded with baseline=True; omitted defaults to False."""
    (tmp_path / "jobs").mkdir()
    (tmp_path / "jobs" / "sample.yaml").write_text(yaml.safe_dump({
        "jobs": [
            {"name": "base-job", "solver": "s1", "system": "sys1", "baseline": True},
            {"name": "normal-job", "solver": "s1", "system": "sys1"},
        ]
    }))
    jobs = load_jobs(tmp_path)
    assert len(jobs) == 2
    assert jobs["base-job"].baseline is True
    assert jobs["normal-job"].baseline is False


def test_load_all(tmp_path):
    """Load all config entities."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    (tmp_path / "jobs").mkdir()
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()

    (tmp_path / "resources" / "r.yaml").write_text(yaml.safe_dump({"resources": [{"name": "r1"}]}))
    (tmp_path / "systems" / "s.yaml").write_text(yaml.safe_dump({
        "systems": [{"name": "s1", "resources": ["r1"]}]
    }))
    (tmp_path / "jobs" / "t.yaml").write_text(yaml.safe_dump({
        "jobs": [{"name": "t1", "solver": "sol1", "system": "s1"}]
    }))
    (solvers_dir / "sol1").mkdir()
    (solvers_dir / "sol1" / "solver.yaml").write_text(yaml.safe_dump({
        "name": "sol1", "entrypoint": "run.sh", "allowed_systems": ["s1"]
    }))
    (solvers_dir / "sol1" / "run.sh").write_text("#!/bin/bash\necho ok\n")

    resources, systems, solvers, jobs = load_all(tmp_path, None)
    assert "r1" in resources
    assert "s1" in systems
    assert "sol1" in solvers
    assert "t1" in jobs


def test_load_all_config_dir_not_found(tmp_path):
    """load_all raises ConfigError when config dir does not exist."""
    missing = tmp_path / "nonexistent"
    with pytest.raises(ConfigError, match="Config directory not found"):
        load_all(missing)


def test_load_all_validates_job_solver_ref(tmp_path):
    """load_all raises ConfigError when job references unknown solver."""
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
        yaml.safe_dump({
            "jobs": [{"name": "t1", "solver": "unknown-solver", "system": "s1"}]
        })
    )
    (solvers_dir / "sol1").mkdir()
    (solvers_dir / "sol1" / "solver.yaml").write_text(
        yaml.safe_dump({"name": "sol1", "entrypoint": "run.sh", "allowed_systems": ["s1"]})
    )
    (solvers_dir / "sol1" / "run.sh").write_text("#!/bin/bash\necho ok\n")

    with pytest.raises(ConfigError, match="references unknown solver"):
        load_all(tmp_path, None)


def test_load_resources_yml_extension(tmp_path):
    """Loader supports .yml files in addition to .yaml."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "resources" / "dev.yml").write_text(
        yaml.safe_dump({"resources": [{"name": "dev", "cpus": 4}]})
    )
    resources = load_resources(tmp_path)
    assert "dev" in resources
    assert resources["dev"].cpus == 4


def test_load_all_validates_job_system_ref(tmp_path):
    """load_all raises ConfigError when job references unknown system."""
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
        yaml.safe_dump({
            "jobs": [{"name": "t1", "solver": "sol1", "system": "unknown-system"}]
        })
    )
    (solvers_dir / "sol1").mkdir()
    (solvers_dir / "sol1" / "solver.yaml").write_text(
        yaml.safe_dump({"name": "sol1", "entrypoint": "run.sh", "allowed_systems": ["s1"]})
    )
    (solvers_dir / "sol1" / "run.sh").write_text("#!/bin/bash\necho ok\n")

    with pytest.raises(ConfigError, match="references unknown system"):
        load_all(tmp_path, None)


def test_load_all_validates_system_resource_ref(tmp_path):
    """load_all raises ConfigError when system references unknown resource."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    (tmp_path / "jobs").mkdir()
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()

    (tmp_path / "resources" / "r.yaml").write_text(
        yaml.safe_dump({"resources": [{"name": "r1"}]})
    )
    (tmp_path / "systems" / "s.yaml").write_text(
        yaml.safe_dump({"systems": [{"name": "s1", "resources": ["r1", "unknown-resource"]}]})
    )
    (tmp_path / "jobs" / "t.yaml").write_text(
        yaml.safe_dump({"jobs": [{"name": "t1", "solver": "sol1", "system": "s1"}]})
    )
    (solvers_dir / "sol1").mkdir()
    (solvers_dir / "sol1" / "solver.yaml").write_text(
        yaml.safe_dump({"name": "sol1", "entrypoint": "run.sh", "allowed_systems": ["s1"]})
    )
    (solvers_dir / "sol1" / "run.sh").write_text("#!/bin/bash\necho ok\n")

    with pytest.raises(ConfigError, match="references unknown resource"):
        load_all(tmp_path, None)


def test_load_all_validates_solver_allowed_systems(tmp_path):
    """load_all raises ConfigError when job uses system not in solver allowed_systems."""
    (tmp_path / "resources").mkdir()
    (tmp_path / "systems").mkdir()
    (tmp_path / "jobs").mkdir()
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()

    (tmp_path / "resources" / "r.yaml").write_text(
        yaml.safe_dump({"resources": [{"name": "r1"}]})
    )
    (tmp_path / "systems" / "s.yaml").write_text(
        yaml.safe_dump({
            "systems": [
                {"name": "s1", "resources": ["r1"]},
                {"name": "s2", "resources": ["r1"]},
            ]
        })
    )
    (tmp_path / "jobs" / "t.yaml").write_text(
        yaml.safe_dump({
            "jobs": [{"name": "t1", "solver": "sol1", "system": "s2"}]
        })
    )
    (solvers_dir / "sol1").mkdir()
    (solvers_dir / "sol1" / "solver.yaml").write_text(
        yaml.safe_dump({"name": "sol1", "entrypoint": "run.sh", "allowed_systems": ["s1"]})
    )
    (solvers_dir / "sol1" / "run.sh").write_text("#!/bin/bash\necho ok\n")

    with pytest.raises(ConfigError, match="allows only"):
        load_all(tmp_path, None)


def test_load_all_validates_solver_entrypoint_exists(tmp_path):
    """load_all raises ConfigError when solver entrypoint file does not exist."""
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
        yaml.safe_dump({"name": "sol1", "entrypoint": "nonexistent.sh", "allowed_systems": ["s1"]})
    )
    # Do NOT create run.sh - entrypoint points to nonexistent.sh

    with pytest.raises(ConfigError, match="entrypoint.*not found"):
        load_all(tmp_path, None)


def test_load_all_validate_false_skips_validation(tmp_path):
    """load_all with validate=False does not raise on invalid cross-refs."""
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
        yaml.safe_dump({
            "jobs": [{"name": "t1", "solver": "unknown-solver", "system": "s1"}]
        })
    )
    (solvers_dir / "sol1").mkdir()
    (solvers_dir / "sol1" / "solver.yaml").write_text(
        yaml.safe_dump({"name": "sol1", "entrypoint": "run.sh", "allowed_systems": ["s1"]})
    )
    (solvers_dir / "sol1" / "run.sh").write_text("#!/bin/bash\necho ok\n")

    resources, systems, solvers, jobs = load_all(tmp_path, None, validate=False)
    assert "t1" in jobs
    assert jobs["t1"].solver == "unknown-solver"


def test_load_solvers_cwd_false(tmp_path):
    """Solver with cwd: false gets cwd=None (entrypoint parent used at runtime)."""
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()
    (solvers_dir / "s1").mkdir()
    (solvers_dir / "s1" / "solver.yaml").write_text(
        yaml.safe_dump({
            "name": "s1",
            "entrypoint": "run.sh",
            "allowed_systems": [],
            "cwd": False,
        })
    )
    (solvers_dir / "s1" / "run.sh").write_text("#!/bin/bash\necho ok\n")

    solvers = load_solvers(tmp_path, None)
    assert solvers["s1"].cwd is None


def test_load_solvers_cwd_explicit_path(tmp_path):
    """Solver with cwd: /path uses explicit path."""
    solvers_dir = tmp_path / "solvers"
    solvers_dir.mkdir()
    explicit_cwd = tmp_path / "workdir"
    explicit_cwd.mkdir()
    (solvers_dir / "s1").mkdir()
    (solvers_dir / "s1" / "solver.yaml").write_text(
        yaml.safe_dump({
            "name": "s1",
            "entrypoint": "run.sh",
            "allowed_systems": [],
            "cwd": str(explicit_cwd),
        })
    )
    (solvers_dir / "s1" / "run.sh").write_text("#!/bin/bash\necho ok\n")

    solvers = load_solvers(tmp_path, None)
    assert solvers["s1"].cwd == str(explicit_cwd)
