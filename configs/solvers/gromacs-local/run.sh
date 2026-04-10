#!/usr/bin/sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
DATA_PATH="${REPO_ROOT}/data/1d5q.pdb"
OUTPUT_PATH="${REPO_ROOT}/data/1d5q.gro"

gmx pdb2gmx -ff amber99sb-ildn -p topol.top -water tip3p -ignh -f "${DATA_PATH}" -o "${OUTPUT_PATH}"
gmx grompp -f 1d5q.mdp -c "${OUTPUT_PATH}" -p topol.top -o "${REPO_ROOT}/data/1d5q.tpr"
gmx mdrun -v -deffnm 1d5q -ntmpi 4
