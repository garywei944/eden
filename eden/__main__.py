import sys
import sh
import questionary
from absl import logging

from .context import Context, OSType

# from .distros import Distro
# from .utils import restart_with_sudo

logging.set_verbosity(logging.INFO)


ctx = Context()

if ctx.root_privileges:
    logging.error("Please run this script without sudo")
    sys.exit(1)
