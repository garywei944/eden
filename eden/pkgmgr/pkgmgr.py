from abc import ABC, abstractmethod
from attrs import define

from ..context import Context

__all__ = ["PackageManager"]


@define
class PackageManager(ABC):
    ctx: Context

    def __attrs_post_init__(self): ...

    @abstractmethod
    def setup_pkgmgr(self): ...

    @abstractmethod
    def upgrade_system(self): ...

    def install_package(self, package: str | list[str]):
        if isinstance(package, str):
            package = [package]
        self._install_package(package)

    @abstractmethod
    def _install_package(self, package: list[str]): ...
