#!/usr/bin/env python3

import os
import sys
import platform
import distro

from enum import Enum


class OSType(Enum):
    ARCH_LINUX = "Arch Linux"
    UBUNTU = "Ubuntu"
    DEBIAN = "Debian"
    MACOS = "macOS"
    WINDOWS = "Windows"
    OTHER = "Other"


# Check the OS
system = platform.system().lower()

if system != "windows":
    import sh

if system == "linux":
    dist_name = distro.id().lower()
    if dist_name == "ubuntu":
        os_type = OSType.UBUNTU
    elif dist_name == "arch":
        os_type = OSType.ARCH_LINUX
    elif dist_name == "debian":
        os_type = OSType.DEBIAN
    else:
        os_type = OSType.OTHER
elif system == "darwin":
    os_type = OSType.MACOS
elif system == "windows":
    # if sys.getwindowsversion().build >= 22000:
    #     os_type = OSType.WINDOWS11
    # elif platform.release() == "10":
    #     os_type = OSType.WINDOWS10
    # else:
    #     raise Exception("Unsupported Windows version")
    os_type = OSType.WINDOWS
else:
    raise Exception("Unsupported OS")

if system != "windows":
    # check if we have sudo permissions
    try:
        sh.sudo.true()
        sudo = True
    except sh.ErrorReturnCode:
        sudo = False

# Check architecture
arch = platform.architecture()
print(arch)

# for each OS, set the package manager
match os_type:
    case OSType.ARCH_LINUX:
        package_manager = "paru"
    case OSType.UBUNTU | OSType.DEBIAN:
        package_manager = "apt"
    case OSType.MACOS:
        package_manager = "brew"
    case OSType.WINDOWS10 | OSType.WINDOWS11:
        package_manager = "choco"
    case OSType.OTHER:
        package_manager = None


print(platform.release())
