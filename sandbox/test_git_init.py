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
    sh.gitremote.add("origin", "git@github.com:garywei944/eva_arch.git")
    sh.gitconfig("core.excludesFile", ".eva.gitignore")
    sh.gitfetch(depth=1)
    sh.gitreset("--hard", "origin/main")
    if sh.gitbranch("--show-current") == "main":
        sh.gitbranch("-m", "master", "main")
    else:
        print("git branch", repr(sh.gitbranch("--show-current")))
    sh.gitbranch("--set-upstream-to=origin/main", "main")
