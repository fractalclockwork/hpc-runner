#!/usr/bin/env bash
# Start API (8000) + Streamlit UI (8501) with SLURM/LAMMPS env for the harness.
# Usage: from repo root — ./scripts/start-services-slurm.sh
#        or: make start-services-slurm
#
# Environment file (optional): slurm-lammps.env in repo root (copy from slurm-lammps.env.example)

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ENV_FILE="${SLURM_LAMMPS_ENV:-$ROOT/slurm-lammps.env}"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
  echo "Loaded: $ENV_FILE"
fi

export RUN_SLURM_E2E="${RUN_SLURM_E2E:-1}"

if [[ -z "${DOCKER_SLURM_CONTAINER:-}" ]]; then
  echo "Warning: DOCKER_SLURM_CONTAINER is not set. Copy slurm-lammps.env.example to slurm-lammps.env or export it." >&2
  echo "         Jobs using docker exec will fail until it is set." >&2
fi

echo "Starting API with RUN_SLURM_E2E=${RUN_SLURM_E2E} DOCKER_SLURM_CONTAINER=${DOCKER_SLURM_CONTAINER:-<unset>} ..."

nohup uv run uvicorn basic_restapi.fastapi_app:app --reload --port 8000 >> .api.log 2>&1 &
echo $! > .api.pid

nohup uv run streamlit run src/ui/app.py --server.port 8501 --server.headless true >> .ui.log 2>&1 &
echo $! > .ui.pid

echo "API (8000) and UI (8501) started. PIDs: .api.pid, .ui.pid — logs: .api.log, .ui.log"
echo "Run solvers from the UI (Run Solvers) or: curl -X POST http://localhost:8000/api/run_solvers -H 'Content-Type: application/json' -d '{\"solvers\":[{\"name\":\"lammps-slurm\",\"system\":\"sci-slurm-lammps\"}]}'"
