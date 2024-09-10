import os
from abc import ABC, abstractmethod
from enum import Enum
from typing import Self

from absl import logging

from ..context import Context, OSType


__all__ = ["PackageManager", "Distro"]


class PackageManager(ABC):
    pkg_map: dict[str, str]

    def __init__(self, ctx: Context):
        self.ctx = ctx

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def upgrade_system(self):
        pass

    def install_package(self, package: str | list[str]):
        if isinstance(package, str):
            package = [package]
        self._install_package(package)

    @abstractmethod
    def _install_package(self, package: str):
        pass


class Distro(ABC):
    package_manager: PackageManager

    def __new__(cls, ctx: Context) -> Self:
        if cls is Distro:
            match ctx.os_type:
                case OSType.ARCH_LINUX:
                    from .arch import ArchLinux

                    return ArchLinux(ctx)
                case _:
                    raise NotImplementedError
        return super().__new__(cls)

    def __init__(self, ctx: Context):
        self.ctx = ctx

    def setup(self):
        logging.info("Setting up the System")

        # set up sudo
        # echo "Defaults	editor=/usr/bin/vim
        # $USER	ALL=(ALL)	NOPASSWD: ALL" | sudo tee -a /etc/sudoers
        try:
            with open("/etc/sudoers", "a") as f:
                f.write("Defaults\teditor=/usr/bin/vim\n")
                f.write(f"{os.getenv('USER')}\tALL=(ALL)\tNOPASSWD: ALL\n")
        except Exception as e:
            logging.error(f"Failed to set up sudo: {e}")

        self.package_manager.setup()

    def upgrade_system(self):
        logging.info("Upgrading the System")
        self.package_manager.upgrade_system()

    def evangelion_command_collection(self):
        raise NotImplementedError

    def config_keys(self):
        raise NotImplementedError

    def config_dotfiles(self):
        raise NotImplementedError

    def config_terminal(self):
        raise NotImplementedError
