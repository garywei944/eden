from eden.context import Context
from eden.esh import esh as sh
from eden.eva import Eva
from eden.utils.misc import command_exists, get_tmpfs_dir

ctx = Context.instance()
eva = Eva.instance()


requires_pkgmgr = False

depends = ["base-devel", "git"]


def install():
    if command_exists("yay"):
        return

    with get_tmpfs_dir(pushd=True):
        sh.git.clone("https://aur.archlinux.org/yay-bin.git", "yay")
        with sh.pushd("yay"):
            sh.makepkg("-si", "--noconfirm")
