# HPC Regression Platform — MVP

Modular, execution-agnostic HPC regression testing system for the Dow/Berkeley Capstone (Spring 2026).

## Architecture Overview

- **Configuration Layer** — YAML definitions for Resources, Systems, Solvers, Jobs
- **Job Runner** — Execution orchestrator; runs solver scripts as black-box processes
- **Log Parsing** — YAML-defined regex patterns for metric extraction
- **Data Storage** — SQLite for run metadata and metrics
- **Web UI** — REST API (FastAPI) and Streamlit dashboard for running jobs and viewing results

## Quick Start

```bash
# Sync dependencies
uv sync --all-extras --dev

# Run unit tests
make test
# or: uv run pytest src/core/tests -q

# List available jobs
uv run hpc-runner configs --list

# Run all jobs
uv run hpc-runner configs

# Run with custom config dir
uv run hpc-runner /path/to/configs --solvers-dir /path/to/configs/solvers

# Start REST API (programmatic access; root redirects to /docs)
make api
# Open http://localhost:8000 → interactive API docs at /docs

# Or start Streamlit dashboard (interactive UI)
make ui
# Open http://localhost:8501
```

## Docker

Build and run the REST API:

```bash
make docker-build
make docker-run
# Open http://localhost:8000 (redirects to /docs for interactive API)
```

Run tests in container:

```bash
make docker-test
```

Or with docker-compose:

```bash
make docker-up
# or: docker compose -f docker/docker-compose.yml up --build
```

Validate Docker images (build + API health check):

```bash
make docker-validate
```

## Testing

Unit tests cover the major features:

| Test Module | Coverage |
|-------------|----------|
| `test_config.py` | Resource, System, Solver, Job loading; _template skip |
| `test_parser.py` | Metric extraction, validation |
| `test_storage.py` | DB init, store_run, get_runs, get_run_by_id, get_metrics_history |
| `test_runner.py` | End-to-end run, metric extraction from solver output |
| `test_add_solver.py` | --add solver creation, derive_name, add_job |

```bash
make test           # Core unit tests (quiet)
make testv          # Core unit tests (verbose)
make e2e            # Playwright E2E tests (Streamlit UI)
make e2e-docker     # E2E tests in Docker (Streamlit + Playwright)
make docker-validate # Validate Docker images (build + API health check)
```

## Configuration Structure

```
configs/
├── resources/     # CPU/GPU, memory, node definitions
├── systems/       # Resource bundles, env vars
├── jobs/          # Solver+system pairings, success criteria
└── solvers/       # Solver packages
    └── my-solver/
        ├── solver.yaml      # Metadata, entrypoint, parser_config
        ├── run.sh           # Or run.py — executed as black-box
        └── parser_config.yaml   # Optional: regex patterns for metrics
```

## CLI

| Command | Description |
|---------|-------------|
| `hpc-runner [config_dir]` | Run all jobs (config_dir defaults to `configs`) |
| `hpc-runner [config_dir] --list` | List available jobs |
| `hpc-runner [config_dir] --list-runs` | List recent runs from DB (last 20) |
| `hpc-runner [config_dir] --job NAME` | Run specific job(s); repeat `--job` for multiple |
| `hpc-runner [config_dir] --no-store` | Run without persisting to DB |
| `hpc-runner [config_dir] --db PATH` | Override database path |
| `hpc-runner [config_dir] --solvers-dir PATH` | Override solvers directory (default: `configs/solvers`) |
| `hpc-runner --add CMD --system NAME` | Create solver from command, add job, run it |

## REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check (returns `{"status": "ok"}`) |
| `/api/solvers` | GET | List configured solvers |
| `/api/jobs` | GET | List configured jobs |
| `/api/run_jobs` | POST | Run jobs (body: `{"jobs": ["name1"]}`) |
| `/api/runs` | GET | List recent runs (?solver=, ?processor=, ?limit=, ?offset=) |
| `/api/runs/<id>` | GET | Get run details |
| `/api/metrics/<solver>/<metric>` | GET | Metric history for trends |

## Design Principles

- **Execution-Agnostic** — Solver scripts control execution (SLURM, MPI, etc.); platform never calls schedulers directly
- **Modular** — Resources, systems, solvers, jobs defined independently
- **Pluggable** — Add solvers by dropping a folder with `solver.yaml` + run script
