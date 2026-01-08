#!/usr/bin/env bash

set -euo pipefail

# This script is POSIX-compliant

log() {
  echo "[eden] $*" >&2
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
PROJECT_ROOT="$(realpath "${SCRIPT_DIR}")"

EDEN_HOME="${PROJECT_ROOT}/.eden"
ENV_NAME="eden"

# mamba env
export MAMBA_ROOT_PREFIX="${EDEN_HOME}/micromamba"
export PATH="${MAMBA_ROOT_PREFIX}/bin:${PATH}"

mkdir -p "${MAMBA_ROOT_PREFIX}"

log "MAMBA_ROOT_PREFIX: ${MAMBA_ROOT_PREFIX}"
log "PATH: ${PATH}"

install_micromamba() {
  if [[ -x "${MAMBA_ROOT_PREFIX}/bin/micromamba" ]]; then
    return
  fi

  log "installing micromamba (silent)"

  BIN_FOLDER="${MAMBA_ROOT_PREFIX}/bin" \
    INIT_YES=no \
    CONDA_FORGE_YES=no \
    "${SHELL}" <(curl -fsSL https://micro.mamba.pm/install.sh) </dev/null
}

init_micromamba() {
  export MAMBA_EXE="${MAMBA_ROOT_PREFIX}/bin/micromamba"
  __mamba_setup="$("$MAMBA_EXE" shell hook --shell bash --root-prefix "${MAMBA_ROOT_PREFIX}" 2>/dev/null)"
  if [[ $? -eq 0 ]]; then
    eval "${__mamba_setup}"
  else
    alias micromamba="${MAMBA_EXE}" # Fallback on help from micromamba activate
  fi
  unset __mamba_setup

  log "initialized micromamba"
}

create_env() {
  if micromamba env list | awk '{print $1}' | grep -qx "${ENV_NAME}"; then
    return
  fi

  log "creating eden environment"
  micromamba create -y -f "${PROJECT_ROOT}/environment.yml"
}

main() {
  install_micromamba
  init_micromamba
  create_env

  cd ${PROJECT_ROOT}
  exec micromamba run -n "${ENV_NAME}" python -m eden "$@"
}

main "$@"
