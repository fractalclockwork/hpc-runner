#!/usr/bin/env bash
# Slurm job script for openmm-solver.
# Submitted by run.sh via: sbatch --wait [--partition ...] slurm_job.sh
# SBATCH directives for resources are passed as CLI flags from run.sh so they
# can be overridden per-system via env vars without modifying this file.
#SBATCH --job-name=openmm-solver

set -e

# Activate the shared uv venv — no conda needed
VENV_PATH="${VENV_PATH:-/home/shreepatel527/capstone/DOW-1-26/.venv}"
source "${VENV_PATH}/bin/activate"

python3 simulate.py
