from eden.context import Context
from eden.esh import esh as sh
from eden.eva import Eva
from eden.utils.misc import command_exists

ctx = Context.instance()
eva = Eva.instance()


requires_pkgmgr = False

depends = ["base-devel", "git"]


def install():
    if command_exists("yay"):
        return
    sh.git.clone("https://aur.archlinux.org/yay-bin.git", "/tmp/yay")
    with sh.pushd("/tmp/yay"):
        sh.makepkg("-si", "--noconfirm")
