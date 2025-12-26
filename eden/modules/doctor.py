import logging

from eden.context import RuntimeContext

logger = logging.getLogger(__name__)


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def _section(title: str) -> None:
    print()
    print(f"[eden] {title}")


def _item(name: str, value: bool | str) -> None:
    if isinstance(value, bool):
        value = _yes_no(value)
    print(f"  {name:<16}: {value}")


def run(ctx: RuntimeContext) -> None:
    """
    Inspect the current machine and report Eden capabilities.

    This command is read-only and safe to run anywhere.
    """

    logger.info("running doctor")

    # ------------------------------------------------------------
    # Platform
    # ------------------------------------------------------------
    _section("Platform")

    _item("OS", ctx.os)

    if ctx.distro_info:
        distro = ctx.distro_info
        distro_str = f"{distro.get('name', '')} {distro.get('version', '')}".strip()
        _item("Distro", distro_str or ctx.distro_id or "unknown")
    else:
        _item("Distro", ctx.distro_id or "n/a")

    _item("WSL", ctx.is_wsl)
    _item("Headless", ctx.is_headless)

    # ------------------------------------------------------------
    # Privileges
    # ------------------------------------------------------------
    _section("Privileges")

    _item("sudo", ctx.has_sudo)
    _item("docker", ctx.has_docker)

    if not ctx.has_sudo:
        print("  note            : system package installs may be limited")

    # ------------------------------------------------------------
    # Package managers
    # ------------------------------------------------------------
    _section("Package managers")

    _item("apt", ctx.has_apt)
    _item("pacman", ctx.has_pacman)
    _item("yay", ctx.has_yay)
    _item("brew", ctx.has_brew)

    if not any((ctx.has_apt, ctx.has_pacman, ctx.has_yay, ctx.has_brew)):
        print("  warning         : no system package manager detected")

    # ------------------------------------------------------------
    # Language toolchains
    # ------------------------------------------------------------
    _section("Language toolchains")

    _item("cargo", ctx.has_cargo)
    _item("go", ctx.has_go)

    if not ctx.has_cargo and not ctx.has_go:
        print("  note            : will prefer binary or manual source builds")

    # ------------------------------------------------------------
    # Paths
    # ------------------------------------------------------------
    _section("Paths")

    _item("HOME", str(ctx.home))
    _item("Project root", str(ctx.project_root))
    _item("Eden home", str(ctx.eden_home))

    # ------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------
    _section("Summary")

    ready = True

    if not (ctx.has_apt or ctx.has_pacman or ctx.has_yay or ctx.has_brew):
        if not (ctx.has_cargo or ctx.has_go):
            ready = False

    _item("Ready for install", ready)

    if not ready:
        print("  reason          : no usable installer backend detected")

    print()
