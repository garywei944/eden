from pathlib import Path

from eden.context import Context
from eden.eva import Eva
from eden.sh import esh as sh

ctx = Context.instance()
eva = Eva.instance()

if not eva.sudo:
    depends = ["rust"]
    pkgmgr = "cargo"
    pkgname = "astree"

    def post_install():
        sh.ln(
            "-sf",
            str(Path.home() / ".cargo" / "bin" / "astree"),
            str(Path.home() / ".local" / "bin" / "tree"),
        )
