import logging
import shutil
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

from eden.context import RuntimeContext

logger = logging.getLogger(__name__)


# ============================================================
# Utilities
# ============================================================


def has_binary(name: str) -> bool:
    return shutil.which(name) is not None


def run(cmd: list[str], *, env: dict[str, str] | None = None, cwd: str | None = None) -> None:
    logger.debug("running command: %s", " ".join(cmd))
    subprocess.run(cmd, check=True, env=env, cwd=cwd)


# ============================================================
# Installer base
# ============================================================


class Installer(ABC):
    """Abstract installer."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    def available(self) -> bool:
        """Whether this installer can be used in current RuntimeContext."""
        return True

    def supports_batch(self) -> bool:
        return False

    def install(self, package: str) -> None:
        raise NotImplementedError

    def install_batch(self, packages: list[str]) -> None:
        raise NotImplementedError


# ============================================================
# System package installer (batched)
# ============================================================


@dataclass(slots=True)
class SystemPackageInstaller(Installer):
    manager: str  # "pacman" | "yay" | "paru" | "apt" | "brew"

    @property
    def name(self) -> str:
        return f"system:{self.manager}"

    def available(self) -> bool:
        ctx = RuntimeContext.instance()
        return (
            (self.manager == "pacman" and ctx.has_pacman)
            or (self.manager == "yay" and ctx.has_yay)
            or (self.manager == "paru" and ctx.has_paru)
            or (self.manager == "apt" and ctx.has_apt and ctx.has_sudo)
            or (self.manager == "brew" and ctx.has_brew)
        )

    def supports_batch(self) -> bool:
        return True

    def install_batch(self, packages: list[str]) -> None:
        logger.info(
            "installing %d packages via %s: %s",
            len(packages),
            self.manager,
            ", ".join(packages),
        )

        if self.manager == "pacman":
            run(["sudo", "pacman", "-S", "--noconfirm", *packages])
        elif self.manager == "yay":
            run(["yay", "-S", "--noconfirm", *packages])
        elif self.manager == "paru":
            run(["paru", "-S", "--noconfirm", *packages])
        elif self.manager == "apt":
            run(["sudo", "apt-get", "install", "-y", *packages])
        elif self.manager == "brew":
            run(["brew", "install", *packages])
        else:
            raise RuntimeError(f"unsupported system package manager: {self.manager}")


# ============================================================
# Cargo installer
# ============================================================


@dataclass(slots=True)
class CargoInstaller(Installer):
    crate: str

    @property
    def name(self) -> str:
        return f"cargo:{self.crate}"

    def available(self) -> bool:
        return RuntimeContext.instance().has_cargo

    def install(self, package: str | None = None) -> None:
        logger.info("installing %s via cargo", self.crate)
        run(["cargo", "install", self.crate])


# ============================================================
# Go installer
# ============================================================


@dataclass(slots=True)
class GoInstaller(Installer):
    module: str

    @property
    def name(self) -> str:
        return f"go:{self.module}"

    def available(self) -> bool:
        return RuntimeContext.instance().has_go

    def install(self, package: str | None = None) -> None:
        logger.info("installing %s via go", self.module)
        run(["go", "install", self.module])


# ============================================================
# Source installer (last resort)
# ============================================================


@dataclass(slots=True)
class SourceInstaller(Installer):
    repo: str

    @property
    def name(self) -> str:
        return f"source:{self.repo}"

    def install(self, package: str | None = None) -> None:
        raise NotImplementedError("manual source builds not implemented yet")


# ============================================================
# Tool abstraction
# ============================================================


@dataclass(slots=True)
class Tool:
    """
    A Tool represents a usable binary and how to obtain it.
    """

    name: str
    binary: str
    installers: list[Installer]
    post_install: Callable[[], None] | None = None

    def is_installed(self) -> bool:
        return has_binary(self.binary)

    def _run_post_install(self) -> None:
        if self.post_install:
            logger.info("running post-install hook for %s", self.name)
            self.post_install()

    def plan_installer(self) -> Installer | None:
        if self.is_installed():
            return None

        for installer in self.installers:
            if installer.available():
                return installer

        return None


# ============================================================
# Planner & executor
# ============================================================


def install_tools(tools: list[Tool]) -> None:
    """
    Install multiple tools efficiently.

    - System packages are batched
    - Cargo / Go / source installs are per-tool
    - Post-install hooks run per-tool
    """

    # --------------------------------------------------------
    # Planning phase
    # --------------------------------------------------------
    system_batches: dict[str, list[str]] = {}
    deferred: list[tuple[Tool, Installer]] = []

    for tool in tools:
        if tool.is_installed():
            logger.info("%s already installed", tool.name)
            continue

        installer = tool.plan_installer()
        if installer is None:
            raise RuntimeError(f"no available installer for tool: {tool.name}")

        if isinstance(installer, SystemPackageInstaller):
            system_batches.setdefault(installer.manager, []).append(tool.name)
        else:
            deferred.append((tool, installer))

    # --------------------------------------------------------
    # Execute system batches
    # --------------------------------------------------------
    for manager, packages in system_batches.items():
        installer = SystemPackageInstaller(manager)
        installer.install_batch(packages)

    # --------------------------------------------------------
    # Execute deferred installers
    # --------------------------------------------------------
    # for tool, installer in deferred:
    #     installer.install("")

    # --------------------------------------------------------
    # Post-install hooks & verification
    # --------------------------------------------------------
    for tool in tools:
        if not tool.is_installed():
            tool._run_post_install()

        if not tool.is_installed():
            raise RuntimeError(f"tool {tool.name} installed but binary not found")

        logger.info("%s ready", tool.name)
