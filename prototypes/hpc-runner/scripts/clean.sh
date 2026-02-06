#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "Cleaning project at $ROOT"

# Remove virtual env, builds, lockfile, and distribution artifacts
rm -rf "$ROOT/.venv" "$ROOT/dist" "$ROOT/build" "$ROOT"/*.egg-info "$ROOT/uv.lock"

# Remove editable-install artifacts in any venv layout
rm -f "$ROOT/.venv"/lib/python*/site-packages/*.egg-link || true
rm -f "$ROOT/.venv"/lib/python*/site-packages/_*.pth || true

# Remove Python bytecode caches
find "$ROOT" -name "__pycache__" -type d -exec rm -rf {} + || true
find "$ROOT" -name "*.pyc" -delete || true

# Remove stray test directories created during debugging
rm -rf "$ROOT/test" || true

echo "Clean complete"

