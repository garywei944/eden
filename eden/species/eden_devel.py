from eden.context import Context
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

is_meta_pkg = True

sudo_only_depends = [
    # build tools
    "autoconf",
    "pkg-config",
    "checkinstall",
    "libtool",
    "readline",
    "rlwrap",
    # editors and IDEs
    "vim",
    "emacs",
    # develop tools
    "colordiff",
    "dos2unix",
    # debugging and profiling
]

base_depends = [
    "gdb",
    "shfmt",
    "git-delta",
    "git-flow",
]

if eva.sudo:
    depends = sudo_only_depends + base_depends

    if ctx.os_id in ["ubuntu", "debian"]:
        depends += ["build-essential"]
    elif ctx.os_id == "arch":
        depends += ["base-devel"]
else:
    depends = base_depends
