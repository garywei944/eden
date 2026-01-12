from eden.context import Context
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

is_meta_pkg = True
requires_pkgmgr = False

depends = []

if eva.sudo:
    depends.append("sudo")
else:
    depends.append("rust")

if eva.sudo and ctx.os_id == "arch":
    depends += ["yay", "paru"]
