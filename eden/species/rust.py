import os
from pathlib import Path

from eden.context import Context
from eden.esh import curl
from eden.esh import esh as sh
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

requires_pkgmgr = False

if eva.sudo and ctx.os_id == "arch":
    requires_pkgmgr = True
    pkgname = "rust"
else:
    depends = ["curl"]

    def install():
        # curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
        sh.sh("-s", "--", "-y", _in=curl("--proto", "=https", "--tlsv1.2", "https://sh.rustup.rs"))


def post_install():
    paths = os.getenv("PATH", "").split(":")
    os.environ["PATH"] = ":".join([str(Path.home() / ".cargo/bin")] + paths)
