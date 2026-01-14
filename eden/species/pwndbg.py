import shutil
from pathlib import Path

from eden.context import Context
from eden.esh import esh as sh
from eden.eva import Eva

VERSION = "2025.10.20"

ctx = Context.instance()
eva = Eva.instance()

# ! pandbg is not supported without sudo
if not eva.sudo:
    raise RuntimeError("pwndbg installation requires sudo privileges")

if ctx.os_id == "arch":

    def post_install():

        with Path.home().joinpath(".gdbinit").open("w", encoding="utf-8") as gdbinit:
            gdbinit.write("source /usr/share/pwndbg/gdbinit.py\n")

else:
    depends = ["git", "python"]

    def install():
        with sh.pushd(Path.home() / ".local" / "share"):
            shutil.rmtree("pwndbg", ignore_errors=True)
            sh.gitclone("https://github.com/pwndbg/pwndbg")
            with sh.pushd("pwndbg"):
                if ctx.os_id == "debian" and ctx.os_version.major == 10:
                    sh.gitcheckout("debian10-final")
                else:
                    sh.gitcheckout(VERSION)

                sh.Command("./setup.sh")()

    def post_install():
        with Path.home().joinpath(".gdbinit").open("w", encoding="utf-8") as gdbinit:
            gdbinit.write("source ~/.local/share/pwndbg/gdbinit.py\n")
