# Technical Review — Video Walkthrough Plan

Presenter script for **Deliverable 2** (recorded Technical Review, 10–15 minutes). Aligns with [technical_review__outline.md](technical_review__outline.md) §3 (including speaker roster §3.1.1), uses [demo_plan.md](demo_plan.md) **Part 0** as the validation backbone, and requires a live **`slurm-sleep-60`** start / monitor / **Stop** demo when SLURM is available. Maps to **Deliverable 1** (Technical Architecture README): each top-level folder you show should correspond to a README directory-map entry.

**Assumptions:** Run all commands from the repository root. Dependencies installed with `uv sync --all-extras --dev`. Default URLs: Streamlit **http://localhost:8501**, API **http://localhost:8000** (`GET /` returns a **302** to **`/docs`** — Swagger). The Streamlit app expects the API to be reachable (see [api_config.py](../src/ui/api_config.py)); start **`make api`** before **`make ui`** for a full demo.

---

## Pre-recording checklist

- [ ] `uv sync --all-extras --dev` completed
- [ ] `make test` passes (core unit tests)
- [ ] Optional: `make e2e` if you will mention Playwright UI automation ([e2e_quickstart.md](e2e_quickstart.md))
- [ ] Before **Segment C**: `make api` and `make ui` running (or `make start-services`), or plan to start them on camera
- [ ] **SLURM demo (`slurm-sleep-60`):** Stack and env per [slurm_lammps_e2e.md](slurm_lammps_e2e.md) (e.g. `RUN_SLURM_E2E=1`, `make start-services-slurm`, `slurm-lammps.env` if used). Solver uses system **`sci-slurm-lammps`** ([`configs/solvers/slurm-sleep-60/solver.yaml`](../configs/solvers/slurm-sleep-60/solver.yaml))
- [ ] Decide whether `data/harness.db` already has runs or you will seed with a quick local solver; reserve **`slurm-sleep-60`** for the live start / monitor / **Stop** sequence
- [ ] Zoom: UC Berkeley Zoom Cloud, password-protected, link shareable with Sponsor and Instructor ([technical_review__outline.md](technical_review__outline.md) §3.1)
- [ ] **Every team member speaks** at least once (course requirement)

---

## Timed run-of-show (~13 minutes + 1–2 min buffer)

| Block | Time | Outline | What to show / say |
|-------|------|---------|-------------------|
| **A** | 0:00–3:00 | §3.2.1 Lay of the land | Repo structure: where code, configs, tests, docs, and UI live; how the Architecture README directory map mirrors the tree. |
| **B** | 3:00–10:00 | §3.2.2 Deep dive | One primary subsystem (recommended: **Runner + Parser + storage**); brief secondary thread (API or UI data flow). |
| **C** | 10:00–13:00 | §3.2.3 Validation proof | CLI smoke → **`slurm-sleep-60`** (start, monitor, **Stop**) → UI → API → **`make test`**. |
| **D** (optional) | +1–2 min | §4 integration | Platform progress and current capabilities; [CHANGELOG.md](../CHANGELOG.md) for detail (no flash‑demo framing). |

**Flex:** If short on time, trim **Home** in the UI, skip **Long-Term Trends** detail, or shorten the deep-dive secondary thread.

---

## Segment A — Lay of the land (0:00–3:00)

**Primary voices:** **Shree** (purpose, sponsor framing), **Brent** (repo tree, docs, README map, Makefile entrypoints). **Shawn** may add one bridge sentence into architecture before Segment B.

### Talking points

1. **Purpose of the review** (30s): Professional engineering practices, architecture of the HPC Regression Platform, correctness/reproducibility/maintainability for the sponsor ([technical_review__outline.md](technical_review__outline.md) §1).
2. **Top-level map** (2–2.5 min): Walk the tree in an IDE or `tree -L 2` (or README directory map). One sentence per area:

| Path | One-liner |
|------|-----------|
| `src/core/src/harness/` | CLI, config loader, **runner**, **parser**, **storage** — harness core ([runner.py](../src/core/src/harness/runner.py), [parser/parser.py](../src/core/src/harness/parser/parser.py), [storage/db.py](../src/core/src/harness/storage/db.py)) |
| `src/api/src/basic_restapi/` | FastAPI app, invocations, SLURM helpers ([fastapi_app.py](../src/api/src/basic_restapi/fastapi_app.py)) |
| `src/ui/` | Streamlit dashboard ([app.py](../src/ui/app.py)) |
| `configs/resources/`, `configs/systems/`, `configs/solvers/` | Declarative YAML — solver-first; no `configs/jobs/` tree |
| `data/` | Default SQLite `harness.db` |
| `docs/` | Architecture, user guide, demo plans |
| `src/core/tests/`, `src/api/tests/`, `src/ui/tests/e2e/` | Unit, API, Playwright E2E |

3. **Tie to README** (30s): [architecture.md](architecture.md) defers the **repository directory map** and **style guide** to [README.md](../README.md). The end-to-end data flow there matches these folders: CLI → Runner → Parser → Storage → API → UI, with **Streamlit calling FastAPI over HTTP** (some helpers may still use shared harness code or DB paths—see architecture §2).

---

## Segment B — Deep dive (3:00–10:00)

**Primary voice:** **Shawn** (design and architecture). **Brent** can hand off Segment A into this block with a single sentence on “where to run things” if needed.

### Recommended primary thread: Runner + Parser + storage (~5–6 min)

**Files to have open (split editor or slides with paths):**

| Step | File | Say |
|------|------|-----|
| Entry | [cli.py](../src/core/src/harness/cli.py) | How `hpc-runner configs` loads config and invokes the runner |
| Orchestration | [runner.py](../src/core/src/harness/runner.py) | Black-box subprocess; return codes; integration with parser and DB |
| Metrics | [parser/parser.py](../src/core/src/harness/parser/parser.py) + example `configs/solvers/*/parser_config.yaml` | Regex-driven extraction; validation; no metric logic hard-coded per solver |
| Schema | [schemas.py](../src/core/src/harness/config/schemas.py) | Resource, System, Solver; `{solver}@{system}` job naming |
| Persistence | [storage/db.py](../src/core/src/harness/storage/db.py) | What gets stored (runs, metrics, batch/baseline fields) |

**Spoken bullets (patterns and trade-offs):**

- **Config-driven design:** New metrics via YAML patterns, not core code changes.
- **Black-box execution:** Harness does not embed SLURM/MPI; solvers may call schedulers externally ([architecture.md](architecture.md) §1).
- **Reproducibility:** Same configs + same solver scripts → comparable stored runs.
- **Trade-off:** Regex parsing is simple and inspectable; complex logs may need richer patterns or pre-processing in the solver script.
- **Runtime timing:** Optional solver-reported wall time (e.g. `HARNESS_SOLVER_WALL_SECONDS`) refines stored **`runtime_seconds`**; SLURM paths may use **sacct** fallback ([user_guide.md](user_guide.md), [slurm_lammps_e2e.md](slurm_lammps_e2e.md)).

### Secondary thread — pick one (~1.5–2 min)

**Option 1 — API façade**

- [fastapi_app.py](../src/api/src/basic_restapi/fastapi_app.py): `POST /api/run_solvers` with `background: false` (synchronous **200** + results) vs `background: true` (**202** + `invocations`). The Streamlit **Solvers** page queues work through the **background** path (invocation ids); automation may still use synchronous runs.
- [invocations.py](../src/api/src/basic_restapi/invocations.py): list invocations, `execution_status`, `POST .../cancel` (local subprocess vs `scancel` when SLURM applies).

**Option 2 — UI data flow**

- [app.py](../src/ui/app.py): Sidebar `PAGES`; **Solvers** drives runs/invocations via the API; **Run History** uses `GET /api/runs`; **Individual Trends** uses `GET /api/available_metrics`, `GET /api/metrics/{solver}/{metric}`, and `GET /api/solvers/{solver}/baseline` for the optional baseline line.
- [api_config.py](../src/ui/api_config.py): Base URL for HTTP calls to FastAPI (default `http://localhost:8000`, override with **`HPC_API_URL`** e.g. for Docker).

---

## Segment C — Validation proof (10:00–13:00)

**Primary voices:** **Kayleen** (tests + SLURM proof narrative), **Shree** (Streamlit driving **`slurm-sleep-60`**), **Brent** (terminal / API / env as needed). Reorder slightly if the SLURM stack needs a spoken setup line from Brent first.

Follow [demo_plan.md](demo_plan.md) **Part 0** in spirit; **this team’s** SLURM story is **`slurm-sleep-60`** (start → monitor → **Stop** before the 60s job completes).

| Step | Action | Command or UI |
|------|--------|----------------|
| 1 | Load configs | `uv run hpc-runner configs --list` (confirm **`slurm-sleep-60`** listed) |
| 2 | **SLURM demo (required)** | With SLURM env up ([slurm_lammps_e2e.md](slurm_lammps_e2e.md)): on **Solvers**, run **`slurm-sleep-60`** with system **`sci-slurm-lammps`**. Watch **Active runs** / **execution_status**; optional **Scheduler output** or `GET /api/invocations/.../execution_status` and `.../slurm_status`. Then **Stop** (cancel) to show **`scancel`** path. Narrate: submit, observe, cancel. |
| 3 | (Optional quick) | Local smoke: `uv run hpc-runner configs --solver echo-solver` if you need a fast non-SLURM row in **Run History** |
| 4 | Parse / persist | Automatic; default `data/harness.db` |
| 5 | UI | **Run History** (expand stdout/stderr for the SLURM run); trends if time |
| 6 | API | Swagger: e.g. `GET /api/invocations`, `POST /api/invocations/{id}/cancel`, `GET /api/runs/{id}/slurm_status` when E2E enabled |
| 7 | Tests | **`make test`** in terminal (required by outline §3.2.3); optional mention **`make e2e`** |

**Important:** The in-app **Tests** page is **not** wired in the current Streamlit build ([demo_plan.md](demo_plan.md)). Say clearly that automated tests are run via **`make test`** (and optionally **`make e2e`**).

---

## UI demo order (Streamlit sidebar)

Pages are defined in [app.py](../src/ui/app.py) (`PAGES`): **Home**, **Solvers**, **Run History**, **Individual Trends**, **Long-Term Trends**, **Configs**.

| Order | Page | What to demonstrate |
|-------|------|---------------------|
| 1 (optional) | **Home** | Brief orientation (~15s) |
| 2 | **Solvers** | Overview; **Batch run** or per-solver **Run**; background invocations. For the review, prioritize **`slurm-sleep-60`** + **`sci-slurm-lammps`**: submit, watch **Active runs** / **execution_status**, then **Stop** before completion. **Quick status** / **Scheduler output** for pasted ids or raw SLURM output; **Last run** for stored results ([app.py](../src/ui/app.py) `page_solvers`). Stack: [slurm_lammps_e2e.md](slurm_lammps_e2e.md) |
| 3 | **Run History** | Filters; batch grouping; expand row for stdout/stderr/metrics; **Set baseline** if time |
| 4 | **Individual Trends** | Solver/metric chart; optional baseline line |
| 5 | **Long-Term Trends** | Heatmaps / multi-solver views (short if time-constrained) |
| 6 | **Configs** | Open a YAML; Validate or Save |

**Tip:** Run solvers before trends pages if the DB is empty.

---

## API demo order (Swagger at `/docs`)

Routes are registered in [fastapi_app.py](../src/api/src/basic_restapi/fastapi_app.py). Minimal set for the video:

| Order | Method | Path | Note |
|-------|--------|------|------|
| 1 | GET | `/api/health` | Also `/health` alias |
| 2 | GET | `/api/solvers` | Configured solvers |
| 3 | GET | `/api/systems` | Systems |
| 4 | GET | `/api/runs` | Query params: `solver`, `processor`, `limit`, `offset` |
| 5 | GET | `/api/runs/{run_id}` | Pick an id from list response |
| 6 | GET | `/api/available_metrics` | Drives trend dropdowns |
| 7 | POST | `/api/run_solvers` | Show schema: `solvers`, optional `batch_name`, optional `background` |

**If time:** `GET /api/invocations`, `GET /api/invocations/{invocation_id}/execution_status`, `GET /api/invocations/{invocation_id}/slurm_status`, `POST /api/invocations/{invocation_id}/cancel`, `GET /api/baseline_comparison`, `POST /api/runs/{run_id}/set_baseline`, `GET /api/solver_summaries`, `GET /api/get_job_batch_uuids` (batch grouping in **Run History**), `GET /api/runs/{run_id}/slurm_status`.

**Removed:** Older `/api/run_jobs` style flows — clients use **`run_solvers`** ([demo_plan.md](demo_plan.md) §1.4).

---

## Command reference (copy-paste)

```bash
# Setup
uv sync --all-extras --dev
make test

# CLI — smoke
uv run hpc-runner configs --list
uv run hpc-runner configs
uv run hpc-runner configs --solver echo-solver
uv run hpc-runner configs --list-runs

# Web
make ui    # http://localhost:8501
make api   # http://localhost:8000 → /docs

# Background services (optional)
make start-services
make stop-services

# Optional: UI E2E (Playwright)
# uv run playwright install chromium   # once
make e2e

# SLURM demo (slurm-sleep-60) — see docs/slurm_lammps_e2e.md
# export RUN_SLURM_E2E=1
# make start-services-slurm   # or your compose + env (DOCKER_SLURM_* as needed)
# Then UI/API: run solver slurm-sleep-60 @ sci-slurm-lammps → monitor → Stop
```

---

## Segment D — Platform progress (optional 1–2 min)

**Primary voice:** **Shawn** (architecture trajectory); **Shree** may add sponsor-facing next steps.

Short narrative: solver-first runs (`{solver}@{system}`), background **invocations** with cancel (including SLURM **`scancel`**), **baselines** and **batch** metadata in the UI and API. Ground details in [CHANGELOG.md](../CHANGELOG.md). Avoid framing this as a flash-demo recap.

---

## Team roles (four speakers)

Canonical assignment matches [technical_review__outline.md](technical_review__outline.md) §3.1.1.

| Speaker | Expertise | Segments | Responsibility |
|---------|-----------|----------|----------------|
| **Brent** | DevOps and Documentation | A (co), C (co) | Repo tree, `docs/`, README directory map, `Makefile` / `uv` / services; SLURM env and **`make start-services-slurm`** setup for **`slurm-sleep-60`** |
| **Kayleen** | Testing and Validation | C (co-lead) | **`make test`** (and optional **`make e2e`**); narrate **start → monitor → Stop** for **`slurm-sleep-60`** as validation proof |
| **Shree Patel** | UI and Project Management | A (co), C (co) | Sponsor framing and scope; drive Streamlit **Solvers** / **Run History** for SLURM demo; timekeeping |
| **Shawn** | Design and Architecture | B, D (optional) | Deep dive (runner/parser/storage + secondary API or UI thread); optional Segment D recap vs [CHANGELOG.md](../CHANGELOG.md) |

**Requirement:** Every member speaks on the recording ([technical_review__outline.md](technical_review__outline.md) §3.1). Rehearse handoffs so no one talks over the driver’s cursor during UI steps.

---

## Deliverable 1 cross-check

Before recording, confirm the Technical Architecture README includes: directory map, naming/style notes, architectural overview, data flow, how to run tests/UI/API ([technical_review__outline.md](technical_review__outline.md) §2). The video should **point at** the same folders the README describes.

---

## Appendix — Related docs

- [technical_review__outline.md](technical_review__outline.md) — Full deliverable requirements and checklists
- [demo_plan.md](demo_plan.md) — Part 0 smoke test, Part 1 feature detail, Part 2 add-solver (not required for the 10–15 min video unless you choose it)
- [README.md](../README.md) — Project overview, directory map, and style conventions (Deliverable 1 anchor)
- [architecture.md](architecture.md) — Components, mermaid data flow, storage notes, API-oriented overview
- [design.md](design.md) — UI goals and historical page concepts (implementation is in `app.py`)
- [user_guide.md](user_guide.md) — Solvers, metrics, `HARNESS_SOLVER_WALL_SECONDS`, and related behavior
- [src/api/README.md](../src/api/README.md) — Invocation and SLURM-related modules
