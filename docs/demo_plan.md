# Demo Plan

This document guides the sponsor through a feature demo, adding a new solver, and collecting deliverables after running jobs on their own systems.

---

## Part 1: Demo Script — Feature Showcase

Follow these steps to see all platform features.

### 1.1 Setup and Quick Validation

From the project root:

```bash
uv sync --all-extras --dev
make test
uv run hpc-runner configs --list
```

You should see available jobs (e.g. `echo-test`, `python-test`).

### 1.2 Running Jobs (CLI)

```bash
# Run all jobs — JSON output with results
uv run hpc-runner configs

# Run a single job
uv run hpc-runner configs --job echo-test

# List recent runs from database
uv run hpc-runner configs --list-runs
```

### 1.3 Interactive Web Dashboard (Streamlit)

```bash
make ui
```

Open http://localhost:8501. You can:

- **Run All Jobs** — execute all configured jobs
- **Test Runs** — table of runs; filter by solver or processor
- **Run detail** — click a run to see stdout, stderr, metrics
- **Performance Trends** — select solver and metric for a line chart over time

### 1.4 REST API (for automation)

```bash
make api
```

Open http://localhost:8000 (redirects to `/docs` for interactive Swagger UI). Available endpoints:

| Request | Description |
|---------|-------------|
| `GET /api/solvers` | List configured solvers |
| `GET /api/jobs` | List configured jobs |
| `POST /api/run_jobs` with `{"jobs": ["echo-test"]}` | Run specific jobs |
| `GET /api/runs` | List runs (?solver=, ?processor=, ?limit=) |
| `GET /api/metrics/python-solver/mlups` | Metric history for trends |

### 1.5 Configuration Layer

- **configs/resources/** — CPU, GPU, memory definitions
- **configs/systems/** — Resource bundles + environment variables
- **configs/jobs/** — Solver+system pairings, success criteria

Flow: Resource → System → Job. See [user_guide.md](user_guide.md) for details.

---

## Part 2: Adding a New Solver (Step-by-Step)

### 2.1 Copy template

```bash
cp -r configs/solvers/_template configs/solvers/demo-solver
```

### 2.2 Edit solver.yaml

Edit `configs/solvers/demo-solver/solver.yaml`:

```yaml
name: demo-solver
entrypoint: run.sh
allowed_systems: [dev-system]
version: "1.0.0"
parser_config: parser_config.yaml
metrics:
  - name: mlups
    unit: MLUPS
    min: 0
    required: true
```

### 2.3 Implement run.sh

Edit `configs/solvers/demo-solver/run.sh`:

```bash
#!/usr/bin/env bash
echo "Solver started"
echo "MLUPS: 1.0e6"
echo "runtime_seconds: 2.5"
echo "status: success"
echo "Solver finished"
```

### 2.4 Add parser_config.yaml

Edit `configs/solvers/demo-solver/parser_config.yaml` (uncomment and adjust):

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

### 2.5 Add a job

Add to `configs/jobs/sample.yaml` (or a new file):

```yaml
  - name: demo-test
    solver: demo-solver
    system: dev-system
    parameters: {}
    success_criteria:
      returncode: 0
```

### 2.6 Run and verify

```bash
uv run hpc-runner configs --list
uv run hpc-runner configs --job demo-test
```

Check the dashboard for the new run and metrics. See [solver_template.md](solver_template.md) for the full specification.

---

## Part 3: Sponsor Deliverables — What to Provide After Internal Testing

After running jobs on your own HPC systems, please provide the following so we can aggregate and analyze results.

### 3.1 Run Results (Required)

Provide **one** of:

| Option | Format | How to Produce |
|--------|--------|----------------|
| **harness.db** | SQLite file | Copy `data/harness.db` after running jobs (default: results are stored) |
| **results.json** | JSON file | `uv run hpc-runner configs > results.json` (or `--job X` for specific jobs) |

**Recommendation:** Prefer **harness.db** when possible (includes stdout/stderr for debugging). Use **results.json** if DB sharing is restricted.

**Contents:** job_name, solver_name, system_name, returncode, passed, runtime_seconds, timestamp, metrics, processor. harness.db also includes stdout and stderr.

### 3.2 Configuration Snapshot (Required)

| Deliverable | Purpose |
|-------------|---------|
| **configs/** | Copy your `configs/resources/`, `configs/systems/`, `configs/jobs/` — so we know what was run and on what hardware |
| **System identifier** | Short name (e.g. "dow-hpc-01", "sponsor-cluster") — used to tag results |

### 3.3 Optional but Helpful

| Deliverable | Purpose |
|-------------|---------|
| Solver versions | If you modified solvers, version or commit info |
| Environment notes | Env vars, modules, or constraints that affected runs |
| Processor/architecture | Explicit note if non-standard (e.g. ARM, specific GPU) — already in results, but helpful for context |

### 3.4 Deliverable Package Structure

Suggested structure for submission:

```
sponsor-results-YYYY-MM-DD/
├── harness.db              # OR results.json
├── configs/
│   ├── resources/
│   ├── systems/
│   └── jobs/
├── system-info.txt        # Optional: system name, notes
└── README.txt             # Optional: what was run, any issues
```

### 3.5 How We Will Use the Deliverables

- Import harness.db or parse results.json for aggregation
- Compare metrics across systems (processor, runtime, pass/fail)
- Build cross-system regression reports
- Validate config compatibility

---

## Part 4: Summary Checklist

- [ ] Run demo script (Part 1)
- [ ] Add a new solver (Part 2)
- [ ] Run jobs on sponsor systems
- [ ] Collect: harness.db (or results.json) + configs/
- [ ] Submit deliverable package

---

## See Also

- [User Guide](user_guide.md) — Defining solvers, systems, jobs, metrics
- [Solver Template](solver_template.md) — Full solver specification
- [Glossary](glossary.md) — Term definitions
- [README](../README.md) — Quick start
