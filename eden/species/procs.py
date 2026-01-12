from eden.context import Context
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

if eva.sudo and ctx.os_id == "arch":
    pass
else:
    depends = ["rust"]
    pkgmgr = "cargo"
