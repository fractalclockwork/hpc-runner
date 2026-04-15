#!/usr/bin/env bash
# SLURM batch job that sleeps (default 60s) — for monitoring and cancel tests.
# Same Docker/host sbatch flow as lammps-slurm; emits HARNESS_* lines for the runner.
set -euo pipefail

if [[ "${RUN_SLURM_E2E:-}" != "1" ]]; then
  echo "SKIP: set RUN_SLURM_E2E=1 for sleep-60-slurm (see docs/TESTING_SLURM.md)"
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
WORK_HOST="${SLURM_SLEEP_WORK_HOST:-${REPO_ROOT}/docker/slurm_sleep/work}"
SBATCH_TEMPLATE="${REPO_ROOT}/docker/slurm_sleep/sbatch_sleep60.sh"
DOCKER_USE_SBATCH="${SLURM_SLEEP_USE_SBATCH:-${LAMMPS_USE_SBATCH:-1}}"
SECONDS_SLEEP="${SLURM_SLEEP_SECONDS:-60}"

if [[ ! -f "$SBATCH_TEMPLATE" ]]; then
  echo "ERROR: sbatch template missing: $SBATCH_TEMPLATE" >&2
  exit 1
fi

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
  sed "s|__SLEEP_SECONDS__|${SECONDS_SLEEP}|g" "${SBATCH_TEMPLATE}" > "${WORK_HOST}/sbatch_sleep60.sh"

  if [[ "${DOCKER_USE_SBATCH}" == "1" ]]; then
    JOBDIR="/tmp/sleep-60-slurm-harness-$(date +%s)-$$"
    docker exec "${SUBMIT}" bash -lc "mkdir -p '${JOBDIR}'"
    docker cp "${WORK_HOST}/sbatch_sleep60.sh" "${SUBMIT}:${JOBDIR}/sbatch_sleep60.sh"
    docker exec "${SUBMIT}" bash -lc "chmod +x '${JOBDIR}/sbatch_sleep60.sh'"

    out="$(docker exec "${SUBMIT}" bash -lc "cd '${JOBDIR}' && sbatch sbatch_sleep60.sh" 2>&1)" || true
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

  echo "ERROR: sleep-60-slurm requires sbatch (set SLURM_SLEEP_USE_SBATCH=1 or LAMMPS_USE_SBATCH=1)" >&2
  exit 1
fi

# Host SLURM (no Docker)
mkdir -p "${WORK_HOST}"
sed "s|__SLEEP_SECONDS__|${SECONDS_SLEEP}|g" "${SBATCH_TEMPLATE}" > "${WORK_HOST}/sbatch_sleep60.sh"
chmod +x "${WORK_HOST}/sbatch_sleep60.sh"
cd "${WORK_HOST}"
out="$(sbatch ./sbatch_sleep60.sh 2>&1)" || true
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
