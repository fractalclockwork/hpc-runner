# storage/db.py - SQLite storage for runs and metrics
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from ..runner import RunResult


def init_db(path: str | Path) -> None:
    """Create tables if they don't exist."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_name TEXT NOT NULL,
                solver_name TEXT NOT NULL,
                system_name TEXT NOT NULL,
                returncode INTEGER NOT NULL,
                passed INTEGER NOT NULL,
                runtime_seconds REAL NOT NULL,
                timestamp TEXT NOT NULL,
                stdout TEXT,
                stderr TEXT,
                metrics_json TEXT,
                processor TEXT,
                validation_errors TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_runs_solver ON runs(solver_name);
            CREATE INDEX IF NOT EXISTS idx_runs_timestamp ON runs(timestamp);
        """
        )
        # Migration: add processor / validation_errors columns if missing (existing DBs)
        cur = conn.execute("PRAGMA table_info(runs)")
        columns = [row[1] for row in cur.fetchall()]
        if "processor" not in columns:
            conn.execute("ALTER TABLE runs ADD COLUMN processor TEXT")
        if "validation_errors" not in columns:
            conn.execute("ALTER TABLE runs ADD COLUMN validation_errors TEXT")
        conn.commit()


def store_run(db_path: str | Path, result: RunResult) -> int:
    """Store a run result and return the inserted row id."""
    init_db(db_path)
    metrics_json = json.dumps(result.metrics) if result.metrics else None
    validation_errors_json = json.dumps(result.validation_errors or [])
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO runs (
                job_name,
                solver_name,
                system_name,
                returncode,
                passed,
                runtime_seconds,
                timestamp,
                stdout,
                stderr,
                metrics_json,
                processor,
                validation_errors
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.job_name,
                result.solver_name,
                result.system_name,
                result.returncode,
                1 if result.passed else 0,
                result.runtime_seconds,
                result.timestamp,
                result.stdout,
                result.stderr,
                metrics_json,
                result.processor,
                validation_errors_json,
            ),
        )
        row_id = cur.lastrowid or 0
        conn.commit()
    return row_id


def get_runs(
    db_path: str | Path,
    solver: str | None = None,
    processor: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Fetch runs with optional solver and processor filters."""
    init_db(db_path)
    conditions: list[str] = []
    params: list[Any] = []
    if solver:
        conditions.append("solver_name = ?")
        params.append(solver)
    if processor:
        conditions.append("processor = ?")
        params.append(processor)
    where = ("WHERE " + " AND ".join(conditions) + " ") if conditions else ""
    params.extend([limit, offset])
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            f"""SELECT * FROM runs {where}ORDER BY timestamp DESC LIMIT ? OFFSET ?""",
            params,
        ).fetchall()
        return [dict(r) for r in rows]


def get_run_by_id(db_path: str | Path, run_id: int) -> dict[str, Any] | None:
    """Fetch a single run by id."""
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
        return dict(row) if row else None


def get_all_metrics_series(db_path: str | Path, limit: int = 500) -> list[tuple[str, str]]:
    """Discover all (solver_name, metric_name) pairs that have data. For dashboard."""
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            """SELECT solver_name, metrics_json FROM runs
               WHERE metrics_json IS NOT NULL AND metrics_json != '{}'
               ORDER BY timestamp DESC LIMIT ?""",
            (limit,),
        ).fetchall()
    seen: set[tuple[str, str]] = set()
    result: list[tuple[str, str]] = []
    for solver_name, mj in rows:
        try:
            m = json.loads(mj or "{}")
            for k, v in m.items():
                if isinstance(v, (int, float)) and (solver_name, k) not in seen:
                    seen.add((solver_name, k))
                    result.append((solver_name, k))
        except json.JSONDecodeError:
            pass
    return sorted(result, key=lambda x: (x[0], x[1]))


def get_metrics_history(
    db_path: str | Path,
    solver_name: str,
    metric_name: str,
    limit: int = 100,
) -> list[tuple[str, float]]:
    """Get (timestamp, value) history for a metric. For trend visualization."""
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            """SELECT timestamp, metrics_json FROM runs
               WHERE solver_name = ? AND metrics_json IS NOT NULL
               ORDER BY timestamp DESC LIMIT ?""",
            (solver_name, limit),
        ).fetchall()
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
