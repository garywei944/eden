import logging

from eden.context import Context
from eden.eva import Eva

logger = logging.getLogger(__name__)

ctx = Context.instance()
eva = Eva.instance()

is_meta_pkg = True

sudo_only_depends = [
    "base-devel",
    # build tools
    "autoconf",
    "pkg-config",
    "checkinstall",
    "libtool",
    "readline",
    "rlwrap",
    # editors and IDEs
    "emacs",
    # develop tools
    "colordiff",
    "dos2unix",
    # debugging and profiling
]

base_depends = [
    "vim",
    "gdb",
    "shfmt",
    "git-delta",
    "git-flow",
    "python-debugpy",
]

if eva.sudo:
    depends = sudo_only_depends + base_depends

    # ! debian 10 doesn't have checkinstall package
    if ctx.os_id == "debian" and ctx.os_version.major < 12:
        logger.warning("Removing 'checkinstall' from depends for debian < 12")
        depends.remove("checkinstall")
else:
    depends = base_depends
