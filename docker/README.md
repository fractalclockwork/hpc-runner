# Docker assets

| File | Purpose |
|------|---------|
| `Dockerfile` | API + harness workspace image (includes `configs/` and `docker/lammps/` for LAMMPS smoke). |
| `Dockerfile.playwright` | Playwright E2E image. |
| `docker-compose.yml` | REST API on port 8000. |
| `docker-compose.e2e.yml` | Streamlit + Playwright UI E2E. |
| `docker-compose.slurm.yml` | **Optional overlay** — passes `RUN_SLURM_E2E`, `DOCKER_SLURM_CONTAINER`, `LAMMPS_BIN` into the API service. |

## SLURM + LAMMPS

- Inputs and **`sbatch_lammps.sh`** live under **`docker/lammps/`** (also copied into the API image). The harness **`run.sh`** defaults to **`sbatch`** inside `DOCKER_SLURM_SUBMIT_CONTAINER` (or `DOCKER_SLURM_CONTAINER`), waits for the job, then prints **`slurm-<jobid>.out` / `.err`** and exits with **`sacct`**’s exit code.
- Full workflow: **[../docs/TESTING_SLURM.md](../docs/TESTING_SLURM.md)**

```bash
export RUN_SLURM_E2E=1
export DOCKER_SLURM_CONTAINER=sci_slurm-gpu-worker-1
make api   # host API + Docker CLI calling sbatch
```
