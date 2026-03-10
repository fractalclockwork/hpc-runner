# Playwright E2E Quick Start

This guide gets you from a fresh clone to running the Playwright E2E tests against the Streamlit UI.

## Prerequisites

- **Python 3.10+** and **[uv](https://astral.sh/uv/install)** (same as the main project). See [NOTES.md](../NOTES.md) or the README Quick Start for install steps.
- All commands below are run from the **workspace root** (the directory containing `pyproject.toml` and `Makefile`).

## One-time setup

1. **Sync the workspace** (creates `.venv` and installs dependencies):

   ```bash
   uv sync --all-extras --dev
   ```
   Or: `make sync`

2. **Install Playwright browsers** (required before the first E2E run):

   ```bash
   uv run playwright install chromium
   ```

   Without this step, `make e2e` will fail with an error like "Executable doesn't exist" for Chromium.

3. You do **not** need to start Streamlit or the API manually for the default `make e2e`. The test suite starts Streamlit in the background via `src/ui/tests/e2e/conftest.py`.

## Run E2E tests

From the workspace root:

```bash
make e2e
```

This runs `uv run pytest src/ui/tests/e2e -v --browser chromium`. Streamlit is launched automatically on port 8501. You can override the port or URL with `STREAMLIT_PORT` and `STREAMLIT_URL` if needed.

## Optional: other ways to run

- **Streamlit already running:** If you have Streamlit running (e.g. `make ui` or in Docker), set `STREAMLIT_ALREADY_RUNNING=1` and optionally `STREAMLIT_URL` / `STREAMLIT_PORT`, then run the same pytest command. Or use `make e2e-docker-ui`, which starts Streamlit in a container and runs Playwright on the host against it.
- **Fully in Docker:** `make e2e-docker` runs both Streamlit and Playwright in Docker (see `docker/docker-compose.e2e.yml`).
- **UI in Docker, Playwright local:** `make e2e-docker-ui` starts the Streamlit UI in a container and runs the E2E tests locally.

## Troubleshooting

| Issue | What to do |
|-------|------------|
| "Executable doesn't exist" for Chromium | Run `uv run playwright install chromium`. |
| Streamlit fails to start in time | Ensure port 8501 is free, or set `STREAMLIT_PORT` to another port. |
| Tests need the API (Run Jobs, Home metrics, etc.) | The app expects the API at `http://localhost:8000`. Start it with `make api` if you run those flows. |

For more on the app and config, see [architecture.md](architecture.md) and [user_guide.md](user_guide.md).
