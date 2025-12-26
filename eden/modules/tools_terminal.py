import shutil
from pathlib import Path

from eden.context import RuntimeContext
from eden.modules.packages import (
    CargoInstaller,
    SystemPackageInstaller,
    Tool,
)

# ------------------------------------------------------------
# Post-install hooks
# ------------------------------------------------------------


def _ensure_local_bin() -> Path:
    ctx = RuntimeContext.instance()
    path = ctx.home / ".local" / "bin"
    path.mkdir(parents=True, exist_ok=True)
    return path


def fix_fd_on_debian() -> None:
    """
    Debian/Ubuntu install fd as `fdfind`.
    Create ~/.local/bin/fd if needed.
    """
    if shutil.which("fd"):
        return

    fdfind = shutil.which("fdfind")
    if not fdfind:
        return

    target = _ensure_local_bin() / "fd"
    if not target.exists():
        target.symlink_to(fdfind)


def fix_bat_on_debian() -> None:
    """
    Debian/Ubuntu install bat as `batcat`.
    Create ~/.local/bin/bat if needed.
    """
    if shutil.which("bat"):
        return

    batcat = shutil.which("batcat")
    if not batcat:
        return

    target = _ensure_local_bin() / "bat"
    if not target.exists():
        target.symlink_to(batcat)


# ------------------------------------------------------------
# Tools
# ------------------------------------------------------------

RG = Tool(
    name="ripgrep",
    binary="rg",
    installers=[
        SystemPackageInstaller("paru"),
        SystemPackageInstaller("yay"),
        SystemPackageInstaller("pacman"),
        SystemPackageInstaller("apt"),
        CargoInstaller("ripgrep"),
    ],
)

FD = Tool(
    name="fd",
    binary="fd",
    installers=[
        SystemPackageInstaller("paru"),
        SystemPackageInstaller("yay"),
        SystemPackageInstaller("pacman"),
        SystemPackageInstaller("apt"),  # fd-find
        CargoInstaller("fd-find"),
    ],
    post_install=fix_fd_on_debian,
)

FZF = Tool(
    name="fzf",
    binary="fzf",
    installers=[
        SystemPackageInstaller("paru"),
        SystemPackageInstaller("yay"),
        SystemPackageInstaller("pacman"),
        SystemPackageInstaller("apt"),
    ],
)

BAT = Tool(
    name="bat",
    binary="bat",
    installers=[
        SystemPackageInstaller("paru"),
        SystemPackageInstaller("yay"),
        SystemPackageInstaller("pacman"),
        SystemPackageInstaller("apt"),
        CargoInstaller("bat"),
    ],
    post_install=fix_bat_on_debian,
)


TERMINAL_TOOLS: list[Tool] = [
    RG,
    FD,
    FZF,
    BAT,
]
