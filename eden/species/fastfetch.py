import os
import shutil
from pathlib import Path

from packaging import version as pv

from eden.context import Context
from eden.esh import esh as sh
from eden.eva import Eva
from eden.utils.misc import get_tmpfs_dir

ctx = Context.instance()
eva = Eva.instance()


def _install():
    with get_tmpfs_dir(pushd=True):
        sh.git.clone("--depth=1", "https://github.com/fastfetch-cli/fastfetch.git")
        with sh.pushd("fastfetch"):
            Path("build").mkdir(exist_ok=True)
            with sh.pushd("build"):
                if ctx.os_id == "debian" and ctx.os_version.major < 12:
                    sh.cmake(
                        "..",
                        "-DCMAKE_EXE_LINKER_FLAGS=-ldl -lpthread -lm",
                        "-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=OFF",
                    )
                else:
                    sh.cmake("..")
                sh.cmake(
                    "--build", ".", "--target", "fastfetch", "--", f"-j{str(os.cpu_count() or 1)}"
                )

                shutil.copy("fastfetch", Path.home() / ".local" / "bin" / "fastfetch")


if eva.sudo:
    if ctx.os_id == "ubuntu":
        if ctx.os_version < pv.parse("22.04"):
            raise RuntimeError(
                "fastfetch requires Ubuntu 22.04 or higher when installing with sudo."
            )
        if ctx.os_version < pv.parse("25.04"):
            # # install via ppa
            # depends = ["software-properties-common"]

            # def pre_install():
            #     sh.sudo("add-apt-repository", "-y", "ppa:zhangsongcui3371/fastfetch")
            depends = ["git", "cmake", "base-devel"]
            optdepends = ["pkg-config"]
            install = _install

    elif ctx.os_id == "debian":
        if ctx.os_version.major < 13:
            depends = ["git", "cmake", "base-devel"]
            optdepends = ["pkg-config"]
            install = _install
else:
    depends = ["git", "cmake", "base-devel"]
    optdepends = ["pkg-config"]
    install = _install
