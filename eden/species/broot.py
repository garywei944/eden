import sys

import sh

from eden.context import Context
from eden.eva import Eva

sh = sh.bake(_out=sys.stdout, _err=sys.stderr)

ctx = Context.instance()
eva = Eva.instance()

if eva.sudo and ctx.os_id == "arch":
    pkgname = "broot-git"
elif eva.pkgmgr == "apt":
    depends = ["rust"]
    if eva.sudo:
        depends += [
            "build-essential",
            "libxcb1-dev",
            "libxcb-render0-dev",
            "libxcb-shape0-dev",
            "libxcb-xfixes0-dev",
        ]
    pkgmgr = "cargo"

    def install():
        sh.cargo.install("--locked", "--features", "clipboard", "broot")
