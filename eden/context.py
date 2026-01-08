import logging
import os
from pathlib import Path

import attrs
import sh

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


@attrs.define(frozen=True)
class Context(Singleton):
    project_root: Path = attrs.field(default=PROJECT_ROOT)
    has_sudo: bool = attrs.field(factory=has_sudo)

    # check if it's a byted devbox
    byted: bool = False
