import os
import sys
import platform
import distro

from enum import Enum
from attrs import define
from absl import logging


# only import sh if we are not on Windows
system = platform.system().lower()
if system != "windows":
    import sh


__all__ = ["OSType", "Context", "system"]


class OSType(Enum):
    ARCH_LINUX = "Arch Linux"
    UBUNTU = "Ubuntu"
    DEBIAN = "Debian"
    MACOS = "macOS"
    WINDOWS = "Windows"
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
        return OSType.WINDOWS
    else:
        raise Exception("Unsupported OS")


def check_sudo() -> bool:
    if system == "windows":
        # TODO: check if we have admin permissions
        logging.warning("Windows doesn't check admin permissions for now")
        return False
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
        # on windows, update if we are running Windows 11
        if system == "windows" and platform.release() == "10":
            if sys.getwindowsversion().build >= 22000:
                self.os_version = "11"
                logging.info("Windows 11 detected")
            else:
                self.os_version = "10"
                logging.info("Windows 10 detected")

        # TODO: check how to distinguish mac intel from mac arm

        logging.info(f"OS Type: {self.os_type}")
        logging.info(f"OS Version: {self.os_version}")
        logging.info(f"Sudo: {self.sudo}")
        logging.info(f"Root privileges: {self.root_privileges}")
        logging.info(f"Architecture: {self.arch}")
        logging.info(f"System: {system}")
