#!/usr/bin/env bash
# OpenMM solver dispatcher.
# Reads EXECUTION_MODE from the system environment (set via configs/systems/default.yaml).
#   local  (default) -> run simulate.py directly; stdout flows to the runner
#   slurm            -> submit slurm_job.sh via sbatch --wait, then re-print the
#                       job output so the runner can capture metrics from stdout

set -e

EXECUTION_MODE="${EXECUTION_MODE:-local}"

if [[ "$EXECUTION_MODE" == "slurm" ]]; then
    sbatch --wait \
        --partition="${SLURM_PARTITION:-gpu}" \
        --gpus="${SLURM_GPUS:-1}" \
        --ntasks="${SLURM_NTASKS:-8}" \
        --time="${SLURM_TIME:-01:00:00}" \
        --output=slurm_output.txt \
        --error=slurm_output.txt \
        slurm_job.sh
    cat slurm_output.txt
else
    python3 simulate.py
fi
