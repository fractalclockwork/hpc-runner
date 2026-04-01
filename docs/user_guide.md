# User Guide

This guide walks you through defining solvers, execution environments, jobs, and metrics for the HPC Regression Platform. It is intended for **solver authors** and **config authors**.

**Prerequisites:** Run `uv sync --all-extras --dev` from the project root. Familiarity with YAML is helpful. For unfamiliar terms, see the [Glossary](glossary.md).

---

## 1. Defining Execution Environments

Execution environments are built from **Resources** (hardware) and **Systems** (resource bundles plus environment variables).

### Resources

Resources define hardware capacity. Add them in `configs/resources/*.yaml` (`.yml` is also supported; `.yaml` is preferred for consistency):

```yaml
resources:
  - name: dev-local
    cpus: 4
    memory_gb: 8
  - name: hpc-node
    cpus: 64
    gpus: 4
    memory_gb: 256
```

| Field       | Description                    |
|-------------|--------------------------------|
| `name`      | Unique identifier              |
| `cpus`      | CPU count (optional)           |
| `gpus`      | GPU count (optional)           |
| `memory_gb` | Memory in GB (optional)        |

You can define multiple resources in one file or split across files. Each resource is referenced by its `name`.

### Systems

Systems bundle one or more resources and add environment variables. Add them in `configs/systems/*.yaml` (`.yml` also supported):

```yaml
systems:
  - name: dev-system
    resources: [dev-local]
    env: {}
  - name: hpc-cluster-01
    resources: [hpc-node]
    env:
      MODULEPATH: /opt/modules
```

| Field         | Description                              |
|---------------|------------------------------------------|
| `name`        | Unique identifier                        |
| `resources`   | List of resource names                   |
| `env`         | Environment variables (key-value)        |
| `constraints` | Optional list of constraints             |

The `env` map is passed to solver scripts when they run. Use it for module paths, API keys, or other runtime configuration.

**Workflow:** Define a resource → reference it in a system → the system is ready for jobs.

---

## 2. Defining Solvers

A solver is a self-contained package with a run script and metadata. See [solver_template.md](solver_template.md) for the full specification.

### Quick Start

1. Copy the template:
   ```bash
   cp -r configs/solvers/_template configs/solvers/my-solver
   ```

2. Edit `configs/solvers/my-solver/solver.yaml`:
   ```yaml
   name: my-solver
   entrypoint: run.sh
   allowed_systems: [dev-system, hpc-cluster-01]
   ```

3. Implement `run.sh` (or `run.py`). The script must be executable. The platform passes system `env` variables and invokes it as a subprocess. Your script controls execution (local, SLURM, MPI, etc.).

4. Add a job that uses your solver (see [Defining Jobs](#4-defining-jobs)).

**SLURM + LAMMPS:** The bundled `lammps-slurm` solver uses `docker/lammps/` (`in.lammps`, `sbatch_lammps.sh`). With Docker it defaults to **`sbatch`**, waits for the job, and collects **`slurm-*.out` / `.err`**. See [slurm_lammps_e2e.md](slurm_lammps_e2e.md).

### Adding a solver from a command

To quickly add a solver that runs a shell command:

```bash
uv run hpc-runner --add "cat /proc/cpuinfo" --system dev-system
```

This creates a minimal solver and job in `configs/solvers/` and `configs/jobs/added.yaml`, then runs the new job. Use `--name` for a custom solver/job name:

```bash
uv run hpc-runner --add "echo hello" --system dev-system --name hello-check --no-store
```

### Key Points

- **Paths** in `solver.yaml` (e.g. `entrypoint`, `parser_config`) are relative to the solver directory.
- **allowed_systems** must list system names that exist in `configs/systems/`. Jobs can only pair your solver with one of these systems.
- **Entrypoint** must exist at the specified path. Use `run.sh` or `run.py`; the platform invokes them via `bash` or `python3`.
- **cwd** (optional): Working directory for the solver. Default `true` = use solver dir; `false` = use entrypoint parent; or a string path.

---

## 3. Extracting Metrics

To extract metrics from solver output, add a `parser_config.yaml` and reference it in `solver.yaml`.

### Parser Config

Create `configs/solvers/my-solver/parser_config.yaml`:

```yaml
patterns:
  - name: mlups
    regex: 'MLUPS:\s*([\d.e+-]+)'
    type: float
  - name: runtime_seconds
    regex: 'runtime_seconds:\s*([\d.]+)'
    type: float
  - name: status
    regex: 'status:\s*(\w+)'
    type: str
```

Each pattern has:

| Field   | Description                                      |
|---------|--------------------------------------------------|
| `name`  | Metric name (used in results and trend charts)   |
| `regex` | Regex with **exactly one capture group** `(...)` |
| `type`  | `str`, `float`, or `int`                         |

The platform concatenates stdout and stderr, then applies each regex. The first match’s capture group is the metric value.

### Solver Output

Your run script must print metrics to stdout or stderr. For example:

```python
print("MLUPS: 2.1e6")
print("runtime_seconds: 38.5")
print("status: success")
```

### Wire Up in solver.yaml

```yaml
name: my-solver
entrypoint: run.py
allowed_systems: [dev-system]
parser_config: parser_config.yaml
metrics:
  - name: mlups
    unit: MLUPS
    min: 0
    required: true
  - name: runtime_seconds
    unit: s
    required: true
```

The `metrics` list is optional; it declares expected metrics and validation ranges (`min`, `max`, `required`).

---

## 4. Defining Jobs

Jobs pair a solver with a system and define success criteria. Add them in `configs/jobs/*.yaml` (`.yml` also supported):

```yaml
jobs:
  - name: echo-test
    solver: echo-solver
    system: dev-system
    parameters: {}
    success_criteria:
      returncode: 0
  - name: python-test
    solver: python-solver
    system: dev-system
    parameters: {}
    success_criteria:
      returncode: 0
```

| Field             | Description                                      |
|-------------------|--------------------------------------------------|
| `name`            | Unique job identifier                            |
| `solver`          | Solver name (must exist in `configs/solvers/`)   |
| `system`          | System name (must exist in `configs/systems/`)   |
| `parameters`      | Optional key-value params (passed to solver)      |
| `success_criteria`| Pass/fail conditions; `returncode` (default 0)   |
| `timeout_seconds` | Optional; job timeout in seconds (default 3600)   |
| `schedule`        | Optional; reserved for future cron/scheduling    |
| `baseline`        | Optional; if true, runs from this job are stored as a baseline |

The solver’s `allowed_systems` must include the job’s `system`. Otherwise the job will be skipped.

---

## 5. Running Jobs

### CLI

From the project root:

```bash
# List available jobs
uv run hpc-runner configs --list

# Run all jobs
uv run hpc-runner configs

# Run specific job(s)
uv run hpc-runner configs --job echo-test --job python-test

# List recent runs from database
uv run hpc-runner configs --list-runs

# Run without persisting to database
uv run hpc-runner configs --no-store
```

Options:

| Option           | Description                                  |
|------------------|----------------------------------------------|
| `config_dir`     | Optional positional; path to config dir (default: `configs`) |
| `--add CMD`      | Create solver from command and run (requires `--system`)   |
| `--system NAME`  | System name (required with `--add`)                         |
| `--name NAME`    | Custom solver/job name (optional with `--add`)               |
| `--job <name>`   | Run only these jobs (repeatable)              |
| `--list`         | List jobs and exit                           |
| `--list-runs`    | List last 20 runs from DB and exit           |
| `--no-store`     | Do not persist results to database           |
| `--solvers-dir`  | Override solvers directory (default: `configs/solvers`)   |
| `--db`           | Override database path (default: data/harness.db) |

You can also pass a custom config directory as the first argument:

```bash
uv run hpc-runner /path/to/configs --solvers-dir /path/to/configs/solvers
```

### Web UI

Two interfaces are available:

**REST API (FastAPI):** `make api` → http://localhost:8000 (root redirects to `/docs` for interactive API documentation). Use for programmatic access or automation.

**Streamlit UI:** `make ui` → http://localhost:8501. Use for interactive running of jobs and viewing results in a browser. The UI talks to the harness **only via the REST API** (HTTP), not embedded Python calls—start **`make api`** first (or point **`HPC_API_URL`** at a reachable API), or pages such as **Run Jobs** and **Run History** cannot load jobs or runs.

Both allow you to:

- Run all jobs
- View recent runs (filter by solver or processor)
- Inspect run details (stdout, stderr, metrics)
- View performance trends (metric history over time)

### Local sleep solver (`local-sleep-60`)

The **`local-sleep-60`** solver runs only on **`dev-system`** and sleeps **60 seconds** by default (override with **`LOCAL_SLEEP_SECONDS`**). Use it to exercise **Run Solvers**, **invocation monitoring**, and **Stop** for **local** subprocess runs (`GET /api/invocations/.../execution_status`, pid/alive) without SLURM.

```bash
uv run hpc-runner configs --solver local-sleep-60
```

For cancel testing, use **`background: true`** so the API returns immediately while the solver keeps running:

```bash
curl -s -X POST http://localhost:8000/api/run_solvers \
  -H 'Content-Type: application/json' \
  -d '{"solvers":[{"name":"local-sleep-60","system":"dev-system"}],"background":true}'
```

Then poll **`GET /api/invocations`** and call **`POST /api/invocations/<id>/cancel`** while the run is active.

Like the Slurm batch templates, the script prints **`HARNESS_SOLVER_WALL_SECONDS`** (high-resolution wall time around the **`sleep`**). The harness prefers that value for **`runtime_seconds`** when present, matching the Slurm path.

### REST API

For automation:

| Endpoint                    | Method | Description                          |
|----------------------------|--------|--------------------------------------|
| `/api/solvers`             | GET    | List solvers (`default_system`, `allowed_systems`) |
| `/api/run_solvers`         | POST   | Run solvers; body `solvers`, optional `batch_name`, `background` — 202 returns one invocation per solver when background |
| `/api/runs`                | GET    | List runs (?solver=, ?processor=, ?limit=) |
| `/api/runs`                | DELETE | Body `{"ids": [1,2]}` — remove stored runs (baseline rows allowed) |
| `/api/runs/<id>`           | GET    | Run detail                           |
| `/api/runs/<id>/slurm_status` | GET | Live `squeue`/`sacct` when `RUN_SLURM_E2E=1` and run has SLURM metadata |
| `/api/invocations`         | GET    | List invocations; `?active_only=true` for queued/running only |
| `/api/invocations/<id>`    | GET    | Status, `batch_name`, live `scheduler_job_ids`, `jobs_total` / `jobs_completed`, and `results` when done |
| `/api/invocations/<id>/slurm_status` | GET | Live `squeue`/`sacct` for SLURM ids captured on this invocation (`RUN_SLURM_E2E=1`) |
| `/api/invocations/<id>/cancel` | POST | Cancel background run (subprocess + best-effort `scancel`; see env vars below) |
| `/api/solver_summaries`   | GET    | Per-solver pass counts and last run info |

**Background cancel (`scancel`):** set **`HARNESS_ALLOW_SCANCEL=1`** for explicit opt-in, or rely on **`RUN_SLURM_E2E=1`** (tests / Docker SLURM E2E), or configure **`DOCKER_SLURM_CONTAINER`** / **`DOCKER_SLURM_SUBMIT_CONTAINER`** so the API can `docker exec` and run `scancel`. Subprocess termination always runs on cancel regardless of those flags.

| `/api/metrics/<solver>/<metric>` | GET | Metric history for trends            |
| `/api/solvers/<solver>/baseline` | GET | Current baseline run for a solver    |
| `/api/runs/<id>/set_baseline` | POST | Set a run as the baseline for its solver |
| `/api/baseline_comparison` | GET | Compare runs to baseline (?solver=, ?limit=) |

---

## 6. Viewing Results

### Run Output

Each run produces a result with:

- `job_name`, `solver_name`, `system_name`
- `returncode`, `passed` (based on success_criteria)
- `runtime_seconds`, `timestamp`
- `metrics` (extracted via parser_config)
- `processor` (e.g. x86_64, aarch64) — detected via `platform.machine()`

CLI output is JSON. Results are stored in `data/harness.db` unless you use `--no-store`. Jobs have a 1-hour (3600s) timeout; jobs exceeding this are marked as failed.

### Dashboard

The Streamlit UI provides:

- **Home:** Welcome text and a **solver monitoring** table (aggregates from stored runs); **Individual Trends** — select solver and metric, line chart
- **Run History:** Batches of runs; filter by solver or processor; expand for stdout, stderr, metrics; **select runs and delete** from the database (with confirm); for SLURM-backed runs, optional **Refresh SLURM status** (needs API env in [slurm_lammps_e2e.md](slurm_lammps_e2e.md))
- **Run Jobs:** Select jobs; **background** run with per-solver or single-batch orchestration; **Active runs** lists invocations from the API (in-memory registry); requires API up
- **Long-Term Trends:** Heatmaps and trend charts over time, with optional baseline-relative views

Set **`HPC_API_URL`** if the Streamlit process must call an API that is not `http://localhost:8000` (e.g. Docker networking).

---

## 7. Troubleshooting

| Issue                    | Check                                                                 |
|--------------------------|-----------------------------------------------------------------------|
| Solver not found         | Solver folder in `configs/solvers/`; not under `_template` or starting with `_`; check `--solvers-dir` |
| System not found for job | System exists in `configs/systems/`; solver’s `allowed_systems` includes it |
| Metrics not extracted    | Regex has exactly one capture group; solver prints to stdout/stderr   |
| Job fails                | Inspect returncode; view stdout/stderr in run detail or DB             |
| Job times out            | Jobs have a 1-hour limit; long runs may need to be split or optimized |
| Entrypoint not found     | Path in `solver.yaml` is relative to solver dir; file exists           |

---

## 8. Quick Reference

**Config layout:**
```
configs/
├── resources/   # Hardware definitions
├── systems/    # Resource bundles + env
├── jobs/       # Solver+system pairings
└── solvers/    # Solver packages
    └── <name>/
        ├── solver.yaml        # Required
        ├── run.sh or run.py   # Required
        └── parser_config.yaml # Optional
```

**See also:** [Glossary](glossary.md) | [Solver Template](solver_template.md) | [Architecture](architecture.md)
