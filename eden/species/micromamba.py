import sh

from eden.context import Context
from eden.eva import Eva

sh = sh.bake(_fg=True)

ctx = Context.instance()
eva = Eva.instance()

if eva.sudo and ctx.os_id == "arch":
    pkgname = "micromamba-bin"
else:
    depends = ["curl"]

    def install():
        sh.bash(_in=sh.curl("-sL", "micro.mamba.pm/install.sh"))
