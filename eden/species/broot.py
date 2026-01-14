from eden.context import Context
from eden.esh import esh as sh
from eden.eva import Eva

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

    def install():
        sh.cargo.install("--locked", "--features", "clipboard", "broot")

else:
    depends = ["rust"]

    def install():
        sh.cargo.install("--locked", "--features", "clipboard", "broot")
