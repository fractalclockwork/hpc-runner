# API (REST + Web Dashboard)

A FastAPI REST API that drives the harness for running jobs and viewing results. The Streamlit UI calls this API over HTTP.

## Requirements

- **Python** 3.10 or newer
- **uv** (https://github.com/astral-sh/uv)
- Workspace sync (includes harness from `src/core`)

## Quickstart

From the project root:

```bash
uv sync --all-extras --dev
uv run uvicorn basic_restapi.fastapi_app:app --reload --port 8000
```

Or: `make api`. Open [http://localhost:8000/docs](http://localhost:8000/docs) for Swagger UI.

## Project structure

```
src/api/
├── pyproject.toml
├── src/basic_restapi/
│   ├── fastapi_app.py   # Routes, request models, DB wiring
│   └── invocations.py   # Background run_jobs threads, cancel, scancel helpers
└── tests/
```

## Notable endpoints

Explore the full list at `/docs`. Highlights:

- `POST /api/run_jobs` — synchronous results, or `"background": true` with optional `"group_by": "solver"` (one invocation per solver) or `"batch"` (single invocation) → **202** + `invocations` list (+ `invocation_id` when a single invocation)
- `GET /api/invocations` — list invocations (`?active_only=true`); `GET /api/invocations/{id}` — status, live SLURM metadata, progress; `GET .../slurm_status` — `squeue`/`sacct` when `RUN_SLURM_E2E=1`; `POST .../cancel` — cancel (subprocess + `scancel` when `HARNESS_ALLOW_SCANCEL=1`, `RUN_SLURM_E2E=1`, or Docker SLURM container env is set)
- `DELETE /api/runs` — body `{"ids": [...]}`
- `GET /api/runs/{id}/slurm_status` — live SLURM state when `RUN_SLURM_E2E=1`
- `GET /api/solver_summaries` — per-solver aggregates for dashboards

Configs load from `configs/` (see workspace root). Database path follows harness defaults (`data/harness.db`).
