# hpc-runner

A minimal, reproducible runner harness using `structlog` for logging, `PyYAML` for configuration, and `pytest` for testing.  
This repository is designed for clean packaging, deterministic environments, and easy portability across machines using `uv`.

---

## Project Structure

```
hpc-runner/
├── pyproject.toml
├── src/
│   └── hpc_regression/
│       ├── __init__.py
│       └── runner.py
├── configs/
│   └── runners.yaml
├── tests/
│   └── test_runner.py
├── scripts/
│   └── clean.sh
├── pytest.ini
├── .gitignore
└── README.md
```

---

## Requirements

- Python 3.10 or newer  
- `uv` (https://github.com/astral-sh/uv)  
- POSIX shell for helper scripts

---

## Quickstart (Local, Reproducible)

```bash
# 1. Clean any previous artifacts
scripts/clean.sh

# 2. Create/sync the uv environment
uv sync

# 3. Install the package in editable mode (optional)
uv pip install -e .

# 4. Run tests
uv run python -m pytest
```

---

## Build and Distribute

```bash
scripts/clean.sh
uv sync
uv build
unzip -l dist/*.whl | sed -n '1,200p'
```

Install the wheel on another machine:

```bash
uv pip install dist/*.whl
```

---

## Install and Test on Another Machine

```bash
scripts/clean.sh
uv sync
uv pip install dist/*.whl   # or uv pip install -e .
uv run python -m pytest
```

---

# Structlog Configuration

**Overview**  
The runner uses `structlog.get_logger()` for logging. In production, configure `structlog` once at program start so all modules inherit the same processors and sink.

**Minimal production example**
```python
import logging
import structlog

logging.basicConfig(level="INFO", format="%(message)s")
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)
```

**Test-time behavior**  
- Tests can rely on the default `structlog` configuration; no global setup is required.  
- If you want structured logs captured by pytest, add a small bootstrap in `tests/conftest.py`.

**Recommendations**  
- Configure `structlog` at the application entrypoint, not inside library modules.  
- Use human‑friendly renderers locally and JSON/key‑value renderers in production.  
- Route logs to a stable sink (stdout, file, or aggregator).  
- Avoid reconfiguring `structlog` in multiple places to prevent conflicting global state.

---

## Notes and Recommendations

- **Command safety**: tests use simple commands (`echo`, `python -c`). For real runners, validate commands and avoid running untrusted input.  
- **Config schema**: the YAML format is intentionally minimal. Extend with timeouts, retries, resource tags, or per-runner working directories as needed.  
- **uv environment determinism**: use `uv sync` to ensure the `.venv` matches the lockfile.  
- **CI**: in CI, run `uv sync` then `uv run python -m pytest` to ensure tests run inside the same environment.

---

