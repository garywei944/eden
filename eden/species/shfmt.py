from packaging import version as pv

from eden.context import Context
from eden.esh import curl
from eden.esh import esh as sh
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

if (
    not eva.sudo
    or (eva.sudo and ctx.os_id == "ubuntu" and ctx.os_version < pv.Version("22.04"))
    or (eva.sudo and ctx.os_id == "debian" and ctx.os_version.major < 12)
):
    depends = ["curl"]

    # build from source
    def install():
        sh.sh(_in=curl("https://webi.sh/shfmt"))
