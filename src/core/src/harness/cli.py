# cli.py - CLI entrypoint for harness
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .add_solver import add_solver, add_job
from .config import ConfigError, load_all, load_resources, load_systems
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
        help="Path to solvers directory (default: config_dir/solvers)",
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
    parser.add_argument(
        "--add",
        metavar="CMD",
        help="Create a solver from a shell command and run it",
    )
    parser.add_argument(
        "--system",
        metavar="NAME",
        help="System name (required with --add); e.g. dev-system",
    )
    parser.add_argument(
        "--name",
        metavar="NAME",
        help="Custom solver/job name (optional with --add)",
    )

    args = parser.parse_args(argv)
    config_dir = Path(args.config_dir).resolve()

    # Resolve solvers directory (None = use config_dir/solvers)
    solvers_root = Path(args.solvers_dir).resolve() if args.solvers_dir else None
    if solvers_root is None:
        solvers_root = config_dir / "solvers"

    # --add: create solver and job, then run
    if args.add:
        if not args.system:
            print("--system is required when using --add", file=sys.stderr)
            return 1
        resources = load_resources(config_dir)
        systems = load_systems(config_dir)
        if args.system not in systems:
            print(
                f"System '{args.system}' not found. Available: {sorted(systems.keys())}",
                file=sys.stderr,
            )
            return 1
        try:
            solver_name, job_name = add_solver(
                config_dir, solvers_root, args.add, args.system, args.name
            )
            add_job(config_dir, solver_name, args.system, job_name)
        except ValueError as e:
            print(str(e), file=sys.stderr)
            return 1
        # Reload and run the new job
        try:
            resources, systems, solvers, jobs = load_all(config_dir, solvers_root)
        except ConfigError as e:
            print(f"Configuration error: {e}", file=sys.stderr)
            return 1
        if job_name not in jobs:
            print(f"Job '{job_name}' not found after add", file=sys.stderr)
            return 1
        job_list = [jobs[job_name]]
        results = run_jobs(job_list, solvers, systems)
        if not args.no_store:
            init_db(args.db)
            for r in results:
                store_run(args.db, r)
        output = []
        for r in results:
            item = {
                "job_name": r.job_name,
                "solver_name": r.solver_name,
                "system_name": r.system_name,
                "returncode": r.returncode,
                "passed": r.passed,
                "runtime_seconds": r.runtime_seconds,
                "timestamp": r.timestamp,
                "metrics": r.metrics,
                "processor": r.processor,
                "validation_errors": r.validation_errors,
            }
            output.append(item)
        print(json.dumps(output, indent=2))
        return 0 if all(r.passed for r in results) else 1

    try:
        resources, systems, solvers, jobs = load_all(config_dir, solvers_root)
    except ConfigError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1

    if args.list:
        print("Available jobs:")
        for j in jobs.values():
            print(f"  - {j.name} (solver={j.solver}, system={j.system})")
        return 0

    if args.list_runs:
        init_db(args.db)
        runs = get_runs(args.db, limit=20)
        for r in runs:
            if r.get("passed"):
                status = "PASS"
            elif r.get("validation_errors"):
                status = "VALIDATION_ERROR"
            else:
                status = "FAIL"
            proc = r.get("processor") or "-"
            err_info = ""
            # if validation errors are present, show them
            try:
                validation_errors = json.loads(r.get("validation_errors") or "[]")
                if validation_errors:
                    n = len(validation_errors)
                    err_info = f" | {n} validation error{'s' if n != 1 else ''}"
            except (json.JSONDecodeError, TypeError):
                pass
            print(f"  {r['id']}: {r['job_name']} | {status} | {proc} | {r['timestamp']}{err_info}")
        return 0

    job_list = list(jobs.values())
    if args.jobs:
        job_list = [j for j in job_list if j.name in args.jobs]

    if not job_list:
        if args.jobs:
            available = sorted(j.name for j in jobs.values())
            print(
                f"No matching jobs. Requested: {args.jobs}. Available: {available}",
                file=sys.stderr,
            )
        else:
            print(
                f"No jobs to run. Config dir: {config_dir}. "
                "Check configs/jobs/*.yaml and that jobs reference valid solvers/systems.",
                file=sys.stderr,
            )
        return 1

    results = run_jobs(job_list, solvers, systems)

    if not args.no_store:
        init_db(args.db)
        for r in results:
            store_run(args.db, r)

    # Output as JSON for CLI/API consumption
    output = []
    for r in results:
        item = {
            "job_name": r.job_name,
            "solver_name": r.solver_name,
            "system_name": r.system_name,
            "returncode": r.returncode,
            "passed": r.passed,
            "runtime_seconds": r.runtime_seconds,
            "timestamp": r.timestamp,
            "metrics": r.metrics,
            "processor": r.processor,
            "validation_errors": r.validation_errors,
        }
        output.append(item)
    print(json.dumps(output, indent=2))
    return 0 if all(r.passed for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
