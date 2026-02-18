# User Guide

This guide walks you through defining solvers, execution environments, jobs, and metrics for the HPC Regression Testing Platform. It is intended for **solver authors** and **config authors**.

**Prerequisites:** Run `uv sync --all-extras --dev` from the project root. Familiarity with YAML is helpful. For unfamiliar terms, see the [Glossary](glossary.md).

---

## 1. Defining Execution Environments

Execution environments are built from **Resources** (hardware) and **Systems** (resource bundles plus environment variables).

### Resources

Resources define hardware capacity. Add them in `configs/resources/*.yaml`:

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

Systems bundle one or more resources and add environment variables. Add them in `configs/systems/*.yaml`:

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
   cp -r solvers/_template solvers/my-solver
   ```

2. Edit `solvers/my-solver/solver.yaml`:
   ```yaml
   name: my-solver
   entrypoint: run.sh
   allowed_systems: [dev-system, hpc-cluster-01]
   ```

3. Implement `run.sh` (or `run.py`). The script must be executable. The platform passes system `env` variables and invokes it as a subprocess. Your script controls execution (local, SLURM, MPI, etc.).

4. Add a job that uses your solver (see [Defining Jobs](#4-defining-jobs)).

### Key Points

- **Paths** in `solver.yaml` (e.g. `entrypoint`, `parser_config`) are relative to the solver directory.
- **allowed_systems** must list system names that exist in `configs/systems/`. Jobs can only pair your solver with one of these systems.
- **Entrypoint** must exist at the specified path. Use `run.sh` or `run.py`; the platform invokes them via `bash` or `python3`.

---

## 3. Extracting Metrics

To extract metrics from solver output, add a `parser_config.yaml` and reference it in `solver.yaml`.

### Parser Config

Create `solvers/my-solver/parser_config.yaml`:

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

Jobs pair a solver with a system and define success criteria. Add them in `configs/jobs/*.yaml`:

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
| `solver`          | Solver name (must exist in `solvers/`)           |
| `system`          | System name (must exist in `configs/systems/`)   |
| `parameters`      | Optional key-value params (passed to solver)      |
| `success_criteria`| Pass/fail conditions; `returncode` (default 0)   |

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
| `--job <name>`   | Run only these jobs (repeatable)              |
| `--list`         | List jobs and exit                           |
| `--list-runs`    | List recent runs from DB and exit             |
| `--no-store`     | Do not persist results to database           |
| `--solvers-dir`  | Override solvers directory                    |
| `--db`           | Override database path (default: data/harness.db) |

You can also pass a custom config directory as the first argument:

```bash
uv run hpc-runner /path/to/configs --solvers-dir /path/to/solvers
```

### Web UI

Start the dashboard:

```bash
uv run basic-restapi
# or: make api
```

Open http://localhost:8000. You can:

- Run all jobs
- View recent runs (filter by solver or processor)
- Inspect run details (stdout, stderr, metrics)
- View performance trends (metric history over time)

### REST API

For automation:

| Endpoint                    | Method | Description                          |
|----------------------------|--------|--------------------------------------|
| `/api/solvers`             | GET    | List solvers                         |
| `/api/jobs`                | GET    | List jobs                            |
| `/api/run_jobs`            | POST   | Run jobs; body: `{"jobs": ["job1"]}` |
| `/api/runs`                | GET    | List runs (?solver=, ?processor=, ?limit=) |
| `/api/runs/<id>`           | GET    | Run detail                           |
| `/api/metrics/<solver>/<metric>` | GET | Metric history for trends            |

---

## 6. Viewing Results

### Run Output

Each run produces a result with:

- `job_name`, `solver_name`, `system_name`
- `returncode`, `passed` (based on success_criteria)
- `runtime_seconds`, `timestamp`
- `metrics` (extracted via parser_config)
- `processor` (e.g. x86_64, aarch64)

CLI output is JSON. Results are stored in `data/harness.db` unless you use `--no-store`.

### Dashboard

- **Test Runs:** Table of runs with status, processor, timestamp
- **Run detail:** Full stdout, stderr, metrics
- **Performance Trends:** Line chart of a metric over time (select solver and metric)

---

## 7. Troubleshooting

| Issue                    | Check                                                                 |
|--------------------------|-----------------------------------------------------------------------|
| Solver not found         | Solver folder not under `_template` or starting with `_`; `--solvers-dir` points to correct path |
| System not found for job | System exists in `configs/systems/`; solver’s `allowed_systems` includes it |
| Metrics not extracted    | Regex has exactly one capture group; solver prints to stdout/stderr   |
| Job fails                | Inspect returncode; view stdout/stderr in run detail or DB             |
| Entrypoint not found     | Path in `solver.yaml` is relative to solver dir; file exists           |

---

## 8. Quick Reference

**Config layout:**
```
configs/
├── resources/   # Hardware definitions
├── systems/    # Resource bundles + env
└── jobs/       # Solver+system pairings
```

**Solver layout:**
```
solvers/<name>/
├── solver.yaml        # Required
├── run.sh or run.py   # Required
└── parser_config.yaml # Optional
```

**See also:** [Glossary](glossary.md) | [Solver Template](solver_template.md) | [Architecture](architecture.md)
