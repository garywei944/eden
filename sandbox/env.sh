#!/bin/bash

export MAMBA_ROOT_PREFIX="$HOME/micromamba"

eval "$(micromamba shell hook --shell bash)"

micromamba -y create -n eden python=3.12 pip -c conda-forge
micromamba activate eden
