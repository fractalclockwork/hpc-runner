# src/hpc_regression/runner.py
from __future__ import annotations
import subprocess
import yaml
import structlog
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime

logger = structlog.get_logger()

@dataclass
class RunnerSpec:
    name: str
    command: List[str]
    env: Dict[str, str] | None = None
    cwd: str | None = None

def load_config(path: str) -> List[RunnerSpec]:
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    runners = []
    for item in data.get("runners", []):
        runners.append(
            RunnerSpec(
                name=item.get("name", "unnamed"),
                command=item["command"],
                env=item.get("env"),
                cwd=item.get("cwd"),
            )
        )
    return runners

def run_runner(spec: RunnerSpec, capture_output: bool = True, check: bool = False) -> Dict[str, Any]:
    logger.info("runner.start", name=spec.name, command=spec.command, cwd=spec.cwd)
    start_time = datetime.utcnow()
    result = subprocess.run(
        spec.command,
        env={**(spec.env or {})},
        cwd=spec.cwd,
        capture_output=capture_output,
        text=True,
        check=check,
    )
    logger.info(
        "runner.finish",
        name=spec.name,
        returncode=result.returncode,
        stdout=(result.stdout or "").strip(),
        stderr=(result.stderr or "").strip(),
    )
    end_time = datetime.utcnow()
    runtime = (end_time - start_time).total_seconds()
    return {
        "name": spec.name,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        # putting in the timestamp so we get them from runners
        "runtime": runtime,
        "timestamp": datetime.utcnow().isoformat(),
    }

def run_from_config(path: str) -> List[Dict[str, Any]]:
    specs = load_config(path)
    results = []
    for s in specs:
        results.append(run_runner(s))
    return results

def main(argv=None):
    import sys, json, argparse

    parser = argparse.ArgumentParser(
        description="Run commands defined in a YAML config file."
    )
    parser.add_argument(
        "config",
        help="Path to the YAML configuration file defining runners."
    )

    args = parser.parse_args(argv)

    results = run_from_config(args.config)
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

