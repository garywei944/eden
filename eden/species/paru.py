from eden.context import Context
from eden.eva import Eva
from eden.sh import esh as sh
from eden.utils.misc import command_exists

ctx = Context.instance()
eva = Eva.instance()


requires_pkgmgr = False

depends = ["base-devel", "git"]


def install():
    if command_exists("paru"):
        return

    sh.git.clone("https://aur.archlinux.org/paru.git", "/tmp/paru")
    with sh.pushd("/tmp/paru"):
        sh.makepkg("-si", "--noconfirm")
