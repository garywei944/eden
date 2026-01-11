from eden.context import Context
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

is_meta_pkg = True

depends = []
if eva.sudo and ctx.os_id == "arch":
    depends = ["yay", "paru"]

depends += ["rust", "go"]
