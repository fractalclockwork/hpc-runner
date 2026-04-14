#!/bin/bash
#SBATCH --job-name=harness-sleep60
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err
#SBATCH --ntasks=1
#SBATCH --time=00:10:00

# Long-running no-op for monitoring / cancel tests (see sleep-60-slurm solver).
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-.}"

# High-res wall clock for HARNESS_SOLVER_WALL_SECONDS (GNU date +%s.%N, else EPOCHREALTIME / %s).
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

echo "harness sleep job starting, sleeping __SLEEP_SECONDS__s"
t0=$(_harness_monotonic_now)
sleep "__SLEEP_SECONDS__"
t1=$(_harness_monotonic_now)
echo "HARNESS_SOLVER_WALL_SECONDS=$(awk -v a="${t0}" -v b="${t1}" 'BEGIN{print b-a}')"
echo "harness sleep job finished"
