import os
import sys
from absl import logging

from .context import system

if system != "windows":
    import sh

__all__ = ["restart_with_sudo"]


def restart_with_sudo():
    logging.warning("Script requires root privileges. Restarting with sudo...")
    print("=" * 80, file=sys.stderr)
    # Detect if the script was run as a module with `python -m module`
    if sys.argv[0].endswith("__main__.py"):
        module_name = sys.modules["__main__"].__package__
        if module_name:
            command = [sys.executable, "-m", module_name] + sys.argv[1:]
        else:
            raise Exception("Idk what happend here")
    else:
        command = [sys.executable] + sys.argv

    # Relaunch the script with sudo using os.execvp
    try:
        os.execvp("sudo", ["sudo"] + command)
    except OSError as e:
        logging.error(f"Failed to restart script with sudo: {e}")
        sys.exit(1)
