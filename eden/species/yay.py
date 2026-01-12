import sys

import sh

from eden.context import Context
from eden.eva import Eva

sh = sh.bake(_out=sys.stdout, _err=sys.stderr)

ctx = Context.instance()
eva = Eva.instance()


requires_pkgmgr = False

depends = ["base-devel", "git"]


def install():
    sh.git.clone("https://aur.archlinux.org/yay-bin.git", "/tmp/yay")
    with sh.pushd("/tmp/yay"):
        sh.makepkg("-si", "--noconfirm")
