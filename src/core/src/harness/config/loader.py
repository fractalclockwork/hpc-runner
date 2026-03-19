# config/loader.py - Load TOML/YAML definitions for Resources, Systems, Solvers, Jobs
from __future__ import annotations

import yaml
from pathlib import Path

from .schemas import Resource, System, Solver, Job, MetricSpec


class ConfigError(Exception):
    """Raised when configuration is invalid or cross-references are broken."""


def _glob_yaml(glob_dir: Path, _pattern_base: str = "") -> list[Path]:
    """Return paths matching *.yaml and *.yml, avoiding duplicates when both exist."""
    seen: set[str] = set()
    paths: list[Path] = []
    for ext in (".yaml", ".yml"):
        for f in glob_dir.glob(f"*{ext}"):
            stem = f.stem
            if stem not in seen:
                seen.add(stem)
                paths.append(f)
    return paths


def _load_yaml(path: Path) -> dict:
    """Load YAML file. Raises ConfigError on parse or I/O errors."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except OSError as e:
        raise ConfigError(f"Cannot read config file {path}: {e}") from e
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in {path}: {e}") from e
    return data if isinstance(data, dict) else {}


def load_resources(config_dir: Path) -> dict[str, Resource]:
    """Load resources from config_dir/resources/ or resources key in config."""
    resources: dict[str, Resource] = {}
    resources_dir = config_dir / "resources"
    if resources_dir.exists():
        for f in _glob_yaml(resources_dir, "resources"):
            data = _load_yaml(f)
            for item in data.get("resources", [data]):
                if not isinstance(item, dict):
                    raise ConfigError(f"Resource entry in {f} must be a dict, got {type(item).__name__}")
                if "name" not in item:
                    raise ConfigError(f"Resource in {f} missing required field 'name'. Keys: {list(item.keys())}")
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
        for f in _glob_yaml(systems_dir, "systems"):
            data = _load_yaml(f)
            for item in data.get("systems", [data]):
                if not isinstance(item, dict):
                    raise ConfigError(f"System entry in {f} must be a dict, got {type(item).__name__}")
                if "name" not in item:
                    raise ConfigError(f"System in {f} missing required field 'name'. Keys: {list(item.keys())}")
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
    if not isinstance(d, dict) or "name" not in d:
        raise ConfigError(f"Metric spec must have 'name' field. Got: {d}")
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
            folder = f.parent
            if folder.name.startswith("_") or folder.name == "template":
                continue
            data = _load_yaml(f)
            if not isinstance(data, dict):
                raise ConfigError(f"Solver config {f} must be a YAML object, got {type(data).__name__}")
            ep = data.get("entrypoint", "run.sh")
            if not (folder / ep).exists() and (folder / "run.sh").exists():
                ep = "run.sh"
            metrics = []
            for m in data.get("metrics", []):
                try:
                    metrics.append(_metric_from_dict(m))
                except ConfigError as e:
                    raise ConfigError(f"In solver {folder.name}: {e}") from e
            cwd_val = data.get("cwd", True)
            if cwd_val is False:
                cwd = None
            elif isinstance(cwd_val, str):
                cwd = cwd_val
            else:
                cwd = str(folder)
            s = Solver(
                name=data.get("name", folder.name),
                version=data.get("version", "0.0.0"),
                entrypoint=str(folder / ep),
                cwd=cwd,
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


def load_jobs(config_dir: Path) -> dict[str, Job]:
    """Load jobs from config_dir/jobs/."""
    jobs: dict[str, Job] = {}
    jobs_dir = config_dir / "jobs"
    if jobs_dir.exists():
        for f in _glob_yaml(jobs_dir, "jobs"):
            data = _load_yaml(f)
            for item in data.get("jobs", [data]):
                if not isinstance(item, dict):
                    raise ConfigError(f"Job entry in {f} must be a dict, got {type(item).__name__}")
                for key in ("name", "solver", "system"):
                    if key not in item:
                        raise ConfigError(f"Job in {f} missing required field '{key}'. Keys: {list(item.keys())}")
                j = Job(
                    name=item["name"],
                    solver=item["solver"],
                    system=item["system"],
                    parameters=item.get("parameters", {}),
                    success_criteria=item.get("success_criteria", {}),
                    schedule=item.get("schedule"),
                    timeout_seconds=item.get("timeout_seconds"),
                    baseline=bool(item.get("baseline", False)),
                    extra={k: v for k, v in item.items() if k not in ("name", "solver", "system", "parameters", "success_criteria", "schedule", "timeout_seconds", "baseline")},
                )
                jobs[j.name] = j
    return jobs


def validate_config(
    resources: dict[str, Resource],
    systems: dict[str, System],
    solvers: dict[str, Solver],
    jobs: dict[str, Job],
) -> None:
    """Validate cross-references. Raises ConfigError on first failure."""
    for job in jobs.values():
        if job.solver not in solvers:
            raise ConfigError(
                f"Job '{job.name}' references unknown solver '{job.solver}'. "
                f"Available solvers: {sorted(solvers.keys())}"
            )
        if job.system not in systems:
            raise ConfigError(
                f"Job '{job.name}' references unknown system '{job.system}'. "
                f"Available systems: {sorted(systems.keys())}"
            )
        solver = solvers[job.solver]
        if solver.allowed_systems and job.system not in solver.allowed_systems:
            raise ConfigError(
                f"Job '{job.name}' uses system '{job.system}' but solver '{solver.name}' "
                f"allows only: {solver.allowed_systems}"
            )
    for system in systems.values():
        for rname in system.resources:
            if rname not in resources:
                raise ConfigError(
                    f"System '{system.name}' references unknown resource '{rname}'. "
                    f"Available resources: {sorted(resources.keys())}"
                )
    for solver in solvers.values():
        ep_path = Path(solver.entrypoint)
        if not ep_path.exists():
            raise ConfigError(
                f"Solver '{solver.name}': entrypoint '{solver.entrypoint}' not found"
            )


def load_all(
    config_dir: Path,
    solvers_root: Path | None = None,
    validate: bool = True,
) -> tuple[dict[str, Resource], dict[str, System], dict[str, Solver], dict[str, Job]]:
    """Load all config entities from a config directory."""
    config_path = Path(config_dir)
    if not config_path.exists():
        raise ConfigError(f"Config directory not found: {config_path}")
    if not config_path.is_dir():
        raise ConfigError(f"Config path is not a directory: {config_path}")
    resources = load_resources(config_path)
    systems = load_systems(config_path)
    solvers = load_solvers(config_path, solvers_root)
    jobs = load_jobs(config_path)
    if validate:
        validate_config(resources, systems, solvers, jobs)
    return resources, systems, solvers, jobs
