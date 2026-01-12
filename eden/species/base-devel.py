from eden.context import Context
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

requires_pkgmgr = False

if eva.sudo:
    depends = ["sudo"]

if eva.sudo and ctx.os_id == "arch":
    pkgmgr = "pacman"
elif eva.sudo and eva.pkgmgr == "apt":
    pkgmgr = "apt"
    pkgname = "build-essential"
