import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Literal

import distro

# ============================================================
# Generic helpers
# ============================================================


def has_command(cmd: str) -> bool:
    """Return True if command is found in PATH at process start."""
    return shutil.which(cmd) is not None


# ============================================================
# OS / platform
# ============================================================


def detect_os() -> Literal["linux", "darwin"]:
    system = platform.system().lower()
    if system == "linux":
        return "linux"
    if system == "darwin":
        return "darwin"
    raise RuntimeError(f"unsupported OS: {system}")


def detect_distro_id() -> str | None:
    """Return Linux distro ID (e.g. 'debian', 'ubuntu', 'arch'), or None."""
    if detect_os() != "linux":
        return None
    try:
        return distro.id() or None
    except Exception:
        return None


def detect_distro_info() -> dict[str, str] | None:
    """Return detailed distro info for reporting only."""
    if detect_os() != "linux":
        return None
    try:
        return {
            "id": distro.id(),
            "name": distro.name(pretty=True),
            "version": distro.version(),
            "like": distro.like(),
        }
    except Exception:
        return None


def detect_wsl() -> bool:
    """Detect Windows Subsystem for Linux."""
    if detect_os() != "linux":
        return False
    if "WSL_DISTRO_NAME" in os.environ:
        return True
    try:
        return "microsoft" in Path("/proc/version").read_text(encoding="utf-8").lower()
    except OSError:
        return False


def detect_headless() -> bool:
    """Return True if no graphical session is available."""
    return not any(os.environ.get(var) for var in ("DISPLAY", "WAYLAND_DISPLAY", "MIR_SOCKET"))


# ============================================================
# Privileges / execution capabilities
# ============================================================


def detect_sudo() -> bool:
    """Return True if sudo exists and can run non-interactively."""
    if not has_command("sudo"):
        return False
    try:
        subprocess.run(
            ["sudo", "-n", "true"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def detect_docker() -> bool:
    return has_command("docker")


# ============================================================
# Package managers
# ============================================================


def detect_apt() -> bool:
    return has_command("apt") or has_command("apt-get")


def detect_pacman() -> bool:
    return has_command("pacman")


def detect_yay() -> bool:
    return has_command("yay")


def detect_paru() -> bool:
    return has_command("paru")


def detect_brew() -> bool:
    return has_command("brew")


# ============================================================
# Language toolchains
# ============================================================


def detect_cargo() -> bool:
    return has_command("cargo")


def detect_go() -> bool:
    return has_command("go")


# ============================================================
# Paths
# ============================================================


def detect_home() -> Path:
    return Path.home()


def detect_eden_home(project_root: Path) -> Path:
    return project_root / ".eden"
