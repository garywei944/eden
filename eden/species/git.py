from pathlib import Path

from eden.context import Context
from eden.eva import Eva
from eden.sh import esh as sh
from eden.utils.misc import command_exists

ctx = Context.instance()
eva = Eva.instance()

depends = ["openssh"]
requires_pkgmgr = False

if eva.sudo:
    depends.append("sudo")
    if ctx.os_id == "arch":
        pkgmgr = "pacman"
else:
    assert command_exists("git")
    pkgname = None


def post_install():
    """
    ```
    mkdir -p ~/.ssh
    ssh-keygen -R github.com
    #  ssh-keyscan github.com >> ~/.ssh/known_hosts
    curl -L https://api.github.com/meta | jq -r '.ssh_keys | .[]' | sed -e 's/^/github.com /' \
        >>~/.ssh/known_hosts
    chmod 700 ~/.ssh
    chmod 644 ~/.ssh/known_hosts
    ```
    """
    Path.home().joinpath(".ssh").mkdir(mode=0o700, parents=True, exist_ok=True)
    if Path.home().joinpath(".ssh", "known_hosts").exists():
        sh.ssh_keygen("-R", "github.com")
    sh.ssh_keyscan("github.com", _out=Path.home() / ".ssh/known_hosts")
