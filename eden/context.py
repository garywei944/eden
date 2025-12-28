import logging
from pathlib import Path

from attrs import define, field

from eden.utils.singleton import Singleton

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.resolve()


@define(frozen=True)
class Context(Singleton):
    project_root: Path = field(default=PROJECT_ROOT)
