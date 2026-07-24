from eden.context import Context
from eden.esh import curl
from eden.esh import esh as sh
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

if eva.sudo and ctx.is_arch:
    pkgname = "sdkman-bin"
else:
    depends = ["curl", "zip", "unzip"]

    def install():
        sh.bash(_in=curl("https://get.sdkman.io"))
