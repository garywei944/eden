#!/usr/bin/env bash

set -euxo pipefail

NO_CACHE_BUILD=0
while [[ "$#" -gt 0 ]]; do
  case $1 in
  -r | --no-cache)
    NO_CACHE_BUILD=1
    shift
    ;;
  *)
    echo "Unknown parameter passed: $1"
    exit 1
    ;;
  esac
done

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
PROJECT_ROOT="$(realpath "${SCRIPT_DIR}"/..)"
export PROJECT_ROOT

cd "${PROJECT_ROOT}"

COMPOSE_FILE="${PROJECT_ROOT}/dev/docker-compose.yml"

BASE_IMAGE=${BASE_IMAGE:-debian:12}
export BASE_IMAGE

CPUS="$(nproc).0"
export CPUS

build_options=()
if [[ "${NO_CACHE_BUILD}" -eq 1 ]]; then
  build_options+=("--no-cache")
fi

# Build and start (first time or after environment.yml changes)
docker compose -f "${COMPOSE_FILE}" build "${build_options[@]}"
docker compose -f "${COMPOSE_FILE}" run --rm eden
