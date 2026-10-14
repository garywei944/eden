from pathlib import Path

from eden.context import Context
from eden.eva import Eva
from eden.utils.misc import download_file

VERSION = "0.17.5"

ctx = Context.instance()
eva = Eva.instance()

depends = ["gdb"]

# Arch ships extra/gdb-dashboard at /usr/share/gdb-dashboard/.gdbinit; elsewhere
# install the single file to ~/.local. ~/.cuda-gdbinit sources whichever exists.
if not (eva.sudo and ctx.is_arch):

    def install():
        dest = Path.home() / ".local" / "share" / "gdb-dashboard" / ".gdbinit"
        dest.parent.mkdir(parents=True, exist_ok=True)
        download_file(f"https://raw.githubusercontent.com/cyrus-and/gdb-dashboard/v{VERSION}/.gdbinit", dest)
