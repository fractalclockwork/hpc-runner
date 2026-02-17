# config/schemas.py - Declarative definitions for Resources, Systems, Solvers, Jobs
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Resource:
    """CPU/GPU counts, memory, node characteristics."""
    name: str
    cpus: int | None = None
    gpus: int | None = None
    memory_gb: float | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class System:
    """Resource bundle, environment variables, constraints."""
    name: str
    resources: list[str]  # Resource names
    env: dict[str, str] = field(default_factory=dict)
    constraints: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricSpec:
    """Expected metric range for validation."""
    name: str
    unit: str | None = None
    min_: float | None = None
    max_: float | None = None
    required: bool = True


@dataclass
class Solver:
    """Solver entrypoint, allowed systems, expected metric ranges."""
    name: str
    entrypoint: str  # Path to run script (run.sh, run.py)
    version: str = "0.0.0"
    cwd: str | None = None
    allowed_systems: list[str] = field(default_factory=list)
    parser_config: str | None = None  # Path to YAML parser config
    metrics: list[MetricSpec] = field(default_factory=list)
    log_names: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class Job:
    """Solver/system pairing, parameters, success criteria."""
    name: str
    solver: str
    system: str
    parameters: dict[str, Any] = field(default_factory=dict)
    success_criteria: dict[str, Any] = field(default_factory=dict)
    schedule: str | None = None  # Cron-like or "manual"
    extra: dict[str, Any] = field(default_factory=dict)
