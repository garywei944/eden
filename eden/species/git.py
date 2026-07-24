from eden.context import Context
from eden.eva import Eva
from eden.utils.misc import command_exists

ctx = Context.instance()
eva = Eva.instance()

requires_pkgmgr = False

if eva.sudo:
    if ctx.is_arch:
        pkgmgr = "pacman"
else:
    assert command_exists("git")
    pkgname = None
