import os
import sh
import shutil
import requests

from absl import logging, flags
from attrs import define, field
from overrides import overrides
from morecontext import dirchanged

from .context import Context, OSType
from .pkgmgr import PackageManager

__all__ = ["Eden"]


FLAGS = flags.FLAGS


@define
class Eden:
    ctx: Context
    pkgmgr: PackageManager = field(init=False)

    def __attrs_post_init__(self):
        logging.info("Setting up Eden")

        # Set up according package manager
        match self.ctx.os_type:
            case OSType.ARCH_LINUX:
                from .pkgmgr import Yay

                self.pkgmgr = Yay(self.ctx)
            case OSType.UBUNTU:
                ...
            case OSType.DEBIAN:
                ...
            case OSType.MACOS:
                ...
            case OSType.OTHER:
                ...

    def run(self):
        self.pkgmgr.setup_pkgmgr()
        self.config_keys()
        self.pkgmgr.upgrade_system()
        self.install_ecc()
        self.config_dotfiles()

    def config_keys(self): ...

    def config_dotfiles(self): ...

    def install_ecc(self): ...
