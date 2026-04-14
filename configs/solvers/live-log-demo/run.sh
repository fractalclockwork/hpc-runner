#!/usr/bin/env bash
# Live-log demo solver: prints in stages so UI polling can show incremental output.

set -euo pipefail

SLEEP_SECONDS="${LIVE_LOG_SLEEP_SECONDS:-10}"

sleep "$SLEEP_SECONDS"
echo "Live log demo: step 1/3"
sleep "$SLEEP_SECONDS"
echo "Live log demo: step 2/3"
sleep "$SLEEP_SECONDS"
echo "Live log demo: step 3/3"
sleep "$SLEEP_SECONDS"
echo "Solver finished successfully"
