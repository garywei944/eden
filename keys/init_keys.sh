#!/usr/bin/env bash

DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null && pwd)
cd "$DIR" || exit

if ! unzip keys.zip; then
    echo "Error: Failed to unzip keys.zip"
    exit 1
fi
chmod +x config_keys.sh
./config_keys.sh

shopt -s extglob dotglob
rm -- !(init_keys.sh|keys.zip)
