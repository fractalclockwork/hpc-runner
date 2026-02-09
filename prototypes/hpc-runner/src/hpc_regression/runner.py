# src/hpc_regression/runner.py
from __future__ import annotations
import subprocess
import yaml
import structlog
import json
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime, timezone
from .log_parser import parse_structlog_status

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
    start_time = datetime.now(timezone.utc)
    result = subprocess.run(
        spec.command,
        env={**(spec.env or {})},
        cwd=spec.cwd,
        capture_output=capture_output,
        text=True,
        check=check,
    )
    
    # Build a structlog-like JSON line to pass to the parser
    # okay i think this can be better thought out bc this is just packaging
    # the structlog early prior to the return statement but we also return
    # the log after compiling soooo this seems it can be re-thought
    structlog_line = json.dumps({
        "event": "runner.finish",
        "name": spec.name,
        "returncode": result.returncode,
    })
    
    # Use parse_structlog_status to derive status from the structlog line
    parsed_status = parse_structlog_status(structlog_line)
    
    logger.info(
        "runner.finish",
        name=spec.name,
        returncode=result.returncode,
        parsed_status=parsed_status,
        stdout=(result.stdout or "").strip(),
        stderr=(result.stderr or "").strip(),
    )
    end_time = datetime.now(timezone.utc)
    runtime = (end_time - start_time).total_seconds()
    return {
        "name": spec.name,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        # changed status to parsed_status
        "parsed_status": parsed_status,
        # putting in the timestamp so we get them from runners
        "runtime": runtime,
        "timestamp": datetime.now(timezone.utc).isoformat(),
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

