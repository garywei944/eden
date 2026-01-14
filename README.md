# Eden: Evangelion Development Environment Nexus

Unix initialization solution that supports multiple OS

## Why Eden?

The requirements are straightforward:

- I have multiple instances of Unix-like OS: PC, macbook, AWS EC2, Computing cluster, WSL, etc.
- I want to have a consistent environment across all these machines, including:
  - package installation (fd, ripgrep, fzf, etc.)
  - dotfiles (zshrc, gitconfig, etc.)
  - private keys, etc.

A few bash scripts sounds like a good idea, but it's not enough:

- Different OS may have different package managers (apt, brew, etc.).
- I may or may not have root access (sudo) on these machines, which fundamentally changes the way to install packages.
- They may or may not have desktop GUI (X11, Wayland, etc.).
- There might be built-in version of some packages (rsut, ruby, go, etc.), which I don't want to overwrite.

W.I.P.

## Design Choice

I choose to use Python over bash for the following reasons:

- More advanced logic can be implemented easily in Python.
- It's easy to develop and test Python codes.
- Easy to maintain and extend.

## Predecessor

[eva_init](https://github.com/garywei944/eva_init) is the predecessor of Eden.
It's a bash-based project that performs the same work, but it gets really messy and is hard
to maintain after a while.
