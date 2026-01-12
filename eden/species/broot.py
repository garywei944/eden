from eden.context import Context
from eden.eva import Eva
from eden.sh import esh as sh

ctx = Context.instance()
eva = Eva.instance()

if eva.sudo and ctx.os_id == "arch":
    pass
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
