import sys
import sh
import questionary
from absl import logging, flags, app

from .context import Context, OSType
from .eden import Eden


def main(argv: list[str]):
    # logging.set_verbosity(logging.INFO)

    ctx = Context()

    if ctx.root_privileges:
        logging.error("Please run this script without sudo")
        sys.exit(1)

    Eden(ctx).run()


app.run(main)
