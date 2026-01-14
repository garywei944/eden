import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

import distro
from packaging import version as pv

from eden.args import Args
from eden.sh import esh as sh
from eden.utils.singleton import Singleton

__all__ = ["Context", "has_sudo"]

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.resolve()


def has_sudo() -> bool:
    """Check if the current user has sudo privileges."""
    if os.geteuid() == 0:
        return True

    try:
        sh.sudo(["-n", "true"])
        return True
    except (sh.ErrorReturnCode, sh.CommandNotFound):
        return False


def parse_os_version() -> pv.Version:
    version = distro.version(best=True)
    try:
        return pv.parse(version)
    except pv.InvalidVersion:
        return pv.Version("1!0.0")


@dataclass(frozen=True)
class Context(Singleton):
    args: Args

    os_id: str = distro.id()
    os_version: pv.Version = parse_os_version()

    project_root: Path = PROJECT_ROOT
    is_root: bool = os.geteuid() == 0
    has_sudo: bool = has_sudo()
    stdin_isatty: bool = sys.stdin.isatty()

    # check if it's a byted devbox
    byted: bool = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "byted", self.args.byted)
