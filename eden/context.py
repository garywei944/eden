import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Self

from eden.utils import detect
from eden.utils.singleton import Singleton

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RuntimeContext(Singleton):
    # ------------------------------------------------------------
    # Platform
    # ------------------------------------------------------------
    os: Literal["linux", "darwin"]
    distro_id: str | None
    distro_info: dict[str, str] | None

    is_wsl: bool
    is_headless: bool

    # ------------------------------------------------------------
    # Privileges / execution
    # ------------------------------------------------------------
    has_sudo: bool
    has_docker: bool

    # ------------------------------------------------------------
    # Package managers
    # ------------------------------------------------------------
    has_apt: bool
    has_pacman: bool
    has_yay: bool
    has_paru: bool
    has_brew: bool

    # ------------------------------------------------------------
    # Language toolchains
    # ------------------------------------------------------------
    has_cargo: bool
    has_go: bool

    # ------------------------------------------------------------
    # Paths
    # ------------------------------------------------------------
    home: Path
    project_root: Path
    eden_home: Path

    # ------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------
    @classmethod
    def build(cls, *, project_root: Path) -> Self:
        """
        Build the RuntimeContext snapshot.

        This MUST be called exactly once at program start.
        """
        logger.debug("building RuntimeContext snapshot")

        os_name = detect.detect_os()

        ctx = cls(
            # platform
            os=os_name,
            distro_id=detect.detect_distro_id(),
            distro_info=detect.detect_distro_info(),
            is_wsl=detect.detect_wsl(),
            is_headless=detect.detect_headless(),
            # privileges
            has_sudo=detect.detect_sudo(),
            has_docker=detect.detect_docker(),
            # package managers
            has_apt=detect.detect_apt(),
            has_pacman=detect.detect_pacman(),
            has_yay=detect.detect_yay(),
            has_paru=detect.detect_paru(),
            has_brew=detect.detect_brew(),
            # toolchains
            has_cargo=detect.detect_cargo(),
            has_go=detect.detect_go(),
            # paths
            home=detect.detect_home(),
            project_root=project_root,
            eden_home=detect.detect_eden_home(project_root),
        )

        logger.debug("RuntimeContext built: %s", ctx)
        return ctx
