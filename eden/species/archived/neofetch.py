import shutil
from pathlib import Path

from eden.context import Context
from eden.eva import Eva
from eden.sh import esh as sh
from eden.sh import git

ctx = Context.instance()
eva = Eva.instance()

if not eva.sudo:
    depends = ["git", "base-devel"]

    def install():
        with sh.pushd("/tmp"):
            shutil.rmtree("neofetch", ignore_errors=True)
            git.clone("--depth=1", "https://github.com/dylanaraps/neofetch.git")
            with sh.pushd("neofetch"):
                # sed -i 's/\/usr/$(HOME)\/.local/g' Makefile
                path = Path("Makefile")
                text = path.read_text(encoding="utf-8")
                text = text.replace("/usr", f"{Path.home()}/.local")
                path.write_text(text, encoding="utf-8")

                sh.make.install()
