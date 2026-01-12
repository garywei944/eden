from eden.context import Context
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

if not eva.sudo or (eva.sudo and eva.pkgmgr == "apt"):
    depends = ["rust"]
    pkgmgr = "cargo"
