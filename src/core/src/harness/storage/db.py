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
                validation_errors TEXT,
                is_baseline INTEGER NOT NULL DEFAULT 0,
                job_batch_uuid TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_runs_solver ON runs(solver_name);
            CREATE INDEX IF NOT EXISTS idx_job_batch_uuid_solver ON runs(job_batch_uuid);
            CREATE INDEX IF NOT EXISTS idx_runs_timestamp ON runs(timestamp);
        """
        )
        # Migration: add processor / validation_errors / is_baseline columns if missing (existing DBs)
        cur = conn.execute("PRAGMA table_info(runs)")
        columns = [row[1] for row in cur.fetchall()]
        if "processor" not in columns:
            conn.execute("ALTER TABLE runs ADD COLUMN processor TEXT")
        if "validation_errors" not in columns:
            conn.execute("ALTER TABLE runs ADD COLUMN validation_errors TEXT")
        if "is_baseline" not in columns:
            conn.execute("ALTER TABLE runs ADD COLUMN is_baseline INTEGER NOT NULL DEFAULT 0")
        conn.commit()


def store_run(db_path: str | Path, result: RunResult) -> int:
    """Store a run result and return the inserted row id."""
    init_db(db_path)
    metrics_json = json.dumps(result.metrics) if result.metrics else None
    validation_errors_json = json.dumps(result.validation_errors or [])
    is_baseline = 1 if getattr(result, "baseline", False) else 0
    with sqlite3.connect(db_path) as conn:
        # If this run is a baseline (e.g. job.baseline: true), it replaces any existing
        # baseline for the same solver so we always have one active baseline per solver.
        if is_baseline:
            conn.execute(
                "UPDATE runs SET is_baseline = 0 WHERE solver_name = ?",
                (result.solver_name,),
            )
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
                validation_errors,
                job_batch_uuid,
                is_baseline
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                result.job_batch_uuid,
                is_baseline,
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


def _run_to_response(r: dict[str, Any]) -> dict[str, Any]:
    """Decode metrics_json and validation_errors for a run row."""
    out = dict(r)
    if out.get("metrics_json"):
        try:
            out["metrics"] = json.loads(out["metrics_json"])
        except json.JSONDecodeError:
            out["metrics"] = {}
    else:
        out["metrics"] = {}
    if out.get("validation_errors") is not None:
        try:
            out["validation_errors"] = json.loads(out["validation_errors"])
        except json.JSONDecodeError:
            out["validation_errors"] = []
    else:
        out["validation_errors"] = []
    out["passed"] = bool(out.get("passed"))
    out["is_baseline"] = bool(out.get("is_baseline", False))
    return out


def get_baseline_run(db_path: str | Path, solver_name: str) -> dict[str, Any] | None:
    """Return the run marked as baseline for the given solver (one per solver), or None."""
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """SELECT * FROM runs
               WHERE solver_name = ? AND is_baseline = 1
               ORDER BY timestamp DESC LIMIT 1""",
            (solver_name,),
        ).fetchone()
    if row is None:
        return None
    return _run_to_response(dict(row))


def set_baseline_run(db_path: str | Path, run_id: int) -> dict[str, Any] | None:
    """
    Set a specific run as the baseline for its solver.
    Clears is_baseline on all other runs of the same solver, then sets this run to baseline.
    Returns the updated run dict, or None if run_id not found.
    """
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT id, solver_name FROM runs WHERE id = ?", (run_id,)).fetchone()
        if row is None:
            return None
        solver_name = row[1]
        conn.execute("UPDATE runs SET is_baseline = 0 WHERE solver_name = ?", (solver_name,))
        conn.execute("UPDATE runs SET is_baseline = 1 WHERE id = ?", (run_id,))
        conn.commit()
        updated = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
    return _run_to_response(dict(updated))


def get_baseline_comparison(
    db_path: str | Path,
    solver_name: str | None = None,
    limit_per_solver: int = 50,
) -> list[dict[str, Any]]:
    """
    For each solver (or the given solver), return baseline run and other runs with
    per-metric comparison. Each item: solver_name, baseline_run, other_runs,
    comparisons: list of {run_id, job_name, timestamp, metrics, vs_baseline: {metric: {baseline, value, delta, delta_pct}}}.
    """
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        if solver_name:
            solvers_rows = conn.execute(
                "SELECT DISTINCT solver_name FROM runs WHERE solver_name = ?",
                (solver_name,),
            ).fetchall()
        else:
            solvers_rows = conn.execute("SELECT DISTINCT solver_name FROM runs").fetchall()
    solvers_list = [r[0] for r in solvers_rows]
    result: list[dict[str, Any]] = []
    for sname in solvers_list:
        baseline = get_baseline_run(db_path, sname)
        if not baseline:
            result.append({
                "solver_name": sname,
                "baseline_run": None,
                "other_runs": [],
                "comparisons": [],
            })
            continue
        baseline_metrics = baseline.get("metrics") or {}
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            others = conn.execute(
                """SELECT * FROM runs
                   WHERE solver_name = ? AND (is_baseline = 0 OR id != ?)
                   ORDER BY timestamp DESC LIMIT ?""",
                (sname, baseline["id"], limit_per_solver),
            ).fetchall()
        comparisons: list[dict[str, Any]] = []
        other_runs_decoded: list[dict[str, Any]] = []
        for row in others:
            r = _run_to_response(dict(row))
            other_runs_decoded.append(r)
            vs: dict[str, dict[str, Any]] = {}
            for k, base_val in baseline_metrics.items():
                if not isinstance(base_val, (int, float)):
                    continue
                val = r["metrics"].get(k)
                if val is None or not isinstance(val, (int, float)):
                    continue
                base_f = float(base_val)
                val_f = float(val)
                delta = val_f - base_f
                delta_pct = (100.0 * delta / base_f) if base_f != 0 else None
                vs[k] = {"baseline": base_f, "value": val_f, "delta": delta, "delta_pct": delta_pct}
            comparisons.append({
                "run_id": r["id"],
                "job_name": r["job_name"],
                "timestamp": r["timestamp"],
                "metrics": r["metrics"],
                "vs_baseline": vs,
            })
        result.append({
            "solver_name": sname,
            "baseline_run": baseline,
            "other_runs": other_runs_decoded,
            "comparisons": comparisons,
        })
    return result

def get_job_batch_uuids(db_path: str | Path) -> list[Any] | None:
    """Return list of job_batch_uuids"""
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """SELECT DISTINCT job_batch_uuid FROM runs""",
        ).fetchall()
    if rows is None:
        return None
    return [row['job_batch_uuid'] for row in rows if row['job_batch_uuid'] != ""]
