from eden.context import Context
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

if eva.sudo and eva.pkgmgr == "apt":
    pkgname = "netcat-openbsd"
