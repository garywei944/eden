#!/usr/bin/env bash

set -euxo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
PROJECT_ROOT="$(realpath "${SCRIPT_DIR}")"

SHELL="${SHELL:-/bin/bash}"
IMAGE="${IMAGE:-archlinux:latest}"

docker run --rm -it \
  --name eden-dev \
  -v "${PROJECT_ROOT}:/eden" \
  -w /eden \
  "${IMAGE}" \
  "${SHELL}"
