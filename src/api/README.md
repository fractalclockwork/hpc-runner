# API (REST + Web Dashboard)

A minimal FastAPI REST API and web dashboard that hooks into the harness core for running jobs and viewing results.

## Requirements

- **Python** 3.10 or newer
- **uv** (https://github.com/astral-sh/uv)
- Workspace sync (includes harness from src/core)

## Quickstart

From the project root:

```bash
# Sync workspace (installs core + api)
uv sync --all-extras --dev

# Run the REST API
uv run uvicorn basic_restapi.fastapi_app:app --reload --port 8000
# Navigate to http://localhost:8000 (redirects to /docs for interactive API docs)
```

Or use the Makefile:

```bash
make api
```

The root path `/` redirects to `/docs` (Swagger UI) so you can explore and test the API interactively.

## Project Structure

```
src/api/
├── pyproject.toml
├── src/basic_restapi/
│   └── fastapi_app.py
└── README.md
```

The API loads configs and solvers from the project root (`configs/`, `solvers/`).
