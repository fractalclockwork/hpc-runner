# storage/db.py - SQLite storage for runs and metrics
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from ..runner import RunResult


def init_db(path: str | Path) -> None:
    """Create tables if they don't exist."""
    conn = sqlite3.connect(path)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_name TEXT NOT NULL,
            solver_name TEXT NOT NULL,
            system_name TEXT NOT NULL,
            returncode INTEGER NOT NULL,
            passed INTEGER NOT NULL,
            runtime_seconds REAL NOT NULL,
            timestamp TEXT NOT NULL,
            stdout TEXT,
            stderr TEXT,
            metrics_json TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_runs_solver ON runs(solver_name);
        CREATE INDEX IF NOT EXISTS idx_runs_timestamp ON runs(timestamp);
    """)
    conn.commit()
    conn.close()


def store_run(db_path: str | Path, result: RunResult) -> int:
    """Store a run result and return the inserted row id."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    metrics_json = json.dumps(result.metrics) if result.metrics else None
    cur = conn.execute(
        """INSERT INTO runs (
            test_name, solver_name, system_name, returncode, passed,
            runtime_seconds, timestamp, stdout, stderr, metrics_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            result.test_name,
            result.solver_name,
            result.system_name,
            result.returncode,
            1 if result.passed else 0,
            result.runtime_seconds,
            result.timestamp,
            result.stdout,
            result.stderr,
            metrics_json,
        ),
    )
    row_id = cur.lastrowid or 0
    conn.commit()
    conn.close()
    return row_id


def get_runs(
    db_path: str | Path,
    solver: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Fetch runs with optional solver filter."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    if solver:
        rows = conn.execute(
            """SELECT * FROM runs WHERE solver_name = ?
               ORDER BY timestamp DESC LIMIT ? OFFSET ?""",
            (solver, limit, offset),
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT * FROM runs ORDER BY timestamp DESC LIMIT ? OFFSET ?""",
            (limit, offset),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_run_by_id(db_path: str | Path, run_id: int) -> dict[str, Any] | None:
    """Fetch a single run by id."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_metrics_history(
    db_path: str | Path,
    solver_name: str,
    metric_name: str,
    limit: int = 100,
) -> list[tuple[str, float]]:
    """Get (timestamp, value) history for a metric. For trend visualization."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        """SELECT timestamp, metrics_json FROM runs
           WHERE solver_name = ? AND metrics_json IS NOT NULL
           ORDER BY timestamp DESC LIMIT ?""",
        (solver_name, limit),
    ).fetchall()
    conn.close()
    result: list[tuple[str, float]] = []
    for ts, mj in rows:
        try:
            m = json.loads(mj or "{}")
            if metric_name in m and isinstance(m[metric_name], (int, float)):
                result.append((ts, float(m[metric_name])))
        except json.JSONDecodeError:
            pass
    result.reverse()
    return result
