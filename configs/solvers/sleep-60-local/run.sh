#!/usr/bin/env bash
# Local subprocess sleep — for monitoring and cancel tests on dev-system (no SLURM).
# Uses same HARNESS_SOLVER_WALL_SECONDS convention as Slurm batch scripts (see docs/slurm_lammps_e2e.md).
set -euo pipefail

SECS="${LOCAL_SLEEP_SECONDS:-60}"

_harness_monotonic_now() {
  local x
  x=$(date +%s.%N 2>/dev/null || true)
  if [[ -n "${x}" ]]; then
    echo "${x}"
    return
  fi
  if [[ -n "${EPOCHREALTIME:-}" ]]; then
    echo "${EPOCHREALTIME}"
    return
  fi
  date +%s
}

echo "sleep-60-local: starting sleep for ${SECS}s"
t0=$(_harness_monotonic_now)
sleep "${SECS}"
t1=$(_harness_monotonic_now)
echo "HARNESS_SOLVER_WALL_SECONDS=$(awk -v a="${t0}" -v b="${t1}" 'BEGIN{print b-a}')"
echo "sleep-60-local: finished"
exit 0
