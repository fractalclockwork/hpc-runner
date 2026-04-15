"""Playwright E2E fixtures — Streamlit URL and process management."""

import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest


# Project root: src/ui/tests/e2e/conftest.py -> parents[4]
PROJECT_ROOT = Path(__file__).resolve().parents[4]
API_PORT = int(os.environ.get("API_PORT", "8000"))
API_BASE = os.environ.get("HPC_API_URL", f"http://127.0.0.1:{API_PORT}").rstrip("/")
STREAMLIT_PORT = int(os.environ.get("STREAMLIT_PORT", "8501"))
STREAMLIT_URL = os.environ.get("STREAMLIT_URL", f"http://localhost:{STREAMLIT_PORT}")
STREAMLIT_START_TIMEOUT = 30
API_START_TIMEOUT = 45


def _wait_for_api(base: str, timeout: float = API_START_TIMEOUT) -> bool:
    """Poll until FastAPI responds on /api/health or /health."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        for path in ("/api/health", "/health"):
            try:
                req = urllib.request.Request(f"{base}{path}")
                with urllib.request.urlopen(req, timeout=2) as r:
                    if r.status == 200:
                        return True
            except (OSError, urllib.error.URLError):
                pass
        time.sleep(0.4)
    return False


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


def _is_loopback_api_url(base: str) -> bool:
    return any(h in base for h in ("localhost", "127.0.0.1", "::1"))


@pytest.fixture(scope="session")
def api_process():
    """Start FastAPI on API_PORT when targeting loopback and nothing answers /api/health.

    Run Matrix and other pages need ``GET /api/solvers`` and ``GET /api/systems``. The UI defaults
    to ``HPC_API_URL`` → ``http://localhost:8000`` (see ``src/ui/api_config.py``).
    """
    if os.environ.get("E2E_SKIP_API") == "1":
        yield
        return
    if not _is_loopback_api_url(API_BASE):
        yield
        return
    if _wait_for_api(API_BASE, timeout=3):
        yield
        return
    proc = subprocess.Popen(
        [
            "uv",
            "run",
            "uvicorn",
            "basic_restapi.fastapi_app:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(API_PORT),
        ],
        cwd=PROJECT_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if not _wait_for_api(API_BASE, timeout=API_START_TIMEOUT):
        proc.kill()
        proc.wait()
        pytest.skip("FastAPI did not start in time for e2e (needed for Run Matrix, etc.)")
    yield
    proc.terminate()
    proc.wait(timeout=10)


@pytest.fixture(scope="session")
def streamlit_process(api_process):
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
