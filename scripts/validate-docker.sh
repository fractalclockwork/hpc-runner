#!/usr/bin/env bash
# Validate Docker images: build API + Playwright, run API, verify /api/solvers returns 200.
# Run from project root. Exit 0 on success, 1 on failure.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

VAL_PORT="${VAL_PORT:-18000}"

echo "=== Building API image ==="
docker build -f docker/Dockerfile -t dow-workspace .

echo "=== Building Playwright image ==="
docker build -f docker/Dockerfile.playwright -t dow-workspace-playwright .

echo "=== Starting API container on port $VAL_PORT ==="
CID=$(docker run -d -p "$VAL_PORT:8000" -v "$(pwd)/data:/app/data" dow-workspace)

cleanup() {
  docker rm -f "$CID" 2>/dev/null || true
}
trap cleanup EXIT

echo "=== Waiting for API to be ready ==="
for i in $(seq 1 30); do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$VAL_PORT/api/solvers" 2>/dev/null || echo "000")
  if [ "$CODE" = "200" ]; then
    echo "API ready after ${i}s"
    break
  fi
  if [ "$i" -eq 30 ]; then
    echo "ERROR: API did not respond with 200 within 30s (last code: $CODE)"
    docker logs "$CID" 2>&1 | tail -20
    exit 1
  fi
  sleep 1
done

echo "=== Validation passed ==="
exit 0
