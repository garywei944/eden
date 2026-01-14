from pathlib import Path

from eden.context import Context
from eden.esh import esh as sh
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

if (
    not eva.sudo
    or (eva.sudo and ctx.os_id == "ubuntu")
    or (eva.sudo and ctx.os_id == "debian" and ctx.os_version.major < 12)
):
    depends = ["rust"]
    pkgmgr = "cargo"
    pkgname = "sd"

if ctx.byted:

    def post_install():
        if (path := Path.home() / ".cargo/bin/sd").exists():
            path.rename(str(Path.home() / ".cargo/bin/sdx"))
        elif (path := Path("/usr/bin/sd")).exists():
            sh.sudo.mv("/usr/bin/sd", "/usr/bin/sdx")
