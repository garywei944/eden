#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
PROJECT_ROOT="$(realpath "${SCRIPT_DIR}")"

EDEN_HOME="${PROJECT_ROOT}/.eden"
ENV_NAME="eden"

export MAMBA_ROOT_PREFIX="${EDEN_HOME}/micromamba"
export PATH="${MAMBA_ROOT_PREFIX}/bin:${PATH}"

log() {
  echo "[eden] $*" >&2
}

ensure_micromamba() {
  if command -v micromamba >/dev/null; then
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
  __mamba_setup="$("$MAMBA_EXE" shell hook --shell bash --root-prefix "$MAMBA_ROOT_PREFIX" 2>/dev/null)"
  if [ $? -eq 0 ]; then
    eval "$__mamba_setup"
  else
    alias micromamba="$MAMBA_EXE" # Fallback on help from micromamba activate
  fi
  unset __mamba_setup

  log "initialized micromamba"
}

ensure_env() {
  if micromamba env list | awk '{print $1}' | grep -qx "${ENV_NAME}"; then
    return
  fi

  log "creating eden environment"
  micromamba create -y -f "${PROJECT_ROOT}/environment.yml"
}

main() {
  ensure_micromamba
  init_micromamba
  ensure_env
  exec micromamba run -n "${ENV_NAME}" python -m eden "$@"
}

main "$@"
