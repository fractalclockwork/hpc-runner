# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed

- **Streamlit navigation** — **Solvers** is the landing page (overview plus **Run Solvers** in one flow). Metric line charts moved to **Individual Trends**; multi-solver / heatmap views remain under **Long-Term Trends**. The in-app **Tests** page is disabled (run **`make test`** / Playwright from the repo instead).

### Documentation

- **`docs/demo_plan.md`** — Brought in line with the solver-first model, invocation and batch APIs, baseline and heatmap behavior, current sidebar pages, optional SLURM E2E, and removal of **`/api/run_jobs`**.

### Tests

- **Playwright e2e** — Navigation and run-flow tests updated for the new page names and **Solvers**-centric UI (`src/ui/tests/e2e/`).

## [0.0.0] - 2026-03-31

Period covered: **2026-02-24 → 2026-03-31** (approximate).

### Added

- **Solver-first runs** — Configuration and UX center on solvers, not separate job YAML trees. Solver specs can carry **`default_system`** (and related fields where configured). Runs are built from **solver + system**. Harness job display names follow **`{solver}@{system}`** (e.g. `lammps-slurm@sci-slurm-lammps` in SLURM smoke tests).
- **`POST /api/run_solvers`** — Launch API replacing “run jobs by job id”. Supports optional **`batch_name`**, per-entry **`system`** overrides, and **`background`** mode (**202** with **one invocation per solver** when background is enabled).
- **Invocations, cancel, and execution status** — `GET /api/invocations`, `GET /api/invocations/{id}`, **`/execution_status`**. Unified cancellation for local subprocesses and **SLURM** (**`scancel`** when the environment allows). **`slurm_status`** endpoints for live scheduler state when SLURM E2E is enabled. Modules: `src/api/src/basic_restapi/invocations.py`, `slurm_tools.py` (see **`src/api/README.md`**).
- **Streamlit “Run Solvers”** — UI aligned with **`run_solvers`** and invocation monitoring.
- **SLURM + LAMMPS path** — Slurm stack integration (e.g. **sci_slurm**), LAMMPS-on-SLURM smoke testing, Makefile and **`docs/slurm_lammps_e2e.md`** updates, **`scripts/start-services-slurm.sh`** / related targets. Gated tests: **`RUN_SLURM_E2E=1`** (**PR #83**).
- **Job monitoring** — Improved monitoring with SLURM-oriented behavior that generalizes to other backends (**PR #84**).
- **Job batching** — Batch identities for grouped runs, API for listing job batch UUIDs, UI for batch views and metadata (**PR #77**).
- **Baseline workflow** — Backend and UI for baseline runs, heatmap behavior, copy/layout cleanup (**PR #76**).
- **Monitoring / cancel test solvers** — **`sleep-60-slurm`** (**`sci-slurm-lammps`**, `sbatch` sleep via **[`docker/slurm_sleep/`](docker/slurm_sleep/)**) and **`sleep-60-local`** (**`dev-system`**) for long-enough runs to exercise invocations and cancel.
- **`HARNESS_SOLVER_WALL_SECONDS`** — Optional line printed from inside **`sbatch`** jobs (sleep and LAMMPS templates) and from **`sleep-60-local`**; high-resolution wall time around the workload (GNU **`date +%s.%N`**, **`EPOCHREALTIME`** fallback, **`awk`** delta). The harness prefers it for **`runtime_seconds`** / metrics for **both** SLURM-backed and local runs when present, otherwise refines from **`sacct`** (**`Start`/`End`**, **`Elapsed`**, **`ElapsedRaw`**) when SLURM job ids exist. Implemented in **`src/core/src/harness/slurm_elapsed.py`** after subprocess completion (see **`refine_run_result_runtime_from_slurm`** in **`runner.py`**).

### Changed

- **Config model** — The **`configs/jobs/`** tree is removed; platform configuration is **resources**, **systems**, and **solvers** only.
- **`runtime_seconds` for SLURM** — No longer tied only to coarse integer **`ElapsedRaw`** or the full outer **`run.sh`** duration when batch or local scripts emit **`HARNESS_SOLVER_WALL_SECONDS`** or when **`sacct`** returns finer **Start/End** / **Elapsed** values.

### Removed

- **`/api/run_jobs`** and **`/api/jobs`**-style launch flows in favor of **`/api/run_solvers`**.

### Fixed

- **Metrics and charts** — Charts reorganized; line charts link into run history; heatmap and long-term metrics (spacing, columns, specification ranges, safer inputs, tests/lint) (**PR #69**, **PR #79**, related).
- **UX** — Run-history icon (**PR #61**); single-click exploration from charts (**PR #82**); assorted default/duplicate-figure fixes.

### Documentation and tests

- **Docs** — Architecture, user guide, glossary, and API README updated for the solver-first and invocation model; **[`docs/slurm_lammps_e2e.md`](docs/slurm_lammps_e2e.md)** and user guide sections for **`HARNESS_SOLVER_WALL_SECONDS`**, sacct fallback, and the sleep solvers.
- **Tests** — Core, API, and UI tests (including Playwright e2e) adjusted for **Run Solvers** and the new API; core tests for **`slurm_elapsed`** (parsing, sacct order, inner-wall vs local/SLURM).

### Breaking changes / migration

- **Config** — Stop relying on **`configs/jobs/*.yaml`**. Each solver YAML should define **`allowed_systems`** and **`default_system`** where you expect one-click or default runs.
- **API clients** — Use **`POST /api/run_solvers`** with a body like `{"solvers": [{"name": "...", "system": "..."}], ...}` instead of job-based endpoints.
- **Automation** — Update scripts and docs that still mention **`/api/run_jobs`** or **“Run Jobs”** in the UI to **`run_solvers`** / **Run Solvers**.
