# HPC Regression Testing Platform — MVP

Modular, execution-agnostic HPC regression testing system for the Dow/Berkeley Capstone (Spring 2026).

## Architecture Overview

- **Configuration Layer** — TOML/YAML definitions for Resources, Systems, Solvers, Jobs
- **Job Runner** — Execution orchestrator; runs solver scripts as black-box processes
- **Log Parsing** — YAML-defined regex patterns for metric extraction
- **Data Storage** — SQLite for run metadata and metrics
- **Dashboard** — Web UI for running jobs and viewing results

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

# Run with custom config dir and solvers
uv run hpc-runner /path/to/configs --solvers-dir /path/to/solvers

# Start Web UI
uv run basic-restapi
# Open http://localhost:8000
```

## Docker

Build and run the REST API:

```bash
make docker-build
make docker-run
# Open http://localhost:8000
```

Run tests in container:

```bash
make docker-test
```

Or with docker-compose:

```bash
docker compose up --build
```

## Testing

Unit tests cover the major features:

| Test Module | Coverage |
|-------------|----------|
| `test_config.py` | Resource, System, Solver, Job loading; _template skip |
| `test_parser.py` | Metric extraction, validation |
| `test_storage.py` | DB init, store_run, get_runs, get_run_by_id, get_metrics_history |
| `test_runner.py` | End-to-end run, metric extraction from solver output |

```bash
make test      # Quiet
make testv     # Verbose
```

## Configuration Structure

```
configs/
├── resources/     # CPU/GPU, memory, node definitions
├── systems/       # Resource bundles, env vars
├── jobs/          # Solver+system pairings, success criteria

solvers/
├── my-solver/
│   ├── solver.yaml      # Metadata, entrypoint, parser_config
│   ├── run.sh           # Or run.py — executed as black-box
│   └── parser_config.yaml   # Optional: regex patterns for metrics
```

## CLI

| Command | Description |
|---------|-------------|
| `hpc-runner configs` | Run all jobs |
| `hpc-runner configs --list` | List available jobs |
| `hpc-runner configs --list-runs` | List recent runs from DB |
| `hpc-runner configs --job echo-test` | Run specific job(s) |
| `hpc-runner configs --no-store` | Run without persisting to DB |

## REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/solvers` | GET | List configured solvers |
| `/api/jobs` | GET | List configured jobs |
| `/api/run_jobs` | POST | Run jobs (body: `{"jobs": ["name1"]}`) |
| `/api/runs` | GET | List recent runs (query: `?solver=`, `?limit=`) |
| `/api/runs/<id>` | GET | Get run details |
| `/api/metrics/<solver>/<metric>` | GET | Metric history for trends |

## Design Principles

- **Execution-Agnostic** — Solver scripts control execution (SLURM, MPI, etc.); platform never calls schedulers directly
- **Modular** — Resources, systems, solvers, jobs defined independently
- **Pluggable** — Add solvers by dropping a folder with `solver.yaml` + run script
