from eden.context import Context
from eden.eva import Eva
from eden.sh import esh as sh

ctx = Context.instance()
eva = Eva.instance()

if not eva.sudo:
    depends = ["rust"]
    pkgmgr = "cargo"

if eva.sudo and eva.pkgmgr == "apt":
    if eva.sudo and ctx.os_id == "debian" and ctx.os_version.major < 12:
        depends = ["rust"]
        pkgmgr = "cargo"
    else:

        def post_install():
            sh.sudo.ln("-sf", "/usr/bin/batcat", "/usr/local/bin/bat")
