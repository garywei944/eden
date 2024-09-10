#!/bin/bash

# Install python
export MAMBA_ROOT_PREFIX="$HOME/micromamba"

eval "$(micromamba shell hook --shell bash)"

micromamba -y create -f environment.yml
micromamba activate eden
