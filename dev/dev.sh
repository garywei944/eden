#!/usr/bin/env bash

set -euxo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
PROJECT_ROOT="$(realpath "${SCRIPT_DIR}"/..)"
export PROJECT_ROOT

cd ${PROJECT_ROOT}

BASE_IMAGE=${BASE_IMAGE:-debian:12}
export BASE_IMAGE

# Build and start (first time or after environment.yml changes)
docker compose -f "${PROJECT_ROOT}/dev/docker-compose.yml" build
docker compose -f "${PROJECT_ROOT}/dev/docker-compose.yml" run --rm eden
