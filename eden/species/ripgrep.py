from eden.context import Context
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

if not eva.sudo:
    pkgmgr = "cargo"
    pkgname = "ripgrep"
