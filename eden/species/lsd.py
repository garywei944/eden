from eden.context import Context
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

if not eva.sudo or (eva.sudo and ctx.os_id == "ubuntu" and ctx.os_version.major < 23):
    depends = ["rust"]
    pkgmgr = "cargo"
    pkgname = "lsd"
