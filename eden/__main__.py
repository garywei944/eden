from eden.utils.logging_utils import setup_root_logger

setup_root_logger()

import logging
from pathlib import Path

from eden.args import Args
from eden.context import Context

logger = logging.getLogger(__name__)


def main():
    setup_logging()

    logger.info("Eden main module executed")

    args = Args()
    logger.info("args: %s", args)

    ctx = Context(byted=args.byted)  # type: ignore[call-arg]
    logger.info("context: %s", ctx)

    # 1. create projects, sandbox, and byted folders
    (Path.home() / "projects").mkdir(exist_ok=True, parents=True)
    (Path.home() / "sandbox").mkdir(exist_ok=True, parents=True)
    if ctx.byted:
        (Path.home() / "byted").mkdir(exist_ok=True, parents=True)


def setup_logging():
    logging.getLogger("sh").setLevel(logging.INFO)


main()
