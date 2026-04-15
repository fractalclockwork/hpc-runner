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

# SLURM + LAMMPS API integration test (RUN_SLURM_E2E=1; default DOCKER_SLURM_CONTAINER matches sci_slurm compose worker name — override if your project prefix differs; see docs/TESTING_SLURM.md)
test-slurm:
	RUN_SLURM_E2E=1 DOCKER_SLURM_CONTAINER=$${DOCKER_SLURM_CONTAINER:-sci_slurm-gpu-worker-1} uv run pytest src/api/tests/test_slurm_lammps.py -v -m slurm

# API tests (REST contracts; SLURM/LAMMPS when RUN_SLURM_E2E=1 — use test-slurm for gated file)
test-api:
	uv run pytest src/api/tests -q

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
# Services (stop / start / restart API and UI)
# ---------------------------------------------------------------------------

# Stop API (port 8000) and UI (port 8501)
stop-services:
	./scripts/stop-services.sh

# Start API and UI in background; logs: .api.log, .ui.log; PIDs: .api.pid, .ui.pid
start-services:
	@nohup uv run uvicorn basic_restapi.fastapi_app:app --reload --port 8000 >> .api.log 2>&1 & echo $$! > .api.pid
	@nohup uv run streamlit run src/ui/app.py --server.port 8501 --server.headless true >> .ui.log 2>&1 & echo $$! > .ui.pid
	@echo "API (8000) and UI (8501) started in background. Logs: .api.log, .ui.log"

# Same as start-services but loads slurm-lammps.env (if present) and exports SLURM/LAMMPS vars for the API
start-services-slurm:
	@bash scripts/start-services-slurm.sh

# Stop then start API and UI in background
restart-services: stop-services
	@$(MAKE) start-services

restart-services-slurm: stop-services
	@$(MAKE) start-services-slurm

# ---------------------------------------------------------------------------
# Docker Slurm cluster (external checkout, e.g. sci_slurm)
# ---------------------------------------------------------------------------
# Directory that contains docker-compose.yml for your Slurm stack. Default is a
# sci_slurm symlink next to this Makefile; override if your clone lives elsewhere:
#   make slurm-up SLURM_COMPOSE_DIR=/path/to/sci_slurm
# Optional extra args: make slurm-up SLURM_COMPOSE_EXTRA=--build
# See docs/TESTING_SLURM.md

SLURM_COMPOSE_DIR ?= sci_slurm
SLURM_COMPOSE_EXTRA ?=

slurm-up:
	@if [ ! -d "$(SLURM_COMPOSE_DIR)" ]; then \
	  echo "ERROR: SLURM_COMPOSE_DIR=$(SLURM_COMPOSE_DIR) not found."; \
	  echo "Clone or symlink your Slurm stack (e.g. sci_slurm) here, or set SLURM_COMPOSE_DIR. See docs/TESTING_SLURM.md"; \
	  exit 1; \
	fi
	cd "$(SLURM_COMPOSE_DIR)" && docker compose up -d $(SLURM_COMPOSE_EXTRA)

slurm-down:
	@if [ ! -d "$(SLURM_COMPOSE_DIR)" ]; then \
	  echo "ERROR: SLURM_COMPOSE_DIR=$(SLURM_COMPOSE_DIR) not found."; \
	  exit 1; \
	fi
	cd "$(SLURM_COMPOSE_DIR)" && docker compose down

slurm-ps:
	@if [ ! -d "$(SLURM_COMPOSE_DIR)" ]; then \
	  echo "ERROR: SLURM_COMPOSE_DIR=$(SLURM_COMPOSE_DIR) not found."; \
	  exit 1; \
	fi
	cd "$(SLURM_COMPOSE_DIR)" && docker compose ps

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------

# Build the Docker image
docker-build:
	docker build -f docker/Dockerfile -t dow-workspace .

# Run the API container (port 8000)
docker-run:
	docker run --rm -p 8000:8000 -v $(PWD)/data:/app/data dow-workspace

# Run tests inside container
docker-test:
	docker build -f docker/Dockerfile -t dow-workspace . && docker run --rm dow-workspace uv run pytest src/core/tests -q

# Build Playwright image for E2E tests
docker-build-playwright:
	docker build -f docker/Dockerfile.playwright -t dow-workspace-playwright .

# Run API via docker-compose
docker-up:
	docker compose -f docker/docker-compose.yml up --build

# Run Streamlit UI in Docker (port 8501)
docker-ui:
	docker run --rm -p 8501:8501 -v $(PWD)/data:/app/data dow-workspace uv run streamlit run src/ui/app.py --server.port 8501 --server.address 0.0.0.0

# Install Playwright Chromium only (idempotent). Use alone if you run pytest without Make.
playwright-chromium:
	uv run playwright install chromium

# E2E: one command — download Chromium if needed, then run tests (Streamlit auto-started in conftest).
# Note: pytest's --browser chromium only *selects* Chromium; it does not install it. The line above does.
test-e2e:
	uv run playwright install chromium
	uv run pytest src/ui/tests/e2e -v --browser chromium

# Run Playwright E2E tests in Docker (Streamlit + Playwright containers)
test-e2e-docker:
	docker compose -f docker/docker-compose.e2e.yml up --build --abort-on-container-exit

# Run Streamlit UI in Docker, then run E2E tests against it (local Playwright)
test-e2e-docker-ui: playwright-chromium
	@cid=$$(docker run -d -p 8501:8501 -v $(PWD)/data:/app/data dow-workspace uv run streamlit run src/ui/app.py --server.port 8501 --server.address 0.0.0.0); \
	sleep 8; \
	STREAMLIT_ALREADY_RUNNING=1 uv run pytest src/ui/tests/e2e -v --browser chromium; \
	exit_code=$$?; \
	docker rm -f $$cid 2>/dev/null; \
	exit $$exit_code

# Aliases (deprecated names; prefer test-e2e*)
e2e: test-e2e
e2e-docker: test-e2e-docker
e2e-docker-ui: test-e2e-docker-ui

# Validate Docker images (build + API health check)
docker-validate:
	./scripts/validate-docker.sh

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

.PHONY: sync resync test test-core testv test-cov test-api test-slurm playwright-chromium test-e2e test-e2e-docker test-e2e-docker-ui e2e e2e-docker e2e-docker-ui runner api ui stop-services start-services start-services-slurm restart-services restart-services-slurm slurm-up slurm-down slurm-ps docker-build docker-run docker-test docker-build-playwright docker-up docker-ui docker-validate tree list lint fix clean purge clear-db default

# Default target
default: sync

