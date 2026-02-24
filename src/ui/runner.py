"""Test execution logic — separated from UI concerns."""

import subprocess
from dataclasses import dataclass
from pathlib import Path

# Resolve the project root relative to this file's location:
#   src/ui/runner.py  ->  parents[0] = src/ui
#                     ->  parents[1] = src
#                     ->  parents[2] = project root (DOW-1-26)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Exact test command used by the repository (mirrors `make test`)
TEST_COMMAND = ["uv", "run", "pytest", "src/core/tests", "-q"]


@dataclass
class TestResult:
    returncode: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        return self.returncode == 0


def run_tests() -> TestResult:
    """Execute the project test suite and return captured output.

    Runs the same command as `make test` from the project root.
    Does not modify how the tests themselves work.
    """
    proc = subprocess.run(
        TEST_COMMAND,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    return TestResult(
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )
