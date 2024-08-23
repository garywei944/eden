# evaon

Unix initialization solution that supports multiple OS

## Why evaon?

The demand is straightforward:

- I have multiple instances of Unix-like OS: PC, macbook, AWS EC2, Computing cluster, WSL, etc.
- I want to have a consistent environment on all these machines, including:
  - package installation (fd, ripgrep, fzf, etc.)
  - dotfiles (zshrc, gitconfig, etc.)
  - private keys, etc.

A few bash scripts sounds like a good idea, but it's not enough:

- Different OS may have different package managers (apt, brew, etc.).
- I may or may not have root access (sudo) on these machines, which foundamentally changes the way to install packages.
- There might be built-in version of some packages (rsut, ruby, go, etc.), which I might not want to overwrite.
