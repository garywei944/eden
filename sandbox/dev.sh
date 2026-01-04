#!/usr/bin/env bash
set -euo pipefail

# -------------------------------------------------
# Usage
# -------------------------------------------------
usage() {
  cat <<EOF
Usage:
  ./dev.sh <arch|debian10|debian12>

Examples:
  ./dev.sh arch
  ./dev.sh debian10
  ./dev.sh debian12
EOF
  exit 1
}

# -------------------------------------------------
# Args
# -------------------------------------------------
DISTRO="${1:-}"
[[ -z "${DISTRO}" ]] && usage

# -------------------------------------------------
# Project paths
# -------------------------------------------------
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
PROJECT_ROOT="$(realpath "${SCRIPT_DIR}")"
CONTAINER_NAME="eden-dev-${DISTRO}"

# -------------------------------------------------
# Image selection
# -------------------------------------------------
case "${DISTRO}" in
arch)
  IMAGE="archlinux:latest"
  SHELL="/bin/bash"
  ;;
debian10)
  IMAGE="debian:10"
  SHELL="/bin/bash"
  ;;
debian12)
  IMAGE="debian:12"
  SHELL="/bin/bash"
  ;;
*)
  echo "Unknown distro: ${DISTRO}" >&2
  usage
  ;;
esac

# -------------------------------------------------
# Run container
# -------------------------------------------------
docker run --rm -it \
  --name "${CONTAINER_NAME}" \
  -v "${PROJECT_ROOT}:/eden" \
  -w /eden \
  "${IMAGE}" \
  "${SHELL}"
