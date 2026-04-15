#!/usr/bin/env bash
# LAMMPS via SLURM — inputs under repo docker/lammps/ only (never write to external sci_slurm).
#
# Docker + SLURM (default): submit with sbatch, wait, print slurm-*.out/.err, exit with job exit code.
#   DOCKER_SLURM_CONTAINER — container with sbatch/squeue/sacct (often slurmctld or a login node)
#   DOCKER_SLURM_SUBMIT_CONTAINER — optional; defaults to DOCKER_SLURM_CONTAINER
#   LAMMPS_USE_SBATCH=1 (default when using Docker) — set to 0 for direct: docker exec … lmp -in …
# Host SLURM: runs in docker/lammps/work; LAMMPS_USE_SRUN=1 for srun, else lmp directly.
set -euo pipefail

if [[ "${RUN_SLURM_E2E:-}" != "1" ]]; then
  echo "SKIP: set RUN_SLURM_E2E=1 for a real SLURM/LAMMPS run (see docs/TESTING_SLURM.md)"
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
INPUT="${LAMMPS_INPUT:-${REPO_ROOT}/docker/lammps/in.lammps}"
WORK_HOST="${LAMMPS_WORK_HOST:-${REPO_ROOT}/docker/lammps/work}"
BIN="${LAMMPS_BIN:-lmp}"
SBATCH_TEMPLATE="${REPO_ROOT}/docker/lammps/sbatch_lammps.sh"
USE_SRUN="${LAMMPS_USE_SRUN:-0}"
# When using Docker, default to sbatch workflow (full SLURM example); override with LAMMPS_USE_SBATCH=0
DOCKER_USE_SBATCH="${LAMMPS_USE_SBATCH:-1}"

if [[ ! -f "$INPUT" ]]; then
  echo "ERROR: LAMMPS input not found: $INPUT" >&2
  exit 1
fi

# --- wait for Slurm job id $1 in container $2, timeout seconds $3 ---
_wait_job() {
  local jid=$1 cont=$2
  local max_wait="${SBATCH_WAIT_TIMEOUT:-600}"
  local elapsed=0
  while docker exec "${cont}" bash -lc "squeue -j '${jid}' -h 2>/dev/null | grep -q ."; do
    sleep 2
    elapsed=$((elapsed + 2))
    if [[ "${elapsed}" -ge "${max_wait}" ]]; then
      echo "ERROR: sbatch job ${jid} still in queue after ${max_wait}s" >&2
      return 1
    fi
  done
  sleep 1
}

# --- exit code from sacct for job $1 in container $2 ---
_job_exit_code() {
  local jid=$1 cont=$2
  local raw
  raw="$(docker exec "${cont}" bash -lc "sacct -j '${jid}' -n -X -o ExitCode 2>/dev/null | tail -1 | awk '{print \$1}'")"
  raw="${raw%%+*}"
  echo "${raw%%:*}"
}

if [[ -n "${DOCKER_SLURM_CONTAINER:-}" ]]; then
  mkdir -p "${WORK_HOST}"
  SUBMIT="${DOCKER_SLURM_SUBMIT_CONTAINER:-${DOCKER_SLURM_CONTAINER}}"
  cp -f "$INPUT" "${WORK_HOST}/in.lammps"

  if [[ "${DOCKER_USE_SBATCH}" == "1" ]]; then
    if [[ ! -f "${SBATCH_TEMPLATE}" ]]; then
      echo "ERROR: sbatch template missing: ${SBATCH_TEMPLATE}" >&2
      exit 1
    fi
    sed "s|__LAMMPS_BIN__|${BIN}|g" "${SBATCH_TEMPLATE}" > "${WORK_HOST}/sbatch_lammps.sh"
    JOBDIR="/tmp/lammps-harness-$(date +%s)-$$"
    docker exec "${SUBMIT}" bash -lc "mkdir -p '${JOBDIR}'"
    docker cp "${WORK_HOST}/in.lammps" "${SUBMIT}:${JOBDIR}/in.lammps"
    docker cp "${WORK_HOST}/sbatch_lammps.sh" "${SUBMIT}:${JOBDIR}/sbatch_lammps.sh"
    docker exec "${SUBMIT}" bash -lc "chmod +x '${JOBDIR}/sbatch_lammps.sh'"

    out="$(docker exec "${SUBMIT}" bash -lc "cd '${JOBDIR}' && sbatch sbatch_lammps.sh" 2>&1)" || true
    echo "${out}"
    if [[ "${out}" != *"Submitted batch job"* ]]; then
      echo "ERROR: sbatch failed: ${out}" >&2
      exit 1
    fi
    jid="$(echo "${out}" | sed -n 's/.*Submitted batch job \([0-9][0-9]*\).*/\1/p')"
    if [[ -z "${jid}" ]]; then
      echo "ERROR: could not parse Slurm job id from: ${out}" >&2
      exit 1
    fi
    # Machine-readable lines for harness (cancellation / stored run metadata); documented in TESTING_SLURM.md
    echo "HARNESS_SCHEDULER_BACKEND=slurm"
    echo "HARNESS_SLURM_JOB_ID=${jid}"
    echo "HARNESS_SUBMIT_CONTAINER=${SUBMIT}"
    _wait_job "${jid}" "${SUBMIT}" || exit 1

    echo "--- slurm-${jid}.out ---"
    docker exec "${SUBMIT}" bash -lc "cat '${JOBDIR}/slurm-${jid}.out'" 2>/dev/null || echo "(no stdout file)"
    echo "--- slurm-${jid}.err ---"
    docker exec "${SUBMIT}" bash -lc "cat '${JOBDIR}/slurm-${jid}.err'" 2>/dev/null || true

    ec="$(_job_exit_code "${jid}" "${SUBMIT}")"
    if [[ -z "${ec}" ]]; then
      echo "ERROR: sacct returned no ExitCode for job ${jid}" >&2
      exit 1
    fi
    exit "${ec}"
  fi

  # Direct run in container (no batch)
  docker exec "${DOCKER_SLURM_CONTAINER}" bash -lc "mkdir -p /tmp/lammps-smoke"
  docker cp "${WORK_HOST}/in.lammps" "${DOCKER_SLURM_CONTAINER}:/tmp/lammps-smoke/in.lammps"
  if [[ "$USE_SRUN" == "1" ]]; then
    docker exec "${DOCKER_SLURM_CONTAINER}" bash -lc "cd /tmp/lammps-smoke && srun -n 1 ${BIN} -in in.lammps"
  else
    docker exec "${DOCKER_SLURM_CONTAINER}" bash -lc "cd /tmp/lammps-smoke && ${BIN} -in in.lammps"
  fi
  exit 0
fi

# Host / shared SLURM (no Docker)
mkdir -p "${WORK_HOST}"
cp -f "$INPUT" "${WORK_HOST}/in.lammps"
cd "${WORK_HOST}"

if [[ "${LAMMPS_USE_SBATCH:-0}" == "1" ]]; then
  sed "s|__LAMMPS_BIN__|${BIN}|g" "${SBATCH_TEMPLATE}" > "${WORK_HOST}/sbatch_lammps.sh"
  chmod +x "${WORK_HOST}/sbatch_lammps.sh"
  cd "${WORK_HOST}"
  out="$(sbatch ./sbatch_lammps.sh 2>&1)" || true
  echo "${out}"
  jid="$(echo "${out}" | sed -n 's/.*Submitted batch job \([0-9][0-9]*\).*/\1/p')"
  [[ -n "${jid}" ]] || { echo "ERROR: sbatch failed: ${out}" >&2; exit 1; }
  echo "HARNESS_SCHEDULER_BACKEND=slurm"
  echo "HARNESS_SLURM_JOB_ID=${jid}"
  echo "HARNESS_SUBMIT_CONTAINER=host"
  while squeue -j "${jid}" -h 2>/dev/null | grep -q .; do sleep 2; done
  sleep 1
  echo "--- slurm-${jid}.out ---"
  cat "${WORK_HOST}/slurm-${jid}.out" 2>/dev/null || true
  echo "--- slurm-${jid}.err ---"
  cat "${WORK_HOST}/slurm-${jid}.err" 2>/dev/null || true
  raw="$(sacct -j "${jid}" -n -X -o ExitCode 2>/dev/null | tail -1 | awk '{print $1}')"
  raw="${raw%%+*}"
  ec="${raw%%:*}"
  exit "${ec}"
fi

if [[ "$USE_SRUN" == "1" ]]; then
  exec srun -n 1 "${BIN}" -in in.lammps
fi
exec "${BIN}" -in in.lammps
