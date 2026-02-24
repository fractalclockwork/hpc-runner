"""Execution-agnostic harness for running solver jobs."""

from .config import ConfigError, load_all, Resource, System, Solver, Job
from .paths import get_project_root, get_db_path, get_config_dir
from .runner import run_job, run_jobs, RunResult
from .parser import extract_metrics
from .storage import (
    init_db,
    store_run,
    get_runs,
    get_run_by_id,
    get_all_metrics_series,
    get_metrics_history,
)

__all__ = [
    "ConfigError",
    "get_project_root",
    "get_db_path",
    "get_config_dir",
    "load_all",
    "Resource",
    "System",
    "Solver",
    "Job",
    "run_job",
    "run_jobs",
    "RunResult",
    "extract_metrics",
    "init_db",
    "store_run",
    "get_runs",
    "get_run_by_id",
    "get_all_metrics_series",
    "get_metrics_history",
]

