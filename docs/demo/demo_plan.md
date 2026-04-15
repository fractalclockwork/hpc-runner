# Demo Plan

This document supports **Flash Demo #3: The Pre-Flight Checklist** (in-class live demo) and continues to guide the **project sponsor** through a deeper feature walkthrough: running the platform, adding a solver, and collecting deliverables after jobs run on sponsor systems.

For the recorded **Technical Review** (longer format), use [technical_review_plan.md](technical_review_plan.md).

---

## Flash Demo #3 — Course requirements (MSSE)

**Format:** Live screen share — **4:00 minutes presentation** (strict hard stop) + **2:00 minutes Q&A** (six-minute block total).

**Goal:** *Progress, not perfection.* Show momentum: code, data, architecture, or an honest blocker. If you show a blocker, state what it is and your timeline to resolve it. Be explicit about **what you plan to share with the project sponsor** (for this team: live harness + UI/API, and sponsor result handoff as in **Part 3** below).

### Rules and logistics

| Rule | Detail |
|------|--------|
| **No slides** | Everything must be **live** (IDE, terminal, schema, console, UI) except **one single slide** allowed for an **architecture diagram** if needed. |
| **Roles** | **One driver** (screen share), **one narrator** (talking). |
| **Audience** | Peers complete a **post-demo feedback survey** (Canvas); meaningful comments per team are part of audience expectations. |

### Choose your path (map to this project)

| Path | When | What to show live (examples for this repo) |
|------|------|---------------------------------------------|
| **A — Full access** | Real stack works on your machine | `make test`, `uv run hpc-runner configs --solver echo-solver`, Streamlit **Solvers** + **Run History**, or a real error/trace you are debugging. |
| **B — Partial access** | Some pieces missing (e.g. no sponsor HPC yet) | Same harness against **mock/dev solvers** and `data/harness.db`; or Swagger **`/docs`** + one CLI run; public/sample configs only. |
| **C — Blocked** | Waiting on access, legal, or environment | **One architecture slide** from [architecture.md](architecture.md) + repo tree in IDE; mock **solver YAML** / **parser_config**; clear blocker statement and **timeline**. |

### Grading reminders (course)

- **Presenters (pass/fail):** ~4 minutes of **technical substance** (code/architecture/data), not marketing; **show** more than **tell**.
- **Audience (pass/fail):** Survey submitted with **meaningful feedback** for peers.

### Suggested 4-minute live script (Path A or B — adjust as needed)

Practice with a timer. Hard stop at **4:00**.

| Time | Driver shows | Narrator says |
|------|----------------|---------------|
| 0:00–0:25 | Repo root in terminal or IDE sidebar | Project one-liner: solver-first HPC regression harness; sponsor will share run DB + configs (**Part 3**). |
| 0:25–1:15 | Terminal: `make test` (or quick `pytest` line) then `uv run hpc-runner configs --list` | Tests green; configs load; we run black-box solvers, parse metrics, store SQLite. |
| 1:15–2:45 | Terminal: `uv run hpc-runner configs --solver echo-solver` **or** `make api` + `make ui` → **Solvers** → **Batch run** or per-solver **Run**; **Active runs** / **Stop**; then **Run History** row expand | End-to-end smoke: run → persist → UI. UI queues **background invocations** (ids); API also supports sync `POST /api/run_solvers` for automation. |
| 2:45–3:45 | Swagger `http://localhost:8000/docs` — `GET /api/runs` **or** IDE peek at [runner.py](../src/core/src/harness/runner.py) / [parser/parser.py](../src/core/src/harness/parser/parser.py) | API for automation; or “how execution + parsing works” in two sentences. |
| 3:45–4:00 | Optional: single architecture slide **or** `configs/solvers/` YAML | Data flow: CLI/API → runner → parser → `harness.db` → API → Streamlit. Stop talking at 4:00. |

**Path C:** Spend ~2 minutes on architecture + mock config schema, ~1.5 minutes on blocker/timeline, ~30s on sponsor plan.

---

## Platform focus (Flash Demo #3 and sponsor deep-dive)

Use this list to decide what to emphasize live vs what to defer to **Part 1** / **Part 0**.

- **Current UI functionality** — Streamlit sidebar: **Home**, **Solvers**, **Run History**, **Individual Trends**, **Long-Term Trends**, **Configs**. On **Solvers**: optional batch name, **Batch run** or per-solver **Run**; runs are **queued in the background** (invocation ids); **Active runs** with **execution_status** and **Stop** (cancel); **Quick status** / **Scheduler output** for pasted ids or SLURM output; **Last run** for stored results. Other pages: **Run History** (filters, batch grouping, **Set baseline**), **Individual Trends** (line chart + optional baseline via API), **Long-Term Trends** (heatmaps, baseline-relative views, manual overrides where implemented), **Configs** (YAML validate/save). The in-app **Tests** page is **not** in the sidebar in the current build—run `make test` or `pytest` from the repo. See [design.md](design.md) and [src/ui/app.py](../src/ui/app.py).
- **Solver-first runs and invocations** — Runs from **solver + system** (no `configs/jobs/` tree). Display identity **`{solver}@{system}`**. API: invocation listing, **execution status**, unified **cancel** (local or **scancel** when SLURM applies), optional **`slurm_status`**. See [CHANGELOG.md](../CHANGELOG.md) and [src/api/README.md](../src/api/README.md).
- **Runner + parsing** — [runner.py](../src/core/src/harness/runner.py), [parser/parser.py](../src/core/src/harness/parser/parser.py), [cli.py](../src/core/src/harness/cli.py). Optional **`HARNESS_SOLVER_WALL_SECONDS`** refines **`runtime_seconds`** (**sacct** fallback on SLURM): [user_guide.md](user_guide.md), [slurm_lammps_e2e.md](slurm_lammps_e2e.md).
- **Architecture** — [architecture.md](architecture.md): Config, Runner, Parser, Storage, API, UI; data flow diagram.
- **Config model** — YAML under **resources**, **systems**, **solvers** only; types in [schemas.py](../src/core/src/harness/config/schemas.py). Storage: [architecture.md](architecture.md) §8 (`runs`, validation, batch, baseline fields).

---

## Part 0: End-to-End MVP Smoke Test

One ordered walkthrough to validate the full workflow (sponsor rehearsal, integration testing, or **Technical Review**). For a **Flash Demo #3** slot, use the **4-minute script** above instead of all eight steps. For detailed commands and UI tables, see Part 1 and Part 2.

| Step | Action | How |
|------|--------|-----|
| 1 | **Load configs** | `uv run hpc-runner configs --list` — or start API and call `GET /api/solvers`, `GET /api/systems` |
| 2 | **Run solvers** | `uv run hpc-runner configs` or `uv run hpc-runner configs --solver echo-solver` — or use **Run Solvers** in the UI or `POST /api/run_solvers` |
| 3 | **Parse metrics** | Automatic: runner uses each solver's `parser_config.yaml` → `extract_metrics()` + `validate_metrics()`. See e.g. `configs/solvers/python-solver/parser_config.yaml` and solver stdout/stderr |
| 4 | **Persist results** | By default results go to `data/harness.db`. Use `--no-store` to run without persisting |
| 5 | **View in UI** | `make ui` → http://localhost:8501 — **Solvers** → **Run Solvers** to launch/monitor; **Run History** (batches, baselines, expand row for stdout/stderr/metrics); **Individual Trends** (line chart + optional baseline); **Long-Term Trends** (heatmaps / baselines) |
| 6 | **View in API** | `make api` → http://localhost:8000/docs — e.g. `GET /api/runs`, `GET /api/runs/<id>`, `GET /api/metrics/...`, `GET /api/invocations`, `POST /api/invocations/<id>/cancel` (see §1.4) |
| 7 | **Add a solver** | Follow **Part 2** below (copy `_template`, edit solver.yaml, run.sh, parser_config.yaml; set `default_system` when multiple systems are allowed) or quick–add: `uv run hpc-runner --add "echo hello" --system dev-system --name hello-check` |
| 8 | **Re-run** | Run the new solver via CLI or **Run Solvers** on **Solvers**; confirm the run appears in **Run History** and (if a metric is defined) under **Individual Trends** / **Long-Term Trends** |

---

## Part 1: Demo Script — Feature Showcase

For a single ordered flow, see **Part 0**. Below are all platform features in detail.

Follow these steps to see all platform features. **Suggested order:** Run solvers first (1.2 or 1.3) so **Individual Trends** / **Long-Term Trends** have data to display.

### 1.1 Setup and Quick Validation

From the project root:

```bash
uv sync --all-extras --dev
make test
uv run hpc-runner configs --list
```

You should see available solvers (e.g. `echo-solver`, `python-solver`).

### 1.2 Running solvers (CLI)

```bash
# Run all solvers — JSON output with results
uv run hpc-runner configs

# Run a single solver
uv run hpc-runner configs --solver echo-solver

# List recent runs from database
uv run hpc-runner configs --list-runs
```

### 1.3 Interactive Web Dashboard (Streamlit)

```bash
make ui
```

Open http://localhost:8501. Walk through each page:

| Page | What to do | What you see |
|------|------------|--------------|
| **Solvers** | Read the overview; use **Batch run** or per-solver **Run** | Optional **batch name**; runs are **always queued in the background** (invocation ids). **Active runs** auto-refreshes **execution_status**; **Stop** cancels. **Quick status** / **Scheduler output** for pasted ids or SLURM output; **Last run** shows stored results |
| **Individual Trends** | Pick a solver/metric from the dropdown (from `GET /api/available_metrics`) | Line chart over run history; optional horizontal **baseline** line if a baseline run is set; raw data expander |
| **Run History** | Filter by solver or processor | Runs grouped by **job batch** (name, date, UUID) when present; each row can **Set baseline** for the solver; expanders for stdout, stderr, metrics |
| **Long-Term Trends** | Explore multi-solver charts and heatmaps | Long-horizon views; heatmaps with spec-range or **baseline-relative** coloring; manual baseline overrides where implemented |
| **Configs** | Pick a category and file; edit YAML; Validate or Save | Resources, systems, solvers, parser_config.yaml |

**Tip:** Run solvers from **Solvers** or the CLI before **Individual Trends** / **Long-Term Trends** so metric history exists.

**Optional SLURM/LAMMPS demo:** With `RUN_SLURM_E2E=1` and the stack from `make start-services-slurm` (see [slurm_lammps_e2e.md](slurm_lammps_e2e.md)), the UI notes SLURM mode and you can exercise real scheduler paths; sleep solvers (**`sleep-60-local`**, **`sleep-60-slurm`**) help test cancel and live status.

### 1.4 REST API (for automation)

```bash
make api
```

Open http://localhost:8000 (`GET /` redirects to `/docs`). The Streamlit app uses `HPC_API_URL` (default `http://localhost:8000`) — see [api_config.py](../src/ui/api_config.py). Core endpoints:

| Request | Description |
|---------|-------------|
| `GET /api/health` | Health check (`{"status": "ok"}`) |
| `GET /api/solvers` | List configured solvers |
| `GET /api/systems` | List systems |
| `POST /api/run_solvers` | Body: `solvers` (each `name`, optional `system`), optional `batch_name`, optional `background`. **`background: false`**: **200** with synchronous result list. **`background: true`**: **202** with `invocations` (one per solver) and optional top-level `invocation_id` when a single solver. The Streamlit **Solvers** page uses the **background** path |
| `GET /api/runs` | List runs (`?solver=`, `?processor=`, `?limit=`, `?offset=`) |
| `DELETE /api/runs` | Delete runs by id list (see OpenAPI schema) |
| `GET /api/runs/<id>` | Run detail |
| `GET /api/runs/<id>/slurm_status` | Scheduler snapshot for that run when applicable |
| `GET /api/invocations` | List invocations (`active_only=true` for in-flight) |
| `GET /api/invocations/<id>` | Invocation record |
| `GET /api/invocations/<id>/execution_status` | Unified execution/scheduler-oriented status |
| `GET /api/invocations/<id>/slurm_status` | SLURM-oriented status when enabled |
| `POST /api/invocations/<id>/cancel` | Cancel (local or **scancel** when allowed) |
| `GET /api/metrics/<solver>/<metric>` | Metric time series |
| `GET /api/available_metrics` | Solver/metric pairs for charts |
| `GET /api/solver_summaries` | Aggregated solver summaries |
| `GET /api/solvers/<solver>/baseline` | Current baseline metrics for a solver |
| `POST /api/runs/<id>/set_baseline` | Mark a run as the solver baseline |
| `GET /api/baseline_comparison` | Baseline comparison data (`?solver=`, `?limit=`) |
| `GET /api/get_job_batch_uuids` | Batch metadata for UI grouping |

Replaces removed **`/api/run_jobs`** / job-list launch flows—clients must use **`run_solvers`**.

### 1.5 Quick Solver Creation (CLI)

Add a solver from a shell command without manual config:

```bash
uv run hpc-runner --add "echo hello" --system dev-system --name hello-check
```

Creates a solver (with `default_system`), then runs it. Use `--no-store` to skip saving to the database.

### 1.6 Configuration Layer

- **configs/resources/** — CPU, GPU, memory definitions
- **configs/systems/** — Resource bundles + environment variables
- **configs/solvers/** — Solver packages (solver.yaml includes `allowed_systems`, optional `default_system`, `success_criteria`, run script, optional parser_config.yaml)

Flow: Resource → System → Solver (runtime pairings are built from solver YAML + CLI/API). See [user_guide.md](user_guide.md) for details.

### 1.7 Docker (optional)

```bash
make docker-build
make docker-run
# Open http://localhost:8000
```

Or validate the build and API health:

```bash
make docker-validate
```

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
default_system: dev-system
version: "1.0.0"
parser_config: parser_config.yaml
success_criteria:
  returncode: 0
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

### 2.5 Run pairing

No separate job YAML is required: `hpc-runner` and `POST /api/run_solvers` build the run from `demo-solver` + resolved system (`default_system` or `--solver` with implicit system).

### 2.6 Run and verify

```bash
uv run hpc-runner configs --list
uv run hpc-runner configs --solver demo-solver
```

Check the dashboard: **Run History** for the new run, **Individual Trends** (and **Long-Term Trends** if relevant) for the mlups chart. See [solver_template.md](solver_template.md) for the full specification.

**Alternative:** Edit solver and parser configs via the **Configs** page in the Streamlit UI (supports solver.yaml and parser_config.yaml).

---

## Part 3: Sponsor Deliverables — What to Provide After Internal Testing

After running solvers on your own HPC systems, please provide the following so we can aggregate and analyze results.

### 3.1 Run Results (Required)

Provide **one** of:

| Option | Format | How to Produce |
|--------|--------|----------------|
| **harness.db** | SQLite file | Copy `data/harness.db` after runs (default: results are stored) |
| **results.json** | JSON file | `uv run hpc-runner configs > results.json` (or `--solver X` for specific solvers) |

**Recommendation:** Prefer **harness.db** when possible (includes stdout/stderr for debugging). Use **results.json** if DB sharing is restricted.

**Contents:** `job_name` (harness label, typically **`{solver}@{system}`**), solver_name, system_name, returncode, passed, runtime_seconds, timestamp, metrics, processor; batch fields and baseline flags as stored. harness.db also includes stdout and stderr.

### 3.2 Configuration Snapshot (Required)

| Deliverable | Purpose |
|-------------|---------|
| **configs/** | Copy your `configs/resources/`, `configs/systems/`, and `configs/solvers/` — so we know what was run and on what hardware |
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
│   └── solvers/
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

**Flash Demo #3 (in class)**

- [ ] Assign **driver** and **narrator**; rehearse with a **4:00** timer (hard stop)
- [ ] Choose **Path A, B, or C**; align live content with sponsor messaging (what sponsor will see later vs what is internal)
- [ ] At most **one** architecture slide (if used); everything else live
- [ ] Confirm screen share: terminal, IDE, Streamlit, and/or Swagger work without login surprises

**Sponsor / integration (ongoing)**

- [ ] Complete Part 0 smoke test: load configs → run solvers → parse metrics → persist → view in UI (Solvers / Run History / trends) → view in API (runs + optional invocations) → add solver → re-run
- [ ] Run demo script (Part 1): setup, CLI, Streamlit pages, API (including `run_solvers` and, if useful, invocations/baseline/batch endpoints)
- [ ] Add a new solver (Part 2)
- [ ] Run solvers on sponsor systems
- [ ] Collect: harness.db (or results.json) + configs/
- [ ] Submit deliverable package

---

## See Also

- [technical_review_plan.md](technical_review_plan.md) — Timed Technical Review video script (10–15 min)
- [CHANGELOG.md](../CHANGELOG.md) — Solver-first model, invocations, SLURM, baselines, batching, breaking changes
- [Architecture](architecture.md) — Components, data flow, storage schema
- [Design](design.md) — UI goals and page components
- [User Guide](user_guide.md) — Defining solvers, systems, metrics, `HARNESS_SOLVER_WALL_SECONDS`
- [SLURM + LAMMPS E2E](slurm_lammps_e2e.md) — Optional gated stack and smoke workflow
- [API README](../src/api/README.md) — Invocation and SLURM-related modules
- [Solver Template](solver_template.md) — Full solver specification
- [Glossary](glossary.md) — Term definitions
- [README](../README.md) — Quick start
