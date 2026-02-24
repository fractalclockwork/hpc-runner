"""Config file discovery, read/write, and validation for the Streamlit UI."""

from __future__ import annotations

import yaml
from dataclasses import dataclass
from pathlib import Path

from harness import get_config_dir

CONFIGS_DIR = get_config_dir()


@dataclass
class ConfigFile:
    """A config file with its path and category."""

    path: Path
    category: str  # "resources" | "systems" | "jobs" | "solvers"
    display_name: str  # e.g. "default" or "python-solver"


def discover_config_files() -> list[ConfigFile]:
    """Discover all config YAML files in configs/."""
    files: list[ConfigFile] = []

    for category in ("resources", "systems", "jobs"):
        dir_path = CONFIGS_DIR / category
        if dir_path.exists():
            for f in sorted(dir_path.glob("*.yaml")) + sorted(dir_path.glob("*.yml")):
                if f.stem not in {p.path.stem for p in files if p.category == category}:
                    files.append(
                        ConfigFile(path=f, category=category, display_name=f.stem)
                    )

    solvers_dir = CONFIGS_DIR / "solvers"
    if solvers_dir.exists():
        for solver_dir in sorted(solvers_dir.iterdir()):
            if solver_dir.is_dir() and not solver_dir.name.startswith("_"):
                solver_yaml = solver_dir / "solver.yaml"
                if solver_yaml.exists():
                    files.append(
                        ConfigFile(
                            path=solver_yaml,
                            category="solvers",
                            display_name=f"{solver_dir.name}/solver.yaml",
                        )
                    )
                parser_config = solver_dir / "parser_config.yaml"
                if parser_config.exists():
                    files.append(
                        ConfigFile(
                            path=parser_config,
                            category="solvers",
                            display_name=f"{solver_dir.name}/parser_config.yaml",
                        )
                    )

    return files


def read_config(path: Path) -> str:
    """Read config file content as string."""
    return path.read_text(encoding="utf-8")


def write_config(path: Path, content: str) -> None:
    """Write config file content."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def parse_yaml(content: str) -> tuple[dict | list | None, str | None]:
    """Parse YAML string. Returns (data, error_message)."""
    try:
        data = yaml.safe_load(content)
        return (data if data is not None else {}, None)
    except yaml.YAMLError as e:
        return (None, str(e))


def validate_all_configs(config_dir: Path | None = None) -> tuple[bool, str]:
    """Validate all configs via load_all. Returns (success, message)."""
    cfg_dir = config_dir or CONFIGS_DIR
    try:
        from harness.config import load_all, ConfigError
    except ImportError:
        return (False, "harness package not available")

    try:
        load_all(cfg_dir, solvers_root=None, validate=True)
        return (True, "All configs valid.")
    except ConfigError as e:
        return (False, str(e))
    except Exception as e:
        return (False, str(e))
