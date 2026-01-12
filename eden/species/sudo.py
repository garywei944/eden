from eden.context import Context
from eden.eva import Eva
from eden.sh import esh as sh

ctx = Context.instance()
eva = Eva.instance()

requires_pkgmgr = False


def install():
    if ctx.is_root:
        if ctx.os_id == "arch":
            sh.pacman("-Syu", "--noconfirm", "sudo")
        elif eva.pkgmgr == "apt":
            sh.apt("install", "-y", "sudo")
