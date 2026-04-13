#!/usr/bin/sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
DATA_DIR="${REPO_ROOT}/data"
DATA_PATH="${REPO_ROOT}/data/1d5q.pdb"
OUTPUT_PATH="${REPO_ROOT}/data/1d5q.gro"
1D5Q_MDP_PATH="${REPO_ROOT}/configs/solvers/gromacs-local/1d5q.mdp"
ENERGY_MIN_MDP_PATH="${REPO_ROOT}/configs/solvers/gromacs-local/1d5q_energy_minimization.mdp"
NVT_MDP_PATH="${REPO_ROOT}/configs/solvers/gromacs-local/1d5q_nvt.mdp"
NPT_1D5Q_MDP_PATH="${REPO_ROOT}/configs/solvers/gromacs-local/1d5q_npt.mdp"
SIM_1D5Q_MDP_PATH="${REPO_ROOT}/configs/solvers/gromacs-local/1d5q_sim.mdp"

# Prep .gro files
gmx pdb2gmx -ff gromos54a7 -p topol.top -water tip3p -ignh -f "${DATA_PATH}" -o "${OUTPUT_PATH}"
gmx editconf -f "${OUTPUT_PATH}" -o "${DATA_DIR}/1d5q_boxed.gro" -c -d 1.0 -bt dodecahedron

# Solvation and charge neutralization
gmx solvate -cp "${DATA_DIR}/1d5q_boxed.gro" -cs spc216.gro -o "${DATA_DIR}/1d5q_solvated.gro" -p topol.top
gmx grompp -f "${1D5Q_MDP_PATH}" -c "${DATA_DIR}/1d5q_solvated.gro" -p topol.top -o "${DATA_DIR}/1d5q.tpr"
gmx genion -s "${DATA_DIR}/1d5q.tpr" -o -"${DATA_DIR}/1d5q_solvated.gro" -p topol.top -pname NA -nname CL -neutral

# Minimize Energy
gmx grompp -f "${ENERGY_MIN_MDP_PATH}" -c 1AKI_solv_ions.gro -p topol.top -o em.tpr
gmx mdrun -v -deffnm em

gmx grompp -f "${NVT_MDP_PATH}" -c em.gro -r em.gro -p topol.top -o nvt.tpr
gmx mdrun -v -deffnm nvt

gmx grompp -f "${NPT_MDP_PATH}" -c nvt.gro -r nvt.gro -p topol.top -o npt.tpr
gmx mdrun -v -deffnm nvt

gmx grompp -f "${SIM_MDP_PATH}" -c npt.gro -t npt.cpt -p topol.top -o md.tpr
gmx mdrun -v -ntmpi 4 -deffnm md
