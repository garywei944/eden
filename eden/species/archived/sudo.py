import getpass
import logging

from eden.context import Context
from eden.esh import esh as sh
from eden.eva import Eva

logger = logging.getLogger(__name__)

ctx = Context.instance()
eva = Eva.instance()

requires_pkgmgr = False


def install():
    if ctx.is_root:
        if ctx.os_id == "arch":
            sh.pacman("-Syu", "--noconfirm", "sudo")
        elif eva.pkgmgr == "apt":
            sh.apt_get.install("-y", "sudo")


def post_install():
    """Set up NOPASSWD for the current user."""
    if ctx.is_root or not eva.sudo:
        return

    username = getpass.getuser()
    sh.sudo(
        "-n", "tee", f"/etc/sudoers.d/90_{username}", _in=f"{username} ALL=(ALL) NOPASSWD: ALL\n"
    )
    logger.info("Configured NOPASSWD sudo for user '%s'.", username)
