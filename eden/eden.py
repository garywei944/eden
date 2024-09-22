import os
import sh
import shutil
import requests
import getpass

import questionary
from enum import Enum, auto
from absl import logging, flags
from attrs import define, field
from overrides import overrides
from morecontext import dirchanged
from pathlib import Path

from .context import Context, OSType
from .pkgmgr import PackageManager
from .utils import sh_, sh_contrib_

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
        sh.sudo.tee(
            "-a",
            "/etc/sudoers",
            _in=f"Defaults\teditor=/usr/bin/vim\n{getpass.getuser()}\tALL=(ALL)\tNOPASSWD: ALL\n",
        )

    def config_keys(self):
        logging.info("Configuring keys")
        logging.warning("This will overwrite existing ~/.ssh/id_rsa key")

        with dirchanged("keys"):
            try:
                sh_("bash", "init_keys.sh")
            except sh.ErrorReturnCode as e:
                logging.error("Failed to configure keys")
                logging.error(e)
                return

        # Create .ssh directory if not exists
        ssh_path = Path.home() / ".ssh"
        ssh_path.mkdir(exist_ok=True)
        os.chmod(ssh_path, 0o700)

        # config git ssh
        with open(ssh_path / "known_hosts", "a") as f:
            sh.ssh_keyscan("-H", "github.com", _out=f)
        os.chmod(ssh_path / "known_hosts", 0o644)

    def install_ecc(self): ...

    def config_dotfiles(self):
        logging.info("Configuring dotfiles")

        with dirchanged(Path.home()):
            shutil.rmtree(".git", ignore_errors=True)
            sh_contrib_("git", "init")
            sh_contrib_("git", "remote", "add", "origin", DOTFILES_REPO)
            sh_contrib_("git", "config", "core.excludesFile", ".eva.gitignore")
            sh_contrib_("git", "fetch", "--depth=1")
            sh_contrib_("git", "reset", "--hard", "origin/main")
            sh_contrib_("git", "branch", "-m", "master", "main", _ok_code=[0, 128])
            sh_contrib_("git", "branch", "--set-upstream-to=origin/main", "main")

    def config_shell(self):
        logging.info("Configuring shell")

        if os.environ.get("SHELL") != "/usr/bin/zsh":
            sh_("chsh", "-s", "/usr/bin/zsh")

        # TODO: shell configuration
        raise NotImplementedError("Shell configuration is not implemented yet")
