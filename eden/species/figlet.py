import os
import shutil
from pathlib import Path

from eden.context import Context
from eden.esh import esh as sh
from eden.eva import Eva
from eden.utils.misc import get_tmpfs_dir

ctx = Context.instance()
eva = Eva.instance()

if not eva.sudo:
    depends = ["git", "base-devel"]

    def install():
        with get_tmpfs_dir(pushd=True):
            shutil.rmtree("figlet", ignore_errors=True)
            sh.git.clone("--depth=1", "https://github.com/cmatsuoka/figlet.git")
            with sh.pushd("figlet"):
                # sed -i 's/\/usr\/local/$(HOME)\/.local/g' Makefile
                path = Path("Makefile")
                text = path.read_text(encoding="utf-8")
                text = text.replace("/usr/local", f"{Path.home()}/.local")
                path.write_text(text, encoding="utf-8")

                sh.make(f"-j{str(os.cpu_count() or 1)}")
                sh.make.install()
