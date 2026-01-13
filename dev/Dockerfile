# syntax=docker/dockerfile:1

ARG BASE_IMAGE=debian:12

FROM ${BASE_IMAGE}

SHELL ["/bin/bash", "-euxo", "pipefail", "-c"]

# Detect distro and install dependencies accordingly
RUN if command -v apt-get >/dev/null 2>&1; then \
    . /etc/os-release; \
    if [[ "$VERSION_CODENAME" == "buster" ]]; then \
    sed -i \
    -e 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' \
    -e 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' \
    /etc/apt/sources.list; \
    echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid; \
    fi; \
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
    sudo \
    build-essential \
    zip unzip \
    cmake \
    openssh-client openssh-server \
    libgmp-dev libmpfr-dev libreadline-dev zlib1g-dev \
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
    sudo \
    base-devel \
    zip unzip \
    cmake \
    openssh \
    && pacman -Scc --noconfirm; \
    else \
    echo "Unsupported base image" && exit 1; \
    fi

RUN useradd -m eva -u 1001; \
    useradd -m adam -u 1002; \
    echo "eva ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/eva; \
    chmod 0440 /etc/sudoers.d/eva;

# # Set up micromamba
# ENV MAMBA_ROOT_PREFIX=/eden/.eden/micromamba
# ENV PATH="${MAMBA_ROOT_PREFIX}/bin:${PATH}"

# # Install micromamba
# RUN curl -fsSL https://micro.mamba.pm/install.sh | \
#     BIN_FOLDER="${MAMBA_ROOT_PREFIX}/bin" \
#     INIT_YES=no \
#     CONDA_FORGE_YES=no \
#     /bin/bash

# # Copy environment file and create the conda environment
# # This layer gets cached unless environment.yml changes
# WORKDIR /eden
# COPY environment.yml .
# RUN micromamba create -y -f environment.yml && \
#     micromamba clean --all --yes

# # Set up shell initialization for interactive use
# RUN micromamba shell init -s bash -p "${MAMBA_ROOT_PREFIX}" && \
#     echo "micromamba activate eden" >> /root/.bashrc

# ENV ENV_NAME=eden

# Default to bash for development
CMD ["/bin/bash"]
