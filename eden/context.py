import logging
import os
from pathlib import Path

import sh
from attrs import define, field

from eden.utils.singleton import Singleton

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


@define(frozen=True)
class Context(Singleton):
    project_root: Path = field(default=PROJECT_ROOT)
    has_sudo: bool = field(factory=has_sudo)
