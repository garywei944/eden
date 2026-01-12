from eden.context import Context
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

requires_pkgmgr = False

if eva.sudo:
    depends = ["sudo"]

if ctx.os_id == "arch":
    if eva.sudo:
        pkgmgr = "pacman"
    else:
        pkgname = None
