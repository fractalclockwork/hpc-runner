"""Metrics dashboard data for the Streamlit UI."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

from harness import get_db_path

DB_PATH = get_db_path()

_TREND_QUERY_TTL = 60  # seconds


@st.cache_data(ttl=_TREND_QUERY_TTL)
def get_runtime_trend_data(db_path: str) -> pd.DataFrame:
    """Return a DataFrame of all runs with runtime_seconds, for trend charting.

    Columns: timestamp, solver_name, system_name, job_name, runtime_seconds, passed
    Returns an empty DataFrame (with correct columns) if no data exists.
    """
    path = Path(db_path)
    if not path.exists():
        return pd.DataFrame(
            columns=["timestamp", "solver_name", "system_name", "job_name", "runtime_seconds", "passed"]
        )

    with sqlite3.connect(path) as conn:
        df = pd.read_sql_query(
            """
            SELECT timestamp, solver_name, system_name, job_name,
                   runtime_seconds, passed
            FROM runs
            ORDER BY timestamp ASC
            """,
            conn,
        )

    if df.empty:
        return df

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["passed"] = df["passed"].astype(bool)
    df["series"] = df["solver_name"] + " / " + df["system_name"]
    return df


@st.cache_data(ttl=_TREND_QUERY_TTL)
def get_mlups_trend_data(db_path: str) -> pd.DataFrame:
    """Return a DataFrame of runs that have an 'mlups' key in metrics_json.

    Columns: timestamp, solver_name, system_name, job_name, passed, mlups, series
    Returns an empty DataFrame (with correct columns) if no data exists.
    """
    path = Path(db_path)
    empty = pd.DataFrame(
        columns=["timestamp", "solver_name", "system_name", "job_name", "passed", "mlups", "series"]
    )
    if not path.exists():
        return empty

    with sqlite3.connect(path) as conn:
        df = pd.read_sql_query(
            """
            SELECT timestamp, solver_name, system_name, job_name, passed, metrics_json
            FROM runs
            WHERE metrics_json IS NOT NULL
            ORDER BY timestamp ASC
            """,
            conn,
        )

    if df.empty:
        return empty

    import json

    def _extract_mlups(metrics_json: str) -> float | None:
        try:
            val = json.loads(metrics_json).get("mlups")
            return float(val) if val is not None else None
        except (json.JSONDecodeError, TypeError, ValueError):
            return None

    df["mlups"] = df["metrics_json"].apply(_extract_mlups)
    df = df.dropna(subset=["mlups"]).drop(columns=["metrics_json"])

    if df.empty:
        return empty

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["passed"] = df["passed"].astype(bool)
    df["series"] = df["solver_name"] + " / " + df["system_name"]
    return df


@st.cache_data(ttl=_TREND_QUERY_TTL)
def get_all_metrics_flat(db_path: str) -> pd.DataFrame:
    """Return all numeric metric values per run in long format.

    Columns: timestamp, solver_name, system_name, job_name, metric_name, value, series
    Includes runtime_seconds, returncode, passed (0/1) from fixed columns,
    plus all numeric keys from metrics_json.  Non-numeric values (e.g. 'status')
    are silently skipped.
    """
    path = Path(db_path)
    empty = pd.DataFrame(
        columns=["timestamp", "solver_name", "system_name", "job_name", "metric_name", "value", "series"]
    )
    if not path.exists():
        return empty

    with sqlite3.connect(path) as conn:
        df = pd.read_sql_query(
            """
            SELECT timestamp, solver_name, system_name, job_name,
                   runtime_seconds, returncode, passed, metrics_json
            FROM runs
            ORDER BY timestamp ASC
            """,
            conn,
        )

    if df.empty:
        return empty

    import json

    rows = []
    for _, run in df.iterrows():
        base = {
            "timestamp": run["timestamp"],
            "solver_name": run["solver_name"],
            "system_name": run["system_name"],
            "job_name": run["job_name"],
        }
        for col in ("runtime_seconds", "returncode"):
            if run[col] is not None:
                rows.append({**base, "metric_name": col, "value": float(run[col])})
        rows.append({**base, "metric_name": "passed", "value": 1.0 if run["passed"] else 0.0})
        if run["metrics_json"]:
            try:
                for k, v in json.loads(run["metrics_json"]).items():
                    try:
                        rows.append({**base, "metric_name": k, "value": float(v)})
                    except (TypeError, ValueError):
                        pass  # skip non-numeric values like status strings
            except json.JSONDecodeError:
                pass

    if not rows:
        return empty

    result = pd.DataFrame(rows)
    result["timestamp"] = pd.to_datetime(result["timestamp"], utc=True)
    result["series"] = result["solver_name"] + " / " + result["system_name"]
    return result


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
