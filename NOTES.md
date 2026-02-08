```markdown
# DOW‑1‑26 Workspace

This repository contains a multi‑project Python workspace managed with `uv`. It includes:

- `hpc-regression`: a minimal runner harness using `structlog`
- `basic_restapi`: a small Flask API for triggering the harness
- `gantt-tool`: a utility for generating Gantt charts from run data

The workspace is fully reproducible and requires no manual virtual environment management.

---

## Quick Start

### 1. Install prerequisites

You need:

- Python 3.10 or newer
- uv (fast Python package manager)

Install uv:

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

No need for pip, virtualenv, conda, or poetry.

---

### 2. Clone the repository

```
git clone <repo-url>
cd DOW-1-26
```

All commands below assume you are in the workspace root (the directory containing `pyproject.toml`).

---

### 3. Sync the workspace

This creates `.venv/` and installs all project and development dependencies.

```
uv sync --all-extras --dev
```

uv will:

- create a virtual environment
- install all workspace members
- install all runtime dependencies
- install dev tools (pytest, ruff)
- generate a lockfile for reproducibility

You do not need to activate `.venv` manually.

---

### 4. Run the test harness

```
uv run pytest prototypes/hpc-runner/tests
```

---

### 5. Run the runner CLI

```
uv run hpc-runner --help
```

Or run the module directly:

```
uv run python -m hpc_regression.runner
```

---

### 6. Run the REST API

```
uv run python -m basic_restapi.app
```

Replace `app` with the actual module name if needed.

---

### 7. Run the Gantt tool

```
uv run python -m gantt_tool
```

---

## Adding Dependencies

Use uv’s native workflow:

```
uv add <package-name>
```

Examples:

```
uv add requests
uv add rich
```

uv updates the lockfile, workspace, and venv automatically.

---

## Inspecting the Environment

List installed packages:

```
uv pip list
```

Inspect dependency resolution:

```
uv tree
```

---

## Troubleshooting

### ModuleNotFoundError when using uv run

Ensure you are in the workspace root:

```
pwd
```

It should end with:

```
.../DOW-1-26
```

### pip not found

Expected. uv environments do not include pip by default.  
Use `uv pip` instead.

### Rebuild everything cleanly

```
rm -rf .venv uv.lock
uv sync --all-extras --dev
```

---

## Repository Structure

```
DOW-1-26/
  pyproject.toml
  prototypes/
    hpc-runner/
      pyproject.toml
      ...
    basic_restapi/
      pyproject.toml
      ...
  utils/
    gantt-tool/
      pyproject.toml
      ...
```

---

## Notes

- uv manages the virtual environment; do not manually activate `.venv`.
- pip is not required; uv provides its own installer and resolver.
- All commands should be run from the workspace root.
```

