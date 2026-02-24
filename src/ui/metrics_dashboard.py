"""Metrics dashboard data for the Streamlit Home page."""

from __future__ import annotations

from pathlib import Path

# Project root: src/ui/metrics_dashboard.py -> parents[1] = src/ui, parents[2] = project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "harness.db"


def get_available_metrics() -> list[tuple[str, str]]:
    """Return list of (solver_name, metric_name) with data."""
    try:
        from harness.storage import get_all_metrics_series, init_db
    except ImportError:
        return []

    if not DB_PATH.exists():
        return []

    init_db(DB_PATH)
    return get_all_metrics_series(DB_PATH)


def get_metric_history(solver_name: str, metric_name: str, limit: int = 100) -> list[tuple[str, float]]:
    """Return [(timestamp, value), ...] for a metric."""
    try:
        from harness.storage import get_metrics_history, init_db
    except ImportError:
        return []

    if not DB_PATH.exists():
        return []

    init_db(DB_PATH)
    return get_metrics_history(DB_PATH, solver_name, metric_name, limit=limit)
