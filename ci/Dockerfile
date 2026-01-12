ARG BASE_IMAGE
ARG MODE
FROM ${BASE_IMAGE}

SHELL ["/bin/bash", "-euxo", "pipefail", "-c"]

# --------------------------------------------------
# Base packages (never install sudo here)
# --------------------------------------------------
RUN \
    if command -v apt-get >/dev/null; then \
    apt-get update && apt-get install -y bash ca-certificates && rm -rf /var/lib/apt/lists/*; \
    elif command -v pacman >/dev/null; then \
    pacman -Sy --noconfirm bash ca-certificates && pacman -Scc --noconfirm; \
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
    useradd -m eva -u 1000; \
    useradd -m adam -u 1001; \
    echo "eva ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/eva; \
    chmod 0440 /etc/sudoers.d/eva; \
    fi

WORKDIR /eden
COPY . /eden
CMD ["bash", "eva"]
