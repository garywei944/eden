# ---------- base image ----------
ARG BASE_IMAGE=debian:12

FROM ${BASE_IMAGE}

# ---------- build mode ----------
ARG MODE
ENV MODE=${MODE}

SHELL ["/bin/bash", "-euxo", "pipefail", "-c"]

# --------------------------------------------------
# Base packages (never install sudo here)
# --------------------------------------------------
RUN \
    if command -v apt-get >/dev/null; then \
    . /etc/os-release; \
    if [[ "$VERSION_CODENAME" == "buster" ]]; then \
    sed -i \
    -e 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' \
    -e 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' \
    /etc/apt/sources.list; \
    echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid; \
    fi; \
    apt-get update; \
    apt-get install -y bash ca-certificates; \
    rm -rf /var/lib/apt/lists/*; \
    elif command -v pacman >/dev/null; then \
    pacman -Sy --noconfirm bash ca-certificates; \
    pacman -Scc --noconfirm; \
    fi


# --------------------------------------------------
# Conditional sudo + users
# --------------------------------------------------
RUN if [[ "$MODE" != "root" ]]; then \
    if command -v apt-get >/dev/null; then \
    apt-get update && apt-get install -y sudo && rm -rf /var/lib/apt/lists/*; \
    elif command -v pacman >/dev/null; then \
    pacman -Sy --noconfirm sudo && pacman -Scc --noconfirm; \
    fi; \
    useradd -m eva -u 1001; \
    useradd -m adam -u 1002; \
    echo "eva ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/eva; \
    chmod 0440 /etc/sudoers.d/eva; \
    fi

# necessary build-essentials has to be presented for user 'adam'
RUN if [[ "$MODE" == "adam" ]]; then \
    if command -v apt-get >/dev/null; then \
    apt-get update && apt-get install -y \
    procps \
    build-essential \
    && rm -rf /var/lib/apt/lists/*; \
    elif command -v pacman >/dev/null; then \
    pacman -Sy --noconfirm \
    procps-ng \
    base-devel \
    && pacman -Scc --noconfirm; \
    fi; \
    fi

# --------------------------------------------------
# Copy repo & default command
# --------------------------------------------------
COPY . /eden
RUN chmod 777 /eden
WORKDIR /eden
CMD ["bash", "eva"]
