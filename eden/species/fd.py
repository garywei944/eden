from eden.context import Context
from eden.esh import esh as sh
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

if not eva.sudo:
    depends = ["rust"]
    pkgmgr = "cargo"
    pkgname = "fd-find"


if eva.sudo and eva.pkgmgr == "apt":
    pkgname = "fd-find"

    def post_install():
        sh.sudo.ln("-sf", "/usr/bin/fdfind", "/usr/local/bin/fd")
