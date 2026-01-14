from eden.context import Context
from eden.eva import Eva
from eden.utils.misc import command_exists

ctx = Context.instance()
eva = Eva.instance()

requires_pkgmgr = False

if eva.sudo:
    if ctx.os_id == "arch":
        pkgmgr = "pacman"
    elif eva.pkgmgr == "apt":
        pkgmgr = "apt"
        pkgname = "build-essential"

else:
    assert command_exists("gcc")
    pkgname = None  # type: ignore[assignment]
