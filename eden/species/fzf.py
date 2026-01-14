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
        shutil.rmtree(Path.home() / ".fzf", ignore_errors=True)
        git.clone("--depth=1", "https://github.com/junegunn/fzf.git", str(Path.home() / ".fzf"))
        sh.Command(str(Path.home() / ".fzf" / "install"))(_in=sh.yes(_out=None, _piped=True))
