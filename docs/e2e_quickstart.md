# Playwright E2E Quick Start

This guide gets you from a fresh clone to running the Playwright E2E tests against the Streamlit UI.

## Prerequisites

- **Python 3.10+** and **[uv](https://astral.sh/uv/install)** (same as the main project). See [NOTES.md](../NOTES.md) or the README Quick Start for install steps.
- All commands below are run from the **workspace root** (the directory containing `pyproject.toml` and `Makefile`).

## One-time setup

1. **Sync the workspace** (Python deps only):

   ```bash
   make sync
   ```
   Or: `uv sync --all-extras --dev`

2. **Playwright Chromium** is **not** part of `uv sync`. **`make test-e2e`** runs **`uv run playwright install chromium`** before pytest (idempotent — quick when already installed). For browser only: **`make playwright-chromium`**.

3. You do **not** need to start Streamlit or the API manually for the default `make test-e2e`. The test suite starts Streamlit in the background via `src/ui/tests/e2e/conftest.py`.

## Run E2E tests

From the workspace root:

```bash
make test-e2e
```

(`make e2e` is a backward-compatible alias for `make test-e2e`.)

This runs **`playwright install chromium`** then `uv run pytest src/ui/tests/e2e -v --browser chromium`. Streamlit is launched automatically on port 8501. You can override the port or URL with `STREAMLIT_PORT` and `STREAMLIT_URL` if needed.

## Optional: other ways to run

- **Streamlit already running:** If you have Streamlit running (e.g. `make ui` or in Docker), set `STREAMLIT_ALREADY_RUNNING=1` and optionally `STREAMLIT_URL` / `STREAMLIT_PORT`, then run the same pytest command. Or use `make test-e2e-docker-ui`, which starts Streamlit in a container and runs Playwright on the host against it (`make e2e-docker-ui` is an alias).
- **Fully in Docker:** `make test-e2e-docker` runs both Streamlit and Playwright in Docker (see `docker/docker-compose.e2e.yml`); `make e2e-docker` is an alias.
- **UI in Docker, Playwright local:** `make test-e2e-docker-ui` starts the Streamlit UI in a container and runs the E2E tests locally.

## Troubleshooting

| Issue | What to do |
|-------|------------|
| "Executable doesn't exist" for Chromium | Run `make playwright-chromium` or `uv run playwright install chromium` (or use `make test-e2e`, which runs install first). |
| Streamlit fails to start in time | Ensure port 8501 is free, or set `STREAMLIT_PORT` to another port. |
| Tests need the API (Run Jobs, Home metrics, etc.) | The app expects the API at `http://localhost:8000`. Start it with `make api` if you run those flows. |

For more on the app and config, see [architecture.md](architecture.md) and [user_guide.md](user_guide.md).

## SLURM + LAMMPS (optional)

This is separate from Playwright UI tests. Inputs live under `docker/lammps/` in the repo; **do not modify** the `sci_slurm` symlink directory—copy files into `docker/lammps/` as needed. See **[slurm_lammps_e2e.md](slurm_lammps_e2e.md)** for `RUN_SLURM_E2E`, `DOCKER_SLURM_CONTAINER`, and the gated API test.

With SLURM/LAMMPS available: `export DOCKER_SLURM_CONTAINER=...` if using Docker, then **`make test-slurm`** (it sets `RUN_SLURM_E2E=1` for you).
