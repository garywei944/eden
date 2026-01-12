import os
import sys
from pathlib import Path

import sh

from eden.context import Context
from eden.eva import Eva

sh = sh.bake(_out=sys.stdout, _err=sys.stderr)

ctx = Context.instance()
eva = Eva.instance()

requires_pkgmgr = False

if eva.sudo and eva.pkgmgr == "apt":
    pkgname = "golang"
elif not eva.sudo:

    def install():
        sh.sh(_in=sh.curl("-sS", "https://webi.sh/golang"))


def post_install():
    paths = os.getenv("PATH", "").split(":")
    os.environ["PATH"] = ":".join(
        [str(Path.home() / "go/bin"), str(Path.home() / ".local/opt/go/bin")] + paths
    )
