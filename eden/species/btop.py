import tarfile
from pathlib import Path

from eden.context import Context
from eden.esh import esh as sh
from eden.eva import Eva
from eden.utils.misc import download_file, get_tmpfs_dir

ctx = Context.instance()
eva = Eva.instance()

if not eva.sudo or (ctx.os_id == "debian" and ctx.os_version.major < 12):
    depends = ["base-devel"]

    def install():
        """
        ```bash
        cd /tmp
        wget -qO btop.tbz "https://github.com/aristocratos/btop/releases/latest/download/btop-${ARCH}-linux-musl.tbz"
        tar -xjf btop.tbz

        cd btop

        make install PREFIX=$HOME/.local -j$(nproc)

        # optional
        sudo make setcap -j$(nproc)
        sudo make setuid -j$(nproc)
        ```
        """

        with get_tmpfs_dir(pushd=True):
            download_file(
                "https://github.com/aristocratos/btop/releases/download/v1.4.6/btop-x86_64-unknown-linux-musl.tbz",
                "btop.tbz",
            )

            with tarfile.open("btop.tbz", "r:bz2") as tar:
                tar.extractall()

            with sh.pushd("btop"):
                if eva.sudo:
                    sh.sudo.make.install()
                else:
                    sh.make.install(f"PREFIX={str(Path.home() / '.local')}")
