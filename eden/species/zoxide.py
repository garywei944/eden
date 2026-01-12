from eden.context import Context
from eden.eva import Eva
from eden.sh import esh as sh

ctx = Context.instance()
eva = Eva.instance()

if not eva.sudo or (eva.sudo and ctx.os_id == "debian" and ctx.os_version.major < 12):
    depends = ["rust"]

    def install():
        sh.cargo.install("zoxide", "--locked")
