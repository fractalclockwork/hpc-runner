# cli.py - CLI entrypoint for Test Runner
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import load_all, load_tests
from .runner import run_tests
from .storage import init_db, store_run, get_runs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="HPC Regression Test Runner - execution-agnostic test execution"
    )
    parser.add_argument(
        "config_dir",
        nargs="?",
        default="configs",
        help="Path to configuration directory (resources, systems, solvers, tests)",
    )
    parser.add_argument(
        "--solvers-dir",
        default=None,
        help="Path to solvers directory (default: config_dir/solvers or config_dir/../solvers)",
    )
    parser.add_argument(
        "--test",
        action="append",
        dest="tests",
        help="Run only these test names (can repeat)",
    )
    parser.add_argument(
        "--db",
        default="hpc_regression.db",
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
        help="List available tests and exit",
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

    resources, systems, solvers, tests = load_all(config_dir, solvers_root)

    if args.list:
        print("Available tests:")
        for t in tests.values():
            print(f"  - {t.name} (solver={t.solver}, system={t.system})")
        return 0

    if args.list_runs:
        init_db(args.db)
        runs = get_runs(args.db, limit=20)
        for r in runs:
            status = "PASS" if r.get("passed") else "FAIL"
            print(f"  {r['id']}: {r['test_name']} | {status} | {r['timestamp']}")
        return 0

    test_list = list(tests.values())
    if args.tests:
        test_list = [t for t in test_list if t.name in args.tests]

    if not test_list:
        print("No tests to run.")
        return 1

    results = run_tests(test_list, solvers, systems)

    if not args.no_store:
        init_db(args.db)
        for r in results:
            store_run(args.db, r)

    # Output as JSON for CLI/API consumption
    output = [
        {
            "test_name": r.test_name,
            "solver_name": r.solver_name,
            "system_name": r.system_name,
            "returncode": r.returncode,
            "passed": r.passed,
            "runtime_seconds": r.runtime_seconds,
            "timestamp": r.timestamp,
            "metrics": r.metrics,
        }
        for r in results
    ]
    print(json.dumps(output, indent=2))
    return 0 if all(r.passed for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
