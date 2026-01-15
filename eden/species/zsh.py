import getpass
import logging

from eden.context import Context
from eden.esh import esh as sh
from eden.eva import Eva
from eden.utils.misc import command_exists

logger = logging.getLogger(__name__)

ctx = Context.instance()
eva = Eva.instance()

if not eva.sudo:
    assert command_exists("zsh")
    pkgname = None


def post_install():

    if eva.sudo:
        # sudo usermod -s /bin/zsh "$USER"
        sh.sudo.usermod("-s", "/bin/zsh", getpass.getuser())
    else:
        # This command seems requires typing the password
        if ctx.stdin_isatty:
            sh.chsh("-s", "/bin/zsh")
        else:
            logger.warning("Skipping chsh because stdin is not a TTY")
