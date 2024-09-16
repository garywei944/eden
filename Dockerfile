FROM archlinux:latest

RUN useradd -m eva && \
    echo "eva ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    echo 'MAKEFLAGS="-j$(nproc)"' >> /etc/makepkg.conf

RUN pacman -Syu --noconfirm && \
    pacman -S --needed --noconfirm base-devel sudo vim git

# Switch to the new user
USER eva
WORKDIR /home/eva

ENV EDITOR=vim

# Clone and build paru from AUR as non-root user
RUN git clone https://aur.archlinux.org/paru-bin.git /tmp/paru-bin && \
    cd /tmp/paru-bin && \
    makepkg -si --noconfirm && \
    rm -rf /tmp/paru-bin
# build yay
RUN git clone https://aur.archlinux.org/yay.git /tmp/yay && \
    cd /tmp/yay && \
    makepkg -si --noconfirm && \
    rm -rf /tmp/yay

RUN yay -S --noconfirm --needed micromamba-bin

# Set up the environment
ENV MAMBA_ROOT_PREFIX="/home/eva/micromamba"
COPY ./environment.yml /home/eva
RUN micromamba -y create -f environment.yml

RUN echo "export MAMBA_ROOT_PREFIX=\"$HOME/micromamba\"" >> ~/.bashrc && \
    echo "eval \"\$(micromamba shell hook --shell bash)\"" >> ~/.bashrc && \
    echo "micromamba activate eden" >> ~/.bashrc

# Set the default command
CMD ["/bin/bash"]


# Copy all files from the parent directory into $HOME
COPY ./eden /home/eva/eden
