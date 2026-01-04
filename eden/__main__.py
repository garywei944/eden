from eden.utils.logging_utils import setup_root_logger

setup_root_logger()

import logging

# from pathlib import Path


logger = logging.getLogger(__name__)


def main():
    logger.info("Eden main module executed")

    # project_root = Path(__file__).parent.parent.resolve()


main()
