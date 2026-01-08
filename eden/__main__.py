from eden.utils.logging_utils import setup_root_logger

setup_root_logger()

import logging

from eden.context import Context

logger = logging.getLogger(__name__)


def main():
    setup_logging()

    logger.info("Eden main module executed")

    ctx = Context()
    logger.info("context: %s", ctx)


def setup_logging():
    logging.getLogger("sh").setLevel(logging.INFO)


main()
