import sys
import logging
import shutil
from contextlib import suppress
from pathlib import Path
import sh

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("sh").setLevel(logging.INFO)

# sh = sh.bake(_out=sys.stdout, _err=sys.stderr)

Path("/tmp/test_git_init").mkdir(parents=True, exist_ok=True)

with sh.pushd("/tmp/test_git_init"):
    #     shutil.rmtree(".git", ignore_errors=True)
    #     sh.git("init")
    #     # sh.git.remote.add("origin", "git@github.com:garywei944/eva_arch.git")
    #     # sh.git.config("core.excludesFile", ".eva.gitignore")
    #     # sh.git.fetch(depth=1)
    #     # sh.git.reset("--hard", "origin/main")
    #     # if sh.git.branch("--show-current", _out=None) == "master":
    #     #     sh.git.branch("-m", "master", "main")
    #     # else:
    #     #     print(sh.git.branch("--show-current"))
    #     out = sh.git.branch("--show-current")
    #     print(type(out))
    #     print(out)
    #     # sh.git.branch("--set-upstream-to=origin/main", "main")

    shutil.rmtree(".git", ignore_errors=True)
    sh.git("init")
    sh.git.remote.add("origin", "git@github.com:garywei944/eva_arch.git")
    sh.git.config("core.excludesFile", ".eva.gitignore")
    sh.git.fetch(depth=1)
    sh.git.reset("--hard", "origin/main")
    if sh.git.branch("--show-current") == "main":
        sh.git.branch("-m", "master", "main")
    else:
        print("git branch", repr(sh.git.branch("--show-current")))
    sh.git.branch("--set-upstream-to=origin/main", "main")
