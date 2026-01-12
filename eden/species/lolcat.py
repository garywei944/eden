from eden.context import Context
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

if eva.pkgmgr == "apt":
    depends = ["rust"]
    pkgmgr = "cargo"
