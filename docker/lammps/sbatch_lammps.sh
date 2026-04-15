#!/bin/bash
#SBATCH --job-name=lammps-harness
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err
#SBATCH --ntasks=1
#SBATCH --time=00:15:00

# Harness replaces __LAMMPS_BIN__ before submit (see docs/TESTING_SLURM.md).
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-.}"

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

t0=$(_harness_monotonic_now)
rc=0
__LAMMPS_BIN__ -in in.lammps || rc=$?
t1=$(_harness_monotonic_now)
echo "HARNESS_SOLVER_WALL_SECONDS=$(awk -v a="${t0}" -v b="${t1}" 'BEGIN{print b-a}')"
exit "${rc}"
