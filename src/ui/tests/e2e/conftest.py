"""Playwright E2E fixtures — Streamlit URL and process management."""

import os
import subprocess
import time
import urllib.request
from pathlib import Path

import pytest


# Project root: src/ui/tests/e2e/conftest.py -> parents[4]
PROJECT_ROOT = Path(__file__).resolve().parents[4]
STREAMLIT_PORT = int(os.environ.get("STREAMLIT_PORT", "8501"))
STREAMLIT_URL = os.environ.get("STREAMLIT_URL", f"http://localhost:{STREAMLIT_PORT}")
STREAMLIT_START_TIMEOUT = 30


def _wait_for_streamlit(url: str, timeout: float = STREAMLIT_START_TIMEOUT) -> bool:
    """Poll until Streamlit responds or timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=2) as r:
                if r.status == 200:
                    return True
        except (OSError, urllib.error.URLError):
            pass
        time.sleep(0.5)
    return False


@pytest.fixture(scope="session")
def streamlit_process():
    """Start Streamlit in background when running locally (STREAMLIT_URL not set to remote)."""
    # If URL points to a different host (e.g. streamlit:8501 in Docker), app is already running
    # Or if STREAMLIT_ALREADY_RUNNING=1 (e.g. Streamlit running in Docker on localhost:8501)
    if os.environ.get("STREAMLIT_ALREADY_RUNNING") == "1":
        if not _wait_for_streamlit(STREAMLIT_URL):
            pytest.skip("Streamlit at STREAMLIT_URL did not respond in time")
        yield
        return
    if "localhost" not in STREAMLIT_URL and "127.0.0.1" not in STREAMLIT_URL:
        yield
        return
    proc = subprocess.Popen(
        ["uv", "run", "streamlit", "run", "src/ui/app.py", "--server.port", str(STREAMLIT_PORT), "--server.headless", "true"],
        cwd=PROJECT_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if not _wait_for_streamlit(STREAMLIT_URL):
        proc.kill()
        proc.wait()
        pytest.skip("Streamlit did not start in time")
    yield
    proc.terminate()
    proc.wait(timeout=5)


@pytest.fixture(scope="session")
def streamlit_url(streamlit_process):
    """URL of the running Streamlit app."""
    return STREAMLIT_URL
