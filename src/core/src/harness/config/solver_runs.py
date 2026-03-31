# config/solver_runs.py - Build Job list from solver + system selections
from __future__ import annotations

from typing import Any

from .loader import ConfigError
from .schemas import Job, Solver, System


def resolve_system_name(solver: Solver, system_override: str | None, *, solver_label: str) -> str:
    """Pick target system: explicit override, default_system, or sole allowed_system."""
    if system_override is not None and str(system_override).strip():
        sys_name = str(system_override).strip()
        if solver.allowed_systems and sys_name not in solver.allowed_systems:
            raise ConfigError(
                f"Solver '{solver_label}': system '{sys_name}' not in allowed_systems {solver.allowed_systems}"
            )
        return sys_name
    if solver.default_system:
        return solver.default_system
    if len(solver.allowed_systems) == 1:
        return solver.allowed_systems[0]
    raise ConfigError(
        f"Solver '{solver_label}': specify system in the request (allowed: {solver.allowed_systems}; "
        f"set default_system in solver.yaml to make one automatic)"
    )


def build_jobs_from_solver_specs(
    solvers: dict[str, Solver],
    systems: dict[str, System],
    specs: list[dict[str, Any]],
) -> list[Job]:
    """Build runtime Job rows: name is {solver}@{system}; fields from solver config."""
    out: list[Job] = []
    for spec in specs:
        name = spec.get("name")
        if not name:
            raise ConfigError("Each solver spec must include 'name'")
        if name not in solvers:
            raise ConfigError(f"Unknown solver '{name}'. Available: {sorted(solvers.keys())}")
        solver = solvers[name]
        sys_override = spec.get("system")
        system_name = resolve_system_name(solver, sys_override, solver_label=name)
        if system_name not in systems:
            raise ConfigError(
                f"Unknown system '{system_name}' for solver '{name}'. Available: {sorted(systems.keys())}"
            )
        run_name = f"{name}@{system_name}"
        sc = dict(solver.success_criteria) if solver.success_criteria else {}
        out.append(
            Job(
                name=run_name,
                solver=name,
                system=system_name,
                parameters={},
                success_criteria=sc,
                schedule=None,
                timeout_seconds=solver.timeout_seconds,
                baseline=solver.baseline,
                extra={},
            )
        )
    return out
