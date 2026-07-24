from eden.context import Context
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

is_meta_pkg = True
requires_pkgmgr = False

depends = []

if not eva.sudo:
    depends.append("rust")

if eva.sudo and ctx.is_arch:
    depends += ["yay", "paru"]
