import shutil
from pathlib import Path

from eden.esh import esh as sh

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
        sh.git.init()
        sh.git.remote.add("origin", "git@github.com:garywei944/eva_arch.git")
        sh.git.config("core.excludesFile", ".eva.gitignore")
        sh.git.fetch(depth=1)
        sh.git.reset("--hard", "origin/main")
        if sh.git("symbolic-ref", "--short", "HEAD", _out=None).strip() == "master":
            sh.git.branch("-m", "master", "main")
        sh.git.branch("--set-upstream-to=origin/main", "main")


def post_install():
    with sh.pushd(Path.home()):
        with Path(".bashrc").open("a", encoding="utf-8") as bashrc:
            bashrc.write("\n. ~/.zsh.bashrc\n")
        with Path(".zprofile").open("a", encoding="utf-8") as zprofile:
            zprofile.write('\n[[ -z "$EVA" ]] && . ~/.profile.sh\n')
        with Path(".ssh/config").open("a", encoding="utf-8") as ssh_config:
            ssh_config.write("Include ~/.config/ssh.conf\n")
