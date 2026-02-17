# cli.py - CLI entrypoint for harness
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import load_all, load_jobs
from .runner import run_jobs
from .storage import init_db, store_run, get_runs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Harness - execution-agnostic job runner"
    )
    parser.add_argument(
        "config_dir",
        nargs="?",
        default="configs",
        help="Path to configuration directory (resources, systems, solvers, jobs)",
    )
    parser.add_argument(
        "--solvers-dir",
        default=None,
        help="Path to solvers directory (default: config_dir/solvers or config_dir/../solvers)",
    )
    parser.add_argument(
        "--job",
        action="append",
        dest="jobs",
        help="Run only these job names (can repeat)",
    )
    parser.add_argument(
        "--db",
        default="data/harness.db",
        help="SQLite database path for storing results",
    )
    parser.add_argument(
        "--no-store",
        action="store_true",
        help="Do not store results in database",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available jobs and exit",
    )
    parser.add_argument(
        "--list-runs",
        action="store_true",
        help="List recent runs from database and exit",
    )

    args = parser.parse_args(argv)
    config_dir = Path(args.config_dir)

    # Resolve solvers directory
    solvers_root = Path(args.solvers_dir) if args.solvers_dir else None
    if solvers_root is None and (config_dir.parent / "solvers").exists():
        solvers_root = config_dir.parent / "solvers"

    resources, systems, solvers, jobs = load_all(config_dir, solvers_root)

    if args.list:
        print("Available jobs:")
        for j in jobs.values():
            print(f"  - {j.name} (solver={j.solver}, system={j.system})")
        return 0

    if args.list_runs:
        init_db(args.db)
        runs = get_runs(args.db, limit=20)
        for r in runs:
            status = "PASS" if r.get("passed") else "FAIL"
            proc = r.get("processor") or "-"
            print(f"  {r['id']}: {r['job_name']} | {status} | {proc} | {r['timestamp']}")
        return 0

    job_list = list(jobs.values())
    if args.jobs:
        job_list = [j for j in job_list if j.name in args.jobs]

    if not job_list:
        print("No jobs to run.")
        return 1

    results = run_jobs(job_list, solvers, systems)

    if not args.no_store:
        init_db(args.db)
        for r in results:
            store_run(args.db, r)

    # Output as JSON for CLI/API consumption
    output = [
        {
            "job_name": r.job_name,
            "solver_name": r.solver_name,
            "system_name": r.system_name,
            "returncode": r.returncode,
            "passed": r.passed,
            "runtime_seconds": r.runtime_seconds,
            "timestamp": r.timestamp,
            "metrics": r.metrics,
            "processor": r.processor,
        }
        for r in results
    ]
    print(json.dumps(output, indent=2))
    return 0 if all(r.passed for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
