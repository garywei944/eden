#!/bin/bash

# Install python
export MAMBA_ROOT_PREFIX="$HOME/micromamba"

eval "$(micromamba shell hook --shell bash)"

micromamba -y create -n eden -c conda-forge \
    "python>=3.10" \
    psutil \
    distro \
    attrs \
    absl-py
micromamba activate eden
pip install sh
