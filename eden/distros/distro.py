from abc import ABC, abstractmethod
from enum import Enum

from absl import logging

from ..context import Context


class PackageManager(ABC):
    pkg_map: dict[str, str]

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def upgrade_system(self):
        pass

    @abstractmethod
    def install_package(self, package: str | list[str]):
        pass


class Distro:
    package_manager: PackageManager

    def __init__(self, ctx: Context):
        self.ctx = ctx

        # TODO: set up the package manager

    def setup(self):
        logging.info("Setting up the System")

        # set up sudo

        # convert the following in python
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
        self.package_manager.upgrade_system()

    def evangelion_command_collection(self):
        raise NotImplementedError

    def config_keys(self):
        raise NotImplementedError

    def config_dotfiles(self):
        raise NotImplementedError

    def config_terminal(self):
        raise NotImplementedError
