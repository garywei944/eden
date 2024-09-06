import os
import attrs
from enum import Enum
import distro
import platform
import shutil
import subprocess

from absl import flags, app


# Enum for OS types
class OSType(Enum):
    ARCH_LINUX = "Arch Linux"
    UBUNTU = "Ubuntu"
    MACOS = "macOS"
    OTHER = "Other"


# Enum for package managers
class PackageManager(Enum):
    APT = "apt"
    PACMAN = "pacman"
    HOMEBREW = "brew"
    YUM = "yum"
    DNF = "dnf"
    ZYPPER = "zypper"
    UNKNOWN = "unknown"


# Enum for device types
class DeviceType(Enum):
    WSL = "Windows Subsystem for Linux"
    DESKTOP = "Desktop"
    SERVER = "Server"


# Define system info class using attrs
@attrs.define
class SystemInfo:
    os_type: OSType
    package_manager: PackageManager
    device_type: DeviceType
    has_sudo: bool


# Function to detect OS type
def get_os_type():
    os_type = platform.system().lower()
    if os_type == "linux":
        distro_info = distro.id().lower()
        if "arch" in distro_info:
            return OSType.ARCH_LINUX
        elif "ubuntu" in distro_info:
            return OSType.UBUNTU
        else:
            return OSType.OTHER
    elif os_type == "darwin":
        return OSType.MACOS
    else:
        return OSType.OTHER


# Function to detect device type
def get_device_type():
    if check_if_wsl():
        return DeviceType.WSL
    elif platform.system().lower() == "linux":
        # Check if GUI is present by checking if DISPLAY or Wayland session exists
        if os.getenv("DISPLAY") or os.getenv("WAYLAND_DISPLAY"):
            return DeviceType.DESKTOP
        else:
            # Additionally, check if X server or any GUI is running
            try:
                result = subprocess.run(
                    ["xset", "q"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                if result.returncode == 0:
                    return DeviceType.DESKTOP
            except FileNotFoundError:
                pass
            return DeviceType.SERVER
    else:
        # For macOS or other OSes
        return DeviceType.DESKTOP


# Function to check if running in WSL
def check_if_wsl():
    try:
        with open("/proc/version", "r") as f:
            version_info = f.read().lower()
        if "microsoft" in version_info or "wsl" in version_info:
            return True
    except FileNotFoundError:
        return False
    return False


# Function to detect package manager
def get_package_manager():
    package_managers = {
        "apt": PackageManager.APT,
        "pacman": PackageManager.PACMAN,
        "brew": PackageManager.HOMEBREW,
        "yum": PackageManager.YUM,
        "dnf": PackageManager.DNF,
        "zypper": PackageManager.ZYPPER,
    }

    for manager in package_managers:
        if shutil.which(manager):
            return package_managers[manager]
    return PackageManager.UNKNOWN


# Function to check sudo privileges
def has_sudo_permission():
    try:
        result = subprocess.run(
            ["sudo", "-n", "true"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            return True
    except Exception:
        return False
    return False


# Dynamically setting default values for flags using function return values
flags.DEFINE_string("os_type", get_os_type().value, "Override the detected OS type.")
flags.DEFINE_bool("check_sudo", has_sudo_permission(), "Check for sudo permissions.")
flags.DEFINE_string(
    "pkg_manager", get_package_manager().value, "Override the detected package manager."
)
flags.DEFINE_string(
    "device_type", get_device_type().value, "Override the detected device type."
)

FLAGS = flags.FLAGS


# Function to collect system information and return an instance of SystemInfo
def collect_system_info():
    os_type = get_os_type()
    package_manager = get_package_manager()
    device_type = get_device_type()
    has_sudo = has_sudo_permission()
    return SystemInfo(
        os_type=os_type,
        package_manager=package_manager,
        device_type=device_type,
        has_sudo=has_sudo,
    )


def main(argv):
    info = collect_system_info()
    print(f"Operating System: {info.os_type.value}")
    print(f"Package Manager: {info.package_manager.value}")
    print(f"Device Type: {info.device_type.value}")
    print(f"Has Sudo Privileges: {info.has_sudo}")


if __name__ == "__main__":
    app.run(main)

# __all__ variable to define the public API of the module
__all__ = [
    "OSType",
    "PackageManager",
    "DeviceType",
    "SystemInfo",
    "get_os_type",
    "get_package_manager",
    "get_device_type",
    "has_sudo_permission",
    "collect_system_info",
]
