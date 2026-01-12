from eden.context import Context
from eden.eva import Eva
from eden.sh import curl
from eden.sh import esh as sh

ctx = Context.instance()
eva = Eva.instance()

if eva.sudo and ctx.os_id == "arch":
    pkgname = "sdkman-bin"
else:
    depends = ["curl", "zip", "unzip"]

    def install():
        sh.bash(_in=curl("https://get.sdkman.io"))
