import shutil
from pathlib import Path

from eden.sh import esh as sh
from eden.sh import git

depends = ["git", "eden_config_git", "eden_config_keys"]


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
        git("init")
        git.remote.add("origin", "git@github.com:garywei944/eva_arch.git")
        git.config("core.excludesFile", ".eva.gitignore")
        git.fetch(depth=1)
        git.reset("--hard", "origin/main")
        if git("symbolic-ref", "--short", "HEAD", _out=None).strip() == "master":
            git.branch("-m", "master", "main")
        git.branch("--set-upstream-to=origin/main", "main")
