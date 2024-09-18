import os
import sh
import shutil
import requests

import questionary
from enum import Enum, auto
from absl import logging, flags
from attrs import define, field
from overrides import overrides
from morecontext import dirchanged

from .context import Context, OSType
from .pkgmgr import PackageManager

__all__ = ["Eden"]

DOTFILES_REPO = "git@github.com:garywei944/eva_arch.git"


class PMEnum(Enum):
    AUTO = auto()
    YAY = auto()
    PARU = auto()
    PACMAN = auto()
    APT = auto()
    BREW = auto()
    NATIVE = auto()


FLAGS = flags.FLAGS
flags.DEFINE_enum_class(
    "pkgmgr",
    PMEnum.AUTO,
    PMEnum,
    "Package manager to use for package installation. Default is auto",
)
flags.DEFINE_alias("pm", "pkgmgr")


@define
class Eden:
    ctx: Context

    pkgmgr: PackageManager = field(init=False)

    def __attrs_post_init__(self):
        logging.info("Setting up Eden")

        # Set up according package manager
        if FLAGS.pkgmgr == PMEnum.AUTO:
            match self.ctx.os_type:
                case OSType.ARCH_LINUX:
                    FLAGS.pkgmgr = PMEnum.YAY
                case OSType.UBUNTU:
                    FLAGS.pkgmgr = PMEnum.APT
                case OSType.MACOS:
                    FLAGS.pkgmgr = PMEnum.BREW
                case _:
                    logging.warning("Unsupported OS, using native package manager")
                    FLAGS.pkgmgr = PMEnum.NATIVE

        match FLAGS.pkgmgr:
            case PMEnum.YAY:
                from .pkgmgr import Yay as PM
            case PMEnum.PARU:
                from .pkgmgr import Paru as PM
            case PMEnum.PACMAN:
                from .pkgmgr import Pacman as PM
            case PMEnum.APT:
                raise NotImplementedError("APT is not implemented yet")
            case PMEnum.BREW:
                raise NotImplementedError("Brew is not implemented yet")
            case PMEnum.NATIVE:
                from .pkgmgr import NativePM as PM
            case _:
                raise RuntimeError("Invalid package manager")

        self.pkgmgr = PM(self.ctx)

    def config_sudo(self):
        logging.info("Configuring sudo")

        #       echo "Defaults	editor=/usr/bin/vim
        # $USER	ALL=(ALL)	NOPASSWD: ALL" | sudo tee -a /etc/sudoers
        sh.sudo(
            "tee",
            "-a",
            "/etc/sudoers",
            _in=sh.echo(
                "Defaults\teditor=/usr/bin/vim\n$USER\tALL=(ALL)\tNOPASSWD: ALL"
            ),
        )

    def config_keys(self):
        logging.info("Configuring keys")
        logging.warning("This will overwrite existing ~/.ssh/id_rsa key")

        sh.bash("keys/init_keys.sh", _fg=True)

    def install_ecc(self): ...

    def config_dotfiles(self):
        logging.info("Configuring dotfiles")
        # cd ~ || exit
        # rm -fr .git
        # git init
        # git remote add origin git@github.com:garywei944/eva_arch.git
        # git config core.excludesFile .eva.gitignore
        # git fetch --depth=1
        # git reset --hard origin/main
        # git branch -m master main
        # git branch --set-upstream-to=origin/main main
        with dirchanged("~"):
            sh.rm("-fr", ".git")
            sh.git("init")
            sh.git("remote", "add", "origin", DOTFILES_REPO)
            sh.git("config", "core.excludesFile", ".eva.gitignore")
            sh.git("fetch", "--depth=1")
            sh.git("reset", "--hard", "origin/main")
            sh.git("branch", "-m", "master", "main")
            sh.git("branch", "--set-upstream-to=origin/main", "main")

    def config_shell(self):
        logging.info("Configuring shell")

        sh.chsh("-s", "/usr/bin/zsh")

        # TODO: shell configuration
        raise NotImplementedError("Shell configuration is not implemented yet")
