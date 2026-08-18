import os
from pathlib import Path

from eden.context import Context
from eden.esh import curl
from eden.esh import esh as sh
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

requires_pkgmgr = False

if eva.sudo and ctx.is_arch:
    requires_pkgmgr = True
    pkgmgr = "pacman"
else:
    depends = ["curl"]

    def install():
        sh.sh(_in=curl("https://pixi.sh/install.sh"))

    def post_install():
        pixi_home = Path(os.getenv("PIXI_HOME") or Path.home() / ".pixi").expanduser()
        pixi_bin_dir = Path(os.getenv("PIXI_BIN_DIR") or pixi_home / "bin").expanduser()
        paths = os.getenv("PATH", "").split(":")
        os.environ["PATH"] = ":".join([str(pixi_bin_dir)] + paths)
