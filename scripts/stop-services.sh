#!/usr/bin/env bash
# Stop API (port 8000) and Streamlit UI (port 8501) processes.
# Run from project root. Idempotent; exit 0 even when no process is listening.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

API_PORT=8000
UI_PORT=8501

_kill_port() {
  local port=$1
  local name=$2
  local pids
  pids=$(lsof -ti:"$port" 2>/dev/null) || true
  if [ -n "$pids" ]; then
    echo "$pids" | xargs kill 2>/dev/null || true
    echo "Stopped $name (port $port)."
  fi
}

_kill_port "$API_PORT" "API"
_kill_port "$UI_PORT" "UI"

echo "Done. API (8000) and UI (8501) stopped if they were running."
