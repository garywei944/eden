import sys
from absl import logging
import questionary

from .context import Context, OSType
from .distros import Distro
from .utils import restart_with_sudo

logging.set_verbosity(logging.INFO)


ctx = Context()

if ctx.os_type != OSType.WINDOWS:
    import sh

# # if we don't have sudo permission, ask for it
# if ctx.sudo and not ctx.root_privileges:

#     if not questionary.confirm(
#         "Sudo privileges are available, but you are not using sudo. \
# Packages will be installed without sudo or the package manager. \
# Do you want to proceed?",
#         False,
#     ).ask():
#         if questionary.confirm("Do you want to restart with sudo?", False).ask():
#             restart_with_sudo()
#         else:
#             logging.error("Exiting...")
#             sys.exit(1)

if ctx.root_privileges:
    logging.error("Please run this script without sudo")
    sys.exit(1)


distro = Distro(ctx)

# Setup the system
distro.setup()
distro.config_keys()
distro.upgrade_system()
distro.evangelion_command_collection()
distro.config_dotfiles()
distro.config_terminal()
