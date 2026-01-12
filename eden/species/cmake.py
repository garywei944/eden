from eden.eva import Eva
from eden.utils.misc import command_exists

eva = Eva.instance()


if not eva.sudo:
    assert command_exists("cmake")

    pkgname = None
