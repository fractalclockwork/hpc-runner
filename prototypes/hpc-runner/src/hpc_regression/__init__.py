"""HPC Regression Testing Platform - execution-agnostic test runner."""

from .config import load_all, Resource, System, Solver, Test
from .runner import run_test, run_tests, RunResult
from .parser import extract_metrics
from .storage import init_db, store_run, get_runs, get_run_by_id, get_metrics_history

__all__ = [
    "load_all",
    "Resource",
    "System",
    "Solver",
    "Test",
    "run_test",
    "run_tests",
    "RunResult",
    "extract_metrics",
    "init_db",
    "store_run",
    "get_runs",
    "get_run_by_id",
    "get_metrics_history",
]

