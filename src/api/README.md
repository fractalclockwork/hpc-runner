# API (REST + Web Dashboard)

A minimal REST API and web dashboard that hooks into the harness core for running jobs and viewing results.

## Requirements

- **Python** 3.10 or newer
- **uv** (https://github.com/astral-sh/uv)
- Workspace sync (includes harness from src/core)

## Quickstart

From the project root:

```bash
# Sync workspace (installs core + api)
uv sync --all-extras --dev

# Run the API
uv run flask --app basic_restapi.app run --debug
# Navigate to http://localhost:8000
```

Or use the Makefile:

```bash
make api
```

## Project Structure

```
src/api/
├── pyproject.toml
├── src/basic_restapi/
│   └── app.py
├── templates/
├── static/
└── README.md
```

The API loads configs and solvers from the project root (`configs/`, `solvers/`).
