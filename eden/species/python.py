from eden.eva import Eva
from eden.utils.misc import command_exists

eva = Eva.instance()

if eva.sudo:
    if eva.pkgmgr == "apt":
        pkgname = "python3"
else:
    assert command_exists("python3")
    pkgname = None  # type: ignore
