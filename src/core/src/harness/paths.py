"""Shared path utilities for project root, DB, and config directory."""

from __future__ import annotations

from pathlib import Path


def get_project_root() -> Path:
    """Find project root by walking up to directory containing pyproject.toml and configs/."""
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / "pyproject.toml").exists() and (parent / "configs").is_dir():
            return parent
    # Fallback: workspace root (has pyproject.toml with [tool.uv.workspace])
    for parent in p.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Could not find project root (no pyproject.toml found)")


def get_db_path() -> Path:
    """Return path to harness SQLite database."""
    return get_project_root() / "data" / "harness.db"


def get_config_dir() -> Path:
    """Return path to configs directory."""
    return get_project_root() / "configs"
