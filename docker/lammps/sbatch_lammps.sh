#!/bin/bash
#SBATCH --job-name=lammps-harness
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err
#SBATCH --ntasks=1
#SBATCH --time=00:15:00

# Harness replaces __LAMMPS_BIN__ before submit (see docs/slurm_lammps_e2e.md).
set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-.}"
exec __LAMMPS_BIN__ -in in.lammps
