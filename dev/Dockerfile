# syntax=docker/dockerfile:1

ARG BASE_IMAGE=debian:12

FROM ${BASE_IMAGE}

# Detect distro and install dependencies accordingly
RUN if command -v apt-get >/dev/null 2>&1; then \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    bzip2 \
    git \
    vim \
    less \
    procps \
    && rm -rf /var/lib/apt/lists/*; \
    elif command -v pacman >/dev/null 2>&1; then \
    pacman -Syu --noconfirm \
    curl \
    ca-certificates \
    bzip2 \
    git \
    vim \
    less \
    procps-ng \
    && pacman -Scc --noconfirm; \
    else \
    echo "Unsupported base image" && exit 1; \
    fi

# Set up micromamba
ENV MAMBA_ROOT_PREFIX=/eden/micromamba
ENV PATH="${MAMBA_ROOT_PREFIX}/bin:${PATH}"

# Install micromamba
RUN curl -fsSL https://micro.mamba.pm/install.sh | \
    BIN_FOLDER="${MAMBA_ROOT_PREFIX}/bin" \
    INIT_YES=no \
    CONDA_FORGE_YES=no \
    /bin/bash

# Copy environment file and create the conda environment
# This layer gets cached unless environment.yml changes
WORKDIR /eden
COPY environment.yml .
RUN micromamba create -y -f environment.yml && \
    micromamba clean --all --yes

# Set up shell initialization for interactive use
RUN micromamba shell init -s bash -p "${MAMBA_ROOT_PREFIX}" && \
    echo "micromamba activate eden" >> /root/.bashrc

ENV ENV_NAME=eden

# Default to bash for development
CMD ["/bin/bash"]
