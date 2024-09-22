import os
import sys
import platform
import distro
import sh
from tabulate import tabulate

from enum import Enum
from attrs import define
from absl import logging

__all__ = ["OSType", "Context"]

system = platform.system().lower()


class OSType(Enum):
    ARCH_LINUX = "Arch Linux"
    UBUNTU = "Ubuntu"
    DEBIAN = "Debian"
    MACOS = "macOS"
    # WINDOWS = "Windows"
    OTHER = "Other"


def get_os_type() -> OSType:
    if system == "linux":
        dist_name = distro.id().lower()
        if dist_name == "ubuntu":
            return OSType.UBUNTU
        elif dist_name == "arch":
            return OSType.ARCH_LINUX
        elif dist_name == "debian":
            return OSType.DEBIAN
        else:
            return OSType.OTHER
    elif system == "darwin":
        return OSType.MACOS
    elif system == "windows":
        # return OSType.WINDOWS
        raise Exception("Windows is not supported")
    else:
        raise Exception("Unsupported OS")


def check_sudo() -> bool:
    try:
        sh.sudo.true()
        return True
    except sh.ErrorReturnCode:
        return False


@define
class Context:
    os_type: OSType = get_os_type()
    os_version: str = platform.version()
    sudo: bool = check_sudo()
    root_privileges: bool = os.geteuid() == 0
    arch: str = platform.architecture()[0]

    def __attrs_post_init__(self):
        logging.info(
            "\n"
            + tabulate(
                [
                    ["OS Type", self.os_type],
                    ["OS Version", self.os_version],
                    ["Sudo", self.sudo],
                    ["Root privileges", self.root_privileges],
                    ["Architecture", self.arch],
                    ["System", system],
                ],
                headers=["Key", "Value"],
            )
        )
        print("-" * 80, file=sys.stderr)
