# SLURM + LAMMPS end-to-end testing

The harness invokes `configs/solvers/lammps-slurm/run.sh` as a black-box subprocess. SLURM and LAMMPS are **not** called by the platform directly—only by the script.

## Fully worked example: `sbatch` + result collection (Docker)

When **`DOCKER_SLURM_CONTAINER`** is set, the default path is:

1. Stage **`docker/lammps/in.lammps`** and a generated **`sbatch_lammps.sh`** (from `docker/lammps/sbatch_lammps.sh`) into a unique job directory inside the container.
2. Run **`sbatch`** and parse `Submitted batch job <jobid>`.
3. Poll **`squeue`** until the job leaves the queue.
4. **`cat`** `slurm-<jobid>.out` and `slurm-<jobid>.err` to stdout/stderr (so the harness captures them).
5. Exit with the batch exit code from **`sacct`** (`ExitCode`, before the `:`).

After a successful **`sbatch`**, `run.sh` prints **machine-readable lines** (to the combined process stdout) so the harness can store SLURM metadata and support cancellation/monitoring:

- `HARNESS_SCHEDULER_BACKEND=slurm`
- `HARNESS_SLURM_JOB_ID=<numeric id>`
- `HARNESS_SUBMIT_CONTAINER=<docker container name or host>`

Batch scripts in this repo (e.g. [`docker/slurm_sleep/sbatch_sleep60.sh`](docker/slurm_sleep/sbatch_sleep60.sh), [`docker/lammps/sbatch_lammps.sh`](docker/lammps/sbatch_lammps.sh)) emit **`HARNESS_SOLVER_WALL_SECONDS=<seconds>`** from **inside** the `sbatch` job (GNU `date +%s.%N` / `EPOCHREALTIME` around the workload, printed to `slurm-%j.out`). Local solver entrypoints can use the **same** line (e.g. [`configs/solvers/local-sleep-60/run.sh`](../configs/solvers/local-sleep-60/run.sh) on **`dev-system`**) so **`runtime_seconds`** uses identical high-resolution wall time around the workload, not only the harness subprocess envelope.

The runner parses the `HARNESS_*` lines above into each stored run (`scheduler_backend`, `scheduler_job_ids`, `submit_container`). After the solver subprocess exits, if **`HARNESS_SOLVER_WALL_SECONDS`** is present in captured stdout/stderr, it sets **`runtime_seconds`** / metrics. Otherwise the harness queries **`sacct`** in the same submit container (or on the host when `HARNESS_SUBMIT_CONTAINER=host`), in this order: **`Start`/`End`**, then **`Elapsed`**, then **`ElapsedRaw`**. That fallback is **best-effort** accounting and may differ by about **±1s** from an in-script **`sleep`** on some sites.

The UI can call **`GET /api/runs/{id}/slurm_status`** when **`RUN_SLURM_E2E=1`**.

**Start your stack** (e.g. `docker compose up` for `sci_slurm`), then on the **host** (Docker CLI + harness):

```bash
cd /path/to/e2e_testing
export RUN_SLURM_E2E=1
export DOCKER_SLURM_CONTAINER=sci_slurm-gpu-worker-1   # or your compute / login node (see below)
uv run hpc-runner configs --job lammps-slurm-smoke --db data/harness.db
# or: make test-slurm
```

**See full solver output** (LAMMPS log, `Submitted batch job …`, `slurm-*.out` / `.err` text): add **`-v` / `--verbose`**. Details print to **stderr**; the JSON summary on **stdout** still parses the same, with **`stdout`** / **`stderr`** fields included when `-v` is set:

```bash
uv run hpc-runner configs --job lammps-slurm-smoke --no-store -v 2>&1 | less
```

### Choosing the container

| Variable | Purpose |
|----------|---------|
| `DOCKER_SLURM_CONTAINER` | Container used for **direct** `docker exec … lmp` when `LAMMPS_USE_SBATCH=0`. |
| `DOCKER_SLURM_SUBMIT_CONTAINER` | Container where **`sbatch` / `squeue` / `sacct`** run. Defaults to `DOCKER_SLURM_CONTAINER`. |

**Without a shared filesystem** between Slurm nodes, submit from a node that can see the job’s working directory—often the **compute node** you use for tests (e.g. `sci_slurm-gpu-worker-1`). If you submit only from `slurmctld`, stdout/stderr may land on the **execution** node’s disk; then either mount shared storage for `JOBDIR` or set `DOCKER_SLURM_SUBMIT_CONTAINER` to the node where outputs appear.

### Opt out of `sbatch` (quick interactive path)

```bash
export LAMMPS_USE_SBATCH=0
```

Then the script uses **`docker exec … lmp -in in.lammps`** in `/tmp/lammps-smoke` (no batch job). Use **`LAMMPS_USE_SRUN=1`** only if your MPI + Slurm PMI stack matches (often fails with generic MPI `lmp`).

### Environment reference

| Variable | Default | Meaning |
|----------|---------|---------|
| `RUN_SLURM_E2E` | — | Must be `1` or the script exits 0 with `SKIP:` (CI-safe). |
| `LAMMPS_USE_SBATCH` | `1` (with Docker) | `0` = direct `lmp` in container. |
| `LAMMPS_BIN` | `lmp` | LAMMPS executable name in the container. |
| `SBATCH_WAIT_TIMEOUT` | `600` | Max seconds to wait for job to leave `squeue`. |
| `LAMMPS_INPUT` | `docker/lammps/in.lammps` | Override input deck path. |

## Do not modify external `sci_slurm`

If you still have a **`sci_slurm`** symlink for convenience, treat it as **read-only** from this project. All inputs and batch templates live under **`docker/lammps/`** in the repo.

## Layout

| Path | Purpose |
|------|---------|
| `docker/lammps/in.lammps` | LAMMPS input deck |
| `docker/lammps/sbatch_lammps.sh` | `#SBATCH` template; `__LAMMPS_BIN__` replaced at run time |
| `docker/lammps/work/` | Gitignored staging on the host (`LAMMPS_WORK_HOST`) |
| `configs/solvers/lammps-slurm/run.sh` | Entrypoint: sbatch (default) or direct `lmp` |
| `docker/slurm_sleep/sbatch_sleep60.sh` | `#SBATCH` template for the sleep test job |
| `docker/slurm_sleep/work/` | Gitignored staging (`SLURM_SLEEP_WORK_HOST`) |
| `configs/solvers/slurm-sleep-60/run.sh` | Entrypoint: `sbatch` a job that sleeps **60s** (override with **`SLURM_SLEEP_SECONDS`**) |

### Monitoring / cancel test: `slurm-sleep-60`

Use solver **`slurm-sleep-60`** with system **`sci-slurm-lammps`** when you need a **long-enough SLURM batch job** to exercise invocation monitoring or **`POST /api/invocations/{id}/cancel`** / **`scancel`**. It uses the same Docker **`sbatch`** flow as **`lammps-slurm`** and emits the same **`HARNESS_*`** lines.

```bash
# Example (background: true so you can poll/cancel while the batch sleeps)
curl -s -X POST http://localhost:8000/api/run_solvers \
  -H 'Content-Type: application/json' \
  -d '{"solvers":[{"name":"slurm-sleep-60","system":"sci-slurm-lammps"}],"background":true}'
```

## Skipped run (default CI / local)

If **`RUN_SLURM_E2E` is not `1`**, `run.sh` exits **0** immediately with a `SKIP:` line so synchronous `POST /api/run_solvers` for `lammps-slurm` still records a passing smoke run when SLURM is skipped.

## Host SLURM (no Docker)

Set **`LAMMPS_USE_SBATCH=1`**, leave **`DOCKER_SLURM_CONTAINER`** unset. The script stages under **`docker/lammps/work/`**, runs **`sbatch`**, waits, prints outputs, and exits using **`sacct`**.

For a host-only interactive run without batch: **`LAMMPS_USE_SBATCH=0`** (and optionally **`LAMMPS_USE_SRUN=1`**).

## Start API + UI with SLURM/LAMMPS env

So **`POST /api/run_solvers`** and the **Run Solvers** page use the same environment as the CLI:

```bash
cp slurm-lammps.env.example slurm-lammps.env   # edit DOCKER_SLURM_CONTAINER, etc.
make stop-services    # if something is already on 8000/8501
make start-services-slurm
```

This loads **`slurm-lammps.env`** from the repo root (if present) and starts the API and Streamlit with **`RUN_SLURM_E2E`**, **`DOCKER_SLURM_CONTAINER`**, etc. exported. Override the file path with **`SLURM_LAMMPS_ENV=/path/to/env`**.

Use **`make restart-services-slurm`** to stop (same ports as `stop-services`) and start again.

### Streamlit dashboard

1. Open **http://localhost:8501** after `make start-services-slurm`.
2. **Run Jobs** — select `lammps-slurm-smoke` (or Run All), click **Run Selected** / **Run All**. Results show pass/fail; expand **Solver output** for `sbatch` + LAMMPS stdout.
3. **Run History** — expand a run to see stored stdout/stderr (same as API).
4. **Home** — choose **`lammps-slurm` / `runtime_seconds`** once at least one run is stored (metrics come from the DB).

The sidebar shows a short **SLURM/LAMMPS mode** note when `RUN_SLURM_E2E=1` is set.

## Automated API test

```bash
export DOCKER_SLURM_CONTAINER=sci_slurm-gpu-worker-1   # if using Docker
make test-slurm
```

`make test-slurm` sets **`RUN_SLURM_E2E=1`**. Export **`DOCKER_SLURM_CONTAINER`** when using Docker.

## Docker Compose (optional)

The API image includes `docker/lammps/` via `docker/Dockerfile`.

```bash
export DOCKER_SLURM_CONTAINER=your_container_name
docker compose -f docker/docker-compose.yml -f docker/docker-compose.slurm.yml up --build
```

**Note:** `run.sh` uses the **`docker` CLI** on the **host** when submitting from the host API process. The stock API image does not include Docker; run **`make api` on the host** or add Docker CLI + `/var/run/docker.sock` to a custom image.

## See also

- [user_guide.md](user_guide.md)
- [e2e_quickstart.md](e2e_quickstart.md) (Playwright UI tests)
