from eden.context import Context
from eden.eva import Eva
from eden.sh import esh as sh

ctx = Context.instance()
eva = Eva.instance()

if not eva.sudo:
    depends = ["rust"]
    pkgmgr = "cargo"


if eva.sudo and eva.pkgmgr == "apt":
    pkgname = "fd-find"

    def post_install():
        sh.sudo.ln("-sf", "/usr/bin/fdfind", "/usr/local/bin/fd")
