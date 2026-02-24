# DOW‑1‑26 Makefile
# Workspace automation using uv
# All commands must be run from the workspace root.

# ---------------------------------------------------------------------------
# Core targets
# ---------------------------------------------------------------------------

# Create or update the workspace environment
sync:
	uv sync --all-extras --dev

# Remove environment and lockfile, then rebuild cleanly
resync:
	rm -rf .venv uv.lock
	uv sync --all-extras --dev

# ---------------------------------------------------------------------------
# Testing
# ---------------------------------------------------------------------------

# Run core tests
test:
	uv run pytest src/core/tests -q

# Run core tests (alias)
test-core:
	uv run pytest src/core/tests -q

# Run tests with verbose output
testv:
	uv run pytest src/core/tests -vv

# Run tests with coverage
test-cov:
	uv run pytest src/core/tests -v --cov=src/core/src/harness --cov-report=term-missing

# ---------------------------------------------------------------------------
# Project entrypoints
# ---------------------------------------------------------------------------

# Run the hpc-runner CLI
runner:
	uv run hpc-runner configs

# Run the REST API (FastAPI)
api:
	uv run uvicorn basic_restapi.fastapi_app:app --reload --port 8000

# Run the Streamlit UI
ui:
	uv run streamlit run src/ui/app.py

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------

# Build the Docker image
docker-build:
	docker build -t dow-workspace .

# Run the API container (port 8000)
docker-run:
	docker run --rm -p 8000:8000 -v $(PWD)/data:/app/data dow-workspace

# Run tests inside container
docker-test:
	docker build -t dow-workspace . && docker run --rm dow-workspace uv run pytest src/core/tests -q

# Build Playwright image for E2E tests
docker-build-playwright:
	docker build -f Dockerfile.playwright -t dow-workspace-playwright .

# Run Playwright E2E tests locally (starts Streamlit automatically)
e2e:
	uv run pytest src/ui/tests/e2e -v --browser chromium

# Run Playwright E2E tests in Docker (Streamlit + Playwright containers)
e2e-docker:
	docker compose -f docker-compose.e2e.yml up --build --abort-on-container-exit

# ---------------------------------------------------------------------------
# Developer utilities
# ---------------------------------------------------------------------------

# Show dependency tree
tree:
	uv tree

# List installed packages (uv-native)
list:
	uv pip list

# Format and lint using ruff
lint:
	uv run ruff check .

# Auto-fix lint issues
fix:
	uv run ruff check . --fix

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

# Remove caches, build artifacts, and temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .venv uv.lock .coverage htmlcov


# ---------------------------------------------------------------------------
# Purge 
# ---------------------------------------------------------------------------

purge:
	@echo "Purging all temporary files, caches, and venvs..."
	# Remove all virtual environments
	find . -type d -name ".venv" -prune -exec rm -rf {} +
	# Remove uv lockfiles everywhere
	find . -type f -name "uv.lock" -delete
	# Remove Python build artifacts
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -prune -exec rm -rf {} +
	find . -type d -name "build" -prune -exec rm -rf {} +
	find . -type d -name "dist" -prune -exec rm -rf {} +
	# Remove pytest caches
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	# Remove coverage artifacts
	find . -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	# Remove uv global caches
	rm -rf ~/.cache/uv
	rm -rf ~/.local/share/uv/python
	@echo "Purge complete."

# ---------------------------------------------------------------------------
# Pre-release
# ---------------------------------------------------------------------------

# Clear the harness database (run before release to reset run history)
clear-db:
	@echo "Clearing harness database..."
	rm -f data/harness.db
	@echo "Database cleared."

# ---------------------------------------------------------------------------
# Meta
# ---------------------------------------------------------------------------

# Default target
default: sync

