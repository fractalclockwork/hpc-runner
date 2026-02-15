# config/loader.py - Load TOML/YAML definitions for Resources, Systems, Solvers, Tests
from __future__ import annotations

import yaml
from pathlib import Path

from .schemas import Resource, System, Solver, Test, MetricSpec


def _load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_resources(config_dir: Path) -> dict[str, Resource]:
    """Load resources from config_dir/resources/ or resources key in config."""
    resources: dict[str, Resource] = {}
    resources_dir = config_dir / "resources"
    if resources_dir.exists():
        for f in resources_dir.glob("*.yaml"):
            data = _load_yaml(f)
            for item in data.get("resources", [data]):
                r = Resource(
                    name=item["name"],
                    cpus=item.get("cpus"),
                    gpus=item.get("gpus"),
                    memory_gb=item.get("memory_gb"),
                    extra={k: v for k, v in item.items() if k not in ("name", "cpus", "gpus", "memory_gb")},
                )
                resources[r.name] = r
    return resources


def load_systems(config_dir: Path) -> dict[str, System]:
    """Load systems from config_dir/systems/."""
    systems: dict[str, System] = {}
    systems_dir = config_dir / "systems"
    if systems_dir.exists():
        for f in systems_dir.glob("*.yaml"):
            data = _load_yaml(f)
            for item in data.get("systems", [data]):
                s = System(
                    name=item["name"],
                    resources=item.get("resources", []),
                    env=item.get("env", {}),
                    constraints=item.get("constraints", []),
                    extra={k: v for k, v in item.items() if k not in ("name", "resources", "env", "constraints")},
                )
                systems[s.name] = s
    return systems


def _metric_from_dict(d: dict) -> MetricSpec:
    return MetricSpec(
        name=d["name"],
        unit=d.get("unit"),
        min_=d.get("min"),
        max_=d.get("max"),
        required=d.get("required", True),
    )


def load_solvers(config_dir: Path, solvers_root: Path | None = None) -> dict[str, Solver]:
    """Load solvers from config_dir/solvers/ or solver folders with solver.yaml."""
    solvers: dict[str, Solver] = {}
    solvers_dir = config_dir / "solvers" if solvers_root is None else solvers_root
    if solvers_dir.exists():
        for f in solvers_dir.glob("**/solver.yaml"):
            data = _load_yaml(f)
            folder = f.parent
            ep = data.get("entrypoint", "run.sh")
            if not (folder / ep).exists() and (folder / "run.sh").exists():
                ep = "run.sh"
            metrics = [_metric_from_dict(m) for m in data.get("metrics", [])]
            s = Solver(
                name=data.get("name", folder.name),
                version=data.get("version", "0.0.0"),
                entrypoint=str(folder / ep),
                cwd=str(folder) if data.get("cwd", True) else None,
                allowed_systems=data.get("allowed_systems", []),
                parser_config=str(folder / data["parser_config"]) if data.get("parser_config") else None,
                metrics=metrics,
                log_names=data.get("log_names", []),
                extra={k: v for k, v in data.items() if k not in (
                    "name", "version", "entrypoint", "cwd", "allowed_systems",
                    "parser_config", "metrics", "log_names"
                )},
            )
            solvers[s.name] = s
    return solvers


def load_tests(config_dir: Path) -> dict[str, Test]:
    """Load tests from config_dir/tests/."""
    tests: dict[str, Test] = {}
    tests_dir = config_dir / "tests"
    if tests_dir.exists():
        for f in tests_dir.glob("*.yaml"):
            data = _load_yaml(f)
            for item in data.get("tests", [data]):
                t = Test(
                    name=item["name"],
                    solver=item["solver"],
                    system=item["system"],
                    parameters=item.get("parameters", {}),
                    success_criteria=item.get("success_criteria", {}),
                    schedule=item.get("schedule"),
                    extra={k: v for k, v in item.items() if k not in ("name", "solver", "system", "parameters", "success_criteria", "schedule")},
                )
                tests[t.name] = t
    return tests


def load_all(config_dir: Path, solvers_root: Path | None = None) -> tuple[dict[str, Resource], dict[str, System], dict[str, Solver], dict[str, Test]]:
    """Load all config entities from a config directory."""
    config_path = Path(config_dir)
    resources = load_resources(config_path)
    systems = load_systems(config_path)
    solvers = load_solvers(config_path, solvers_root)
    tests = load_tests(config_path)
    return resources, systems, solvers, tests
