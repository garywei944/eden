#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
PROJECT_ROOT=$(realpath "$SCRIPT_DIR/..")
cd "$PROJECT_ROOT"

PYTHON_VERSION="3.14.2"
BUILD_DATE="20251217"

EDEN_HOME="${PROJECT_ROOT}/.eden"
PYTHON_DIR="${EDEN_HOME}/python"

tmp=""

log() {
	echo "[eden] $*"
}

die() {
	echo "[eden][error] $*" >&2
	exit 1
}

cleanup() {
	if [ -n "${tmp}" ]; then
		rm -rf "${tmp}"
	fi
}

trap cleanup EXIT

main() {
	if [ -x "${PYTHON_DIR}/bin/python3" ]; then
		log "portable python already installed"
		"${PYTHON_DIR}/bin/python3" -V
		exit 0
	fi

	command -v curl >/dev/null || die "curl not found"
	command -v tar >/dev/null || die "tar not found"

	local tag url

	tag="$(detect_platform)"
	url="https://github.com/indygreg/python-build-standalone/releases/download/${BUILD_DATE}/cpython-${PYTHON_VERSION}+${BUILD_DATE}-${tag}-install_only.tar.gz"

	log "platform: ${tag}"
	log "python version: ${PYTHON_VERSION}"
	log "install dir: ${PYTHON_DIR}"
	log "download url:"
	log "  ${url}"

	mkdir -p "${EDEN_HOME}"
	tmp="$(mktemp -d)"

	log "downloading..."
	curl -fL "${url}" -o "${tmp}/python.tar.gz"

	log "extracting..."
	tar -xzf "${tmp}/python.tar.gz" -C "${tmp}"

	log "installing..."
	mv "${tmp}/python" "${PYTHON_DIR}"

	log "done"
	"${PYTHON_DIR}/bin/python3" -V
}

main "$@"
