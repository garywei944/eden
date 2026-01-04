#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
PROJECT_ROOT="$(realpath "${SCRIPT_DIR}")"

EDEN_HOME="${PROJECT_ROOT}/.eden"
ENV_NAME="eden"

# mamba env
export MAMBA_ROOT_PREFIX="${EDEN_HOME}/micromamba"
export PATH="${MAMBA_ROOT_PREFIX}/bin:${PATH}"
