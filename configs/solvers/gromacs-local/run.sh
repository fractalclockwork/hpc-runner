#!/usr/bin/bash

set -euo pipefail

if which gmx &>/dev/null; then
    echo "gmx found"
else
    echo "gmx not found. you can use the alias command to set gmx if its installed on the target system or avaialbale as a docker image (i.e. alias gmx='alias gmx='docker run --rm --gpus all -v $(pwd):/workspace -w /workspace gromacs/gromacs gmx''"
    return 0
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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
DATA_DIR="${REPO_ROOT}/configs/solvers/gromacs-local/data"
DATA_PATH="${DATA_DIR}/1d5q.pdb"
OUTPUT_PATH="${REPO_ROOT}/data/1d5q.gro"
FIRST_1D5Q_MDP_PATH="$REPO_ROOT"/configs/solvers/gromacs-local/1d5q.mdp
ENERGY_MIN_MDP_PATH="${REPO_ROOT}/configs/solvers/gromacs-local/1d5q_energy_minimization.mdp"
NVT_MDP_PATH="${REPO_ROOT}/configs/solvers/gromacs-local/1d5q_nvt.mdp"
NPT_MDP_PATH="${REPO_ROOT}/configs/solvers/gromacs-local/1d5q_npt.mdp"
SIM_MDP_PATH="${REPO_ROOT}/configs/solvers/gromacs-local/1d5q_sim.mdp"


cd "${DATA_DIR}"

# Prep .gro files
gmx pdb2gmx -ff gromos54a7 -p topol.top -water spc -ignh -f "${DATA_PATH}" -o "${OUTPUT_PATH}"
gmx editconf -f "${OUTPUT_PATH}" -o "${DATA_DIR}/1d5q_boxed.gro" -c -d 1.0 -bt dodecahedron

# Solvation and charge neutralization
gmx solvate -cp "${DATA_DIR}/1d5q_boxed.gro" -cs spc216.gro -o "${DATA_DIR}/1d5q_solvated.gro" -p topol.top
gmx grompp -f "${FIRST_1D5Q_MDP_PATH}" -c "${DATA_DIR}/1d5q_solvated.gro" -p topol.top -o "${DATA_DIR}/1d5q.tpr" -maxwarn 10
echo SOL | gmx genion -s "${DATA_DIR}/1d5q.tpr" -o "${DATA_DIR}/1d5q_solv_ions.gro" -p topol.top -pname NA -nname CL -neutral

# Minimize Energy
gmx grompp -f "${ENERGY_MIN_MDP_PATH}" -c 1d5q_solv_ions.gro -p topol.top -o em.tpr -maxwarn 5
gmx mdrun -v -deffnm em ${MDRUN_CORE_OPTIONS}

gmx grompp -f "${NVT_MDP_PATH}" -c em.gro -r em.gro -p topol.top -o nvt.tpr -maxwarn 5
gmx mdrun -v -deffnm nvt ${MDRUN_CORE_OPTIONS}

gmx grompp -f "${NPT_MDP_PATH}" -c nvt.gro -r nvt.gro -p topol.top -o npt.tpr -maxwarn 5
gmx mdrun -v -deffnm npt ${MDRUN_CORE_OPTIONS}

gmx grompp -f "${SIM_MDP_PATH}" -c npt.gro -t npt.cpt -p topol.top -o md.tpr -maxwarn 5
gmx mdrun -v -deffnm md ${MDRUN_CORE_OPTIONS}

# Get the energy out from the simulation data
cat "${DATA_DIR}/sim.md"
