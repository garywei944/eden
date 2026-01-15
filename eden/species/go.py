import os
from pathlib import Path

from packaging import version as pv

from eden.context import Context
from eden.esh import curl
from eden.esh import esh as sh
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

requires_pkgmgr = False

if (
    not eva.sudo
    or (eva.sudo and ctx.os_id == "debian" and ctx.os_version.major <= 12)
    or (eva.sudo and ctx.os_id == "ubuntu" and ctx.os_version < pv.Version("24.04"))
):
    depends = ["curl", "base-devel"]

    def install():
        sh.sh(_in=curl("https://webi.sh/golang"))

elif eva.sudo and eva.pkgmgr == "apt":
    pkgname = "golang"
elif eva.sudo and ctx.os_id == "arch":
    requires_pkgmgr = True


def post_install():
    paths = os.getenv("PATH", "").split(":")
    os.environ["PATH"] = ":".join(
        [str(Path.home() / "go/bin"), str(Path.home() / ".local/opt/go/bin")] + paths
    )
