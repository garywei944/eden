import os
import sys
from absl import logging

from .context import Context, OSType
from .distros import Distro

logging.set_verbosity(logging.INFO)


ctx = Context()

if ctx.os_type != OSType.WINDOWS:
    import sh

# if we don't have sudo permission, ask for it
if ctx.sudo:
    if os.geteuid() != 0:
        logging.warning("Script requires root privileges. Restarting with sudo...")
        # Detect if the script was run as a module with `python -m module`
        if sys.argv[0].endswith("__main__.py"):
            module_name = sys.modules["__main__"].__package__
            if module_name:
                command = [sys.executable, "-m", module_name] + sys.argv[1:]
            else:
                raise Exception("Idk what happend here")
        else:
            command = [sys.executable] + sys.argv

        # Relaunch the script with sudo
        try:
            sh.sudo(command, _fg=True)
        except sh.ErrorReturnCode as e:
            logging.error(f"Failed to restart script with sudo: {e}")
        finally:
            sys.exit(1)

assert (
    not ctx.sudo or os.geteuid() == 0
), "User has sudo permissions but is not running with sudo"

distro = Distro(ctx)

# Setup the system
distro.setup()
distro.upgrade_system()
distro.evangelion_command_collection()
