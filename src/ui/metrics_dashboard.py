"""Metrics dashboard data for the Streamlit UI."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import streamlit as st

from harness import get_db_path

from api_config import API_URL

DB_PATH = get_db_path()

_TREND_QUERY_TTL = 60  # seconds


def _is_plottable_number(v: Any) -> bool:
    """True for int/float values suitable for line charts (excludes bool)."""
    if isinstance(v, bool):
        return False
    return isinstance(v, (int, float))


@st.cache_data(ttl=_TREND_QUERY_TTL)
def get_trend_runs_data(db_path: str) -> pd.DataFrame:
    """Load runs for Long-Term Trends: timestamps, filters, parsed metrics dict.

    Columns: timestamp, solver_name, system_name, job_name, passed, runtime_seconds, metrics
    """
    path = Path(db_path)
    empty_cols = [
        "timestamp",
        "solver_name",
        "system_name",
        "job_name",
        "passed",
        "runtime_seconds",
        "metrics",
    ]
    if not path.exists():
        return pd.DataFrame(columns=empty_cols)

    with sqlite3.connect(path) as conn:
        df = pd.read_sql_query(
            """
            SELECT timestamp, solver_name, system_name, job_name,
                   runtime_seconds, passed, COALESCE(metrics_json, '{}') AS metrics_json
            FROM runs
            ORDER BY timestamp ASC
            """,
            conn,
        )

    if df.empty:
        return pd.DataFrame(columns=empty_cols)

    def _parse_metrics(raw: str) -> dict[str, Any]:
        try:
            m = json.loads(raw or "{}")
            return m if isinstance(m, dict) else {}
        except json.JSONDecodeError:
            return {}

    df["metrics"] = df["metrics_json"].apply(_parse_metrics)
    df = df.drop(columns=["metrics_json"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["passed"] = df["passed"].astype(bool)
    return df


def list_numeric_metric_names(df: pd.DataFrame) -> list[str]:
    """Union of metric keys that have plottable numeric values in any row."""
    names: set[str] = set()
    if df.empty or "metrics" not in df.columns:
        return []
    for m in df["metrics"]:
        if not isinstance(m, dict):
            continue
        for k, v in m.items():
            if _is_plottable_number(v):
                names.add(k)
    return sorted(names)


def build_metric_trend_frame(df: pd.DataFrame, metric_name: str) -> pd.DataFrame:
    """Rows with a numeric value for ``metric_name``; columns for line charting."""
    if df.empty or "metrics" not in df.columns:
        return pd.DataFrame(
            columns=["timestamp", "solver_name", "system_name", "job_name", "passed", "value", "series"]
        )
    rows: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        m = row["metrics"]
        if not isinstance(m, dict) or metric_name not in m:
            continue
        v = m[metric_name]
        if not _is_plottable_number(v):
            continue
        rows.append(
            {
                "timestamp": row["timestamp"],
                "solver_name": row["solver_name"],
                "system_name": row["system_name"],
                "job_name": row["job_name"],
                "passed": row["passed"],
                "value": float(v),
            }
        )
    if not rows:
        return pd.DataFrame(
            columns=["timestamp", "solver_name", "system_name", "job_name", "passed", "value", "series"]
        )
    out = pd.DataFrame(rows)
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    out["series"] = out["solver_name"].astype(str) + " / " + out["system_name"].astype(str)
    return out


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


@st.cache_data(ttl=_TREND_QUERY_TTL)
def get_baseline_values_for_metric(metric_name: str, solver_names: list[str]) -> dict[str, float]:
    """Fetch per-solver baseline metric values from the API."""
    baseline_values: dict[str, float] = {}
    for solver in solver_names:
        try:
            resp = requests.get(API_URL + f"/api/solvers/{solver}/baseline")
        except requests.exceptions.RequestException:
            continue
        if resp.status_code != 200:
            continue
        try:
            data = resp.json()
        except Exception:
            continue
        metrics = data.get("metrics") or {}
        val = metrics.get(metric_name)
        if isinstance(val, (int, float)):
            baseline_values[solver] = float(val)
    return baseline_values


@st.cache_data(ttl=_TREND_QUERY_TTL)
def get_solver_baseline_metrics(solver_name: str) -> dict[str, float]:
    """Fetch numeric baseline metrics for a solver from the API."""
    try:
        resp = requests.get(API_URL + f"/api/solvers/{solver_name}/baseline")
    except requests.exceptions.RequestException:
        return {}
    if resp.status_code != 200:
        return {}
    try:
        data = resp.json()
    except Exception:
        return {}
    metrics = data.get("metrics") or {}
    return {
        k: float(v)
        for k, v in metrics.items()
        if isinstance(v, (int, float)) and float(v) > 0
    }


@st.cache_data(ttl=_TREND_QUERY_TTL)
def get_baseline_comparison(
    solver_name: str | None = None, limit: int = 100
) -> list[dict[str, Any]]:
    """Fetch baseline comparison payload from the API."""
    params: dict[str, Any] = {"limit": limit}
    if solver_name:
        params["solver"] = solver_name
    try:
        response = requests.get(API_URL + "/api/baseline_comparison", params=params)
        data = response.json()
    except requests.exceptions.RequestException:
        return []
    except Exception:
        return []
    return data if isinstance(data, list) else []
