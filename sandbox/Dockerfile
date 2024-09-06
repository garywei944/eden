# Use Arch Linux base image
FROM archlinux:latest

# Update the system and install base-devel and git (required for AUR helpers)
RUN pacman -Syu --noconfirm && \
    pacman -S --needed --noconfirm base-devel git sudo
# pacman -S --needed --noconfirm base-devel git sudo openssl zlib xz libffi

# Create a new user (e.g., 'auruser') and add to sudoers
RUN useradd -m auruser && \
    echo "auruser ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Switch to the new user
USER auruser
WORKDIR /home/auruser

# Clone and build paru from AUR as non-root user
RUN git clone https://aur.archlinux.org/paru-bin.git /tmp/paru-bin && \
    cd /tmp/paru-bin && \
    makepkg -si --noconfirm && \
    rm -rf /tmp/paru-bin

RUN paru -S --noconfirm --needed micromamba-bin

# Set the default command
CMD ["/bin/bash"]
