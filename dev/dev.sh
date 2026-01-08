#!/usr/bin/env bash

set -euxo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
PROJECT_ROOT="$(realpath "${SCRIPT_DIR}"/..)"
export PROJECT_ROOT

cd "${PROJECT_ROOT}"

COMPOSE_FILE="${PROJECT_ROOT}/dev/docker-compose.yml"

BASE_IMAGE=${BASE_IMAGE:-debian:12}
export BASE_IMAGE

CPUS="$(nproc).0"
export CPUS

# Build and start (first time or after environment.yml changes)
docker compose -f "${COMPOSE_FILE}" build
docker compose -f "${COMPOSE_FILE}" run --rm eden
