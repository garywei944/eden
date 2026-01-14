import logging
import shutil
from pathlib import Path
import sh

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("sh").setLevel(logging.INFO)

# sh = sh.bake(_out=sys.stdout, _err=sys.stderr)

Path("/tmp/test_git_init").mkdir(parents=True, exist_ok=True)

with sh.pushd("/tmp/test_git_init"):
    shutil.rmtree(".git", ignore_errors=True)
    git("init")
    git.remote.add("origin", "git@github.com:garywei944/eva_arch.git")
    git.config("core.excludesFile", ".eva.gitignore")
    git.fetch(depth=1)
    git.reset("--hard", "origin/main")
    if git.branch("--show-current") == "main":
        git.branch("-m", "master", "main")
    else:
        print("git branch", repr(git.branch("--show-current")))
    git.branch("--set-upstream-to=origin/main", "main")
