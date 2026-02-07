# hpc-runner

A minimal, reproducible runner harness using **structlog** for logging, **PyYAML** for configuration, and **pytest** for testing. This project is packaged for deterministic environments and easy portability using `uv`.

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

- **Python** 3.10 or newer  
- **uv** (https://github.com/astral-sh/uv)  
- POSIX shell for helper scripts

---

## Quickstart Local Reproducible

> **Where to run**  
> - Use the project root when you want `uv` to treat the repository as a workspace.  
> - Use the `prototypes/hpc-runner` directory when you want to operate only on the runner project. Examples below show both approaches where relevant.

```bash
# From the project root (recommended for workspace aware commands)
# 1. Clean previous artifacts
scripts/clean.sh

# 2. Create or sync the uv environment for the subproject
uv --directory prototypes/hpc-runner sync

# 3. Install the package in editable mode for development
uv --directory prototypes/hpc-runner run python -m pip install -e .

# 4. Run tests inside the project environment
uv --directory prototypes/hpc-runner run python -m pytest

# 5. Invoke the runner using the module form
uv --directory prototypes/hpc-runner run python -m hpc_regression.runner configs/runners.yaml

# Or invoke the console script after installation
uv --directory prototypes/hpc-runner run hpc-runner configs/runners.yaml
```

```bash
# From inside the project directory prototypes/hpc-runner
# 1. Sync environment
uv sync

# 2. Install editable
uv run python -m pip install -e .

# 3. Run tests
uv run python -m pytest

# 4. Run the runner
uv run python -m hpc_regression.runner configs/runners.yaml
```

**Notes**
- If editable installs do not expose `src/` automatically on your system, you can temporarily add the project `src/` to the venv `site-packages` via a `.pth` file. This is a local development workaround and reversible.
- For deterministic runtime in CI or production, prefer installing the built wheel into the environment.

---

## Build and Distribute

```bash
# From the project directory
scripts/clean.sh
uv sync
uv build

# Inspect wheel contents
unzip -l dist/*.whl | sed -n '1,200p'
```

**Install the wheel on another machine**

```bash
# From the target machine or environment
uv --directory prototypes/hpc-runner pip install dist/*.whl
```

---

## Install and Test on Another Machine

```bash
# From the project directory on the other machine
scripts/clean.sh
uv sync
uv --directory prototypes/hpc-runner pip install dist/*.whl   # or uv pip install -e .
uv --directory prototypes/hpc-runner run python -m pytest
```

---

## Structlog Configuration

**Overview**  
The runner uses `structlog.get_logger()` for logging. Configure `structlog` once at the application entrypoint so all modules inherit the same processors and sink.

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
- Tests can rely on the default `structlog` configuration.  
- To capture structured logs in pytest, add a small bootstrap in `tests/conftest.py`.

**Recommendations**  
- Configure `structlog` at the application entrypoint, not inside library modules.  
- Use human friendly renderers locally and JSON renderers in production.  
- Route logs to a stable sink such as stdout or a file.  
- Avoid reconfiguring `structlog` in multiple places.

---

## Notes and Recommendations

- **Command safety**: Example runners use safe commands like `echo` and `python -c`. Validate and sanitize commands before running untrusted input.  
- **Config schema**: The YAML format is intentionally minimal. Consider adding timeouts, retries, resource tags, and per-runner working directories for production use.  
- **uv environment determinism**: Use `uv sync` to ensure the `.venv` matches the lockfile and to reproduce environments across machines.  
- **CI**: In CI, run `uv sync` then `uv run python -m pytest` to ensure tests run inside the same environment.

---

## Troubleshooting

- If `uv` creates a venv without `pip`, run:
```bash
uv --directory prototypes/hpc-runner run python -m ensurepip --upgrade
uv --directory prototypes/hpc-runner run python -m pip install --upgrade pip setuptools wheel
```
- If the console script fails to import the package, reinstall inside the venv so the entrypoint is regenerated:
```bash
uv --directory prototypes/hpc-runner run python -m pip install --force-reinstall -e .
```
- If editable installs do not expose `src/`, a temporary `.pth` pointing to `prototypes/hpc-runner/src` in the venv `site-packages` will make the package importable during development.

---

## Contributing

- Run tests and linters before submitting a PR.  
- Keep changes small and focused.  
- Document any new configuration keys added to `configs/runners.yaml`.

