import shutil
from pathlib import Path

from eden.sh import esh as sh

depends = ["git"]


def install():
    """
    ```
    cd ~ || exit
    rm -fr .git
    git init
    git remote add origin git@github.com:garywei944/eva_arch.git
    git config core.excludesFile .eva.gitignore
    git fetch --depth=1
    git reset --hard origin/main
    git branch -m master main
    git branch --set-upstream-to=origin/main main
    ```
    """
    with sh.pushd(Path.home()):
        shutil.rmtree(".git", ignore_errors=True)
        sh.git("init")
        sh.git.remote.add("origin", "git@github.com:garywei944/eva_arch.git")
        sh.git.config("core.excludesFile", ".eva.gitignore")
        sh.git.fetch(depth=1)
        sh.git.reset("--hard", "origin/main")
        if sh.git.branch("--show-current").strip() == "master":
            sh.git.branch("-m", "master", "main")
        sh.git.branch("--set-upstream-to=origin/main", "main")
