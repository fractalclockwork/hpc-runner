# Glossary of Terms

This glossary defines key terms for the HPC Regression Platform. It helps **developers** working on the harness or API, **config authors** defining resources, systems, and jobs, and **solver authors** creating solver packages.

---

## Quick Reference

| Task | Relevant Terms |
|------|----------------|
| Adding a new solver | Solver, Entrypoint, allowed_systems, parser_config |
| Defining execution environments | Resource, System |
| Running tests | Job, Run, RunResult |
| Extracting metrics from logs | parser_config, Pattern, Metric, extract_metrics |
| Viewing results | RunResult, harness.db, Metric history |

---

## Core Concepts

**Black-box** — Solver run scripts are executed without platform inspection of internals; only stdout, stderr, and returncode are consumed.

**Execution-agnostic** — Design principle: the platform invokes solver scripts as black-box subprocesses. Solver scripts control execution (local, SLURM, MPI, etc.); the platform does not call schedulers directly.

**Harness** — The core platform (package `harness` in `src/core`) that loads configs, runs jobs, parses metrics, and stores results.

**HPC Regression Testing** — Use case: running solver jobs repeatedly to detect performance regressions and validate correctness across systems.

---

## Configuration Entities

**Job** — A pairing of a Solver with a System, plus parameters and success criteria. Defined in `configs/jobs/*.yaml`. The unit of work executed by the runner. Optional `schedule` field reserved for future cron/scheduling.

**Resource** — Hardware definition: CPU count, GPU count, memory (GB). Defined in `configs/resources/*.yaml`. Referenced by Systems.

**Solver** — A self-contained package with `solver.yaml`, entrypoint script, and optional parser config. Lives in `configs/solvers/<name>/`. Declares `allowed_systems` and metrics.

**System** — A bundle of one or more Resources plus environment variables and optional constraints. Defined in `configs/systems/*.yaml`. Represents a target execution environment (e.g. `dev-system`, `hpc-cluster-01`).

---

## Solver Package Terms

**allowed_systems** — List of system names a solver can run on. Jobs must pair a solver with one of its allowed systems.

**cwd** — Working directory for solver execution. In `solver.yaml`: `true` (default) = solver dir; `false` = entrypoint parent; or a string path.

**Entrypoint** — The script executed to run the solver (e.g. `run.sh`, `run.py`). Path is relative to the solver directory.

**extra** — Optional dict on Resource, System, Solver, and Job schemas for extensibility. Unknown YAML keys are stored here.

**MetricSpec** — Declarative definition of an expected metric: `name`, `unit`, `min`, `max`, `required`. Used for validation.

**parser_config** — YAML file defining regex patterns to extract metrics from solver stdout/stderr. Optional; path relative to solver directory.

**Pattern** — A single extraction rule in `parser_config.yaml`: `name`, `regex` (with one capture group), `type` (`str`, `float`, `int`).

**Template directory** — `configs/solvers/_template/` (or any folder starting with `_` or named `template`). Ignored by the loader; used as a copy source for new solvers. See [solver_template.md](solver_template.md).

---

## Execution and Results

**passed** — Boolean indicating whether the run met success criteria (e.g. returncode match).

**processor** — CPU architecture of the host (e.g. `x86_64`, `aarch64`). Probed via `platform.machine()`; stored with each run for filtering.

**returncode** — Exit code from the solver process. Used for pass/fail when matched against `success_criteria.returncode`.

**Run** — A single execution of a Job. Produces a RunResult.

**RunResult** — Dataclass holding: `job_name`, `solver_name`, `system_name`, `returncode`, `stdout`, `stderr`, `runtime_seconds`, `timestamp`, `metrics`, `passed`, `processor`.

**runtime_seconds** — Wall-clock time from job start to finish.

**success_criteria** — Job-level conditions for pass/fail. Currently supports `returncode` (expected value, default 0).

---

## Metrics and Parsing

**extract_metrics** — Parser function that applies `parser_config` patterns to log text and returns a `dict[str, Any]`.

**Metric** — A named value extracted from solver output (e.g. MLUPS, runtime_seconds). Extracted via regex patterns; stored in `metrics_json` per run.

**Metric history** — Time-series of (timestamp, value) for a given solver+metric. Used for trend charts in the dashboard.

**metrics_json** — JSON-serialized metrics dict stored in the `runs` table.

---

## Storage and API

**config_dir** — Root directory containing `resources/`, `systems/`, `jobs/`, and `solvers/` subdirs. Default: `configs`.

**harness.db** — SQLite database (default `data/harness.db`) storing run metadata and metrics.

**load_all** — Config loader function returning `(resources, systems, solvers, jobs)` from a config directory.

**runs table** — Schema: `id`, `job_name`, `solver_name`, `system_name`, `returncode`, `passed`, `runtime_seconds`, `timestamp`, `stdout`, `stderr`, `metrics_json`, `processor`.

**solvers_dir** — Directory containing solver packages. Lives inside config_dir: `config_dir/solvers` (e.g. `configs/solvers/`). Overridable via `--solvers-dir`.

---

## CLI and API

**hpc-runner** — CLI entrypoint. Usage: `hpc-runner [config_dir]` (config_dir defaults to `configs`). Options: `--list` (list jobs), `--list-runs` (list last 20 runs), `--job <name>` (repeatable), `--no-store` (skip DB), `--db PATH`, `--solvers-dir PATH`, `--add CMD --system NAME` (create solver from command and run).
