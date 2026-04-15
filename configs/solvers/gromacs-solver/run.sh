#!/usr/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
DATA_DIR="${REPO_ROOT}/configs/solvers/gromacs-solver/data"
# Ephemeral run directory (removed after a successful finish). If the script exits early, work/ may remain for debugging.
WORK_DIR="${DATA_DIR}/work"
mkdir -p "${DATA_DIR}"
rm -rf "${WORK_DIR}"
mkdir -p "${WORK_DIR}"

if command -v gmx &>/dev/null; then
    echo "gmx found on PATH"
elif [ -n "${GROMACS_DOCKER_IMAGE:-}" ]; then
    echo "Using gmx via Docker (${GROMACS_DOCKER_IMAGE})"
    # Bind-mount the repo at the same path so absolute paths work inside the container.
    gmx() {
        # shellcheck disable=SC2086
        # -i forwards stdin (needed for genion and other tools reading from a pipe).
        docker run --rm -i \
            -v "${REPO_ROOT}:${REPO_ROOT}" \
            -w "${WORK_DIR}" \
            ${GROMACS_DOCKER_EXTRA_ARGS:-} \
            "${GROMACS_DOCKER_IMAGE}" gmx "$@"
    }
else
    echo "gmx not found. Install GROMACS, or set GROMACS_DOCKER_IMAGE (see configs/systems/gromacs-docker.yaml)." >&2
    exit 1
fi

# GROMACS links to cuda and cuda toolkit at compile and runtime,
# so will need to make sure that the system this script is running on
# compiled them correctly to use GPU support.

# Use these env variables to set GPU vs CPU and core counts
USE_GPU=0
N_CORES=8
# Gromacs (as of 2026.1) uses a string with the indices of the GPUs you are using,
# i.e. if you have 3 GPUs should be set to 012. Can also select particular GPUs
# if wanted
GPU_IDS=0
N_GPUS=1

# Will default to CPU option commands, overwriting with GPU option commands if set
MDRUN_CORE_OPTIONS="-ntomp ${N_CORES}"

if [ "$USE_GPU" -eq 1 ]; then
    echo "Enabling GPU use as options"
    MDRUN_CORE_OPTIONS="-ntmpi ${N_GPUS} -ntomp ${N_CORES} -gpu_id ${GPU_IDS}"

fi

DATA_PATH="${DATA_DIR}/1d5q.pdb"
OUTPUT_PATH="${WORK_DIR}/1d5q.gro"
FIRST_1D5Q_MDP_PATH="$REPO_ROOT"/configs/solvers/gromacs-solver/1d5q.mdp
ENERGY_MIN_MDP_PATH="${REPO_ROOT}/configs/solvers/gromacs-solver/1d5q_energy_minimization.mdp"
NVT_MDP_PATH="${REPO_ROOT}/configs/solvers/gromacs-solver/1d5q_nvt.mdp"
NPT_MDP_PATH="${REPO_ROOT}/configs/solvers/gromacs-solver/1d5q_npt.mdp"
SIM_MDP_PATH="${REPO_ROOT}/configs/solvers/gromacs-solver/1d5q_sim.mdp"

if [ ! -f "${DATA_PATH}" ]; then
    echo "Missing input PDB: ${DATA_PATH}. Add 1d5q.pdb (e.g. from https://files.rcsb.org/download/1D5Q.pdb)." >&2
    exit 1
fi

cd "${WORK_DIR}"

# Prep .gro files
gmx pdb2gmx -ff gromos54a7 -p topol.top -water spc -ignh -f "${DATA_PATH}" -o "${OUTPUT_PATH}"
gmx editconf -f "${OUTPUT_PATH}" -o "${WORK_DIR}/1d5q_boxed.gro" -c -d 1.0 -bt dodecahedron

# Solvation and charge neutralization
gmx solvate -cp "${WORK_DIR}/1d5q_boxed.gro" -cs spc216.gro -o "${WORK_DIR}/1d5q_solvated.gro" -p topol.top
gmx grompp -f "${FIRST_1D5Q_MDP_PATH}" -c "${WORK_DIR}/1d5q_solvated.gro" -p topol.top -o "${WORK_DIR}/1d5q.tpr" -maxwarn 10
echo SOL | gmx genion -s "${WORK_DIR}/1d5q.tpr" -o "${WORK_DIR}/1d5q_solv_ions.gro" -p topol.top -pname NA -nname CL -neutral

# Minimize Energy
gmx grompp -f "${ENERGY_MIN_MDP_PATH}" -c 1d5q_solv_ions.gro -p topol.top -o em.tpr -maxwarn 5
gmx mdrun -v -deffnm em ${MDRUN_CORE_OPTIONS}

gmx grompp -f "${NVT_MDP_PATH}" -c em.gro -r em.gro -p topol.top -o nvt.tpr -maxwarn 5
gmx mdrun -v -deffnm nvt ${MDRUN_CORE_OPTIONS}

gmx grompp -f "${NPT_MDP_PATH}" -c nvt.gro -r nvt.gro -p topol.top -o npt.tpr -maxwarn 5
gmx mdrun -v -deffnm npt ${MDRUN_CORE_OPTIONS}

gmx grompp -f "${SIM_MDP_PATH}" -c npt.gro -t npt.cpt -p topol.top -o md.tpr -maxwarn 5
gmx mdrun -v -deffnm md ${MDRUN_CORE_OPTIONS}

# Get the energy out from the simulation data (stdout for harness), then remove ephemeral outputs.
cat "${WORK_DIR}/md.log"
rm -rf "${WORK_DIR}"
