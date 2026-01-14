from pathlib import Path

from eden.context import Context
from eden.esh import esh as sh
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

depends = ["git", "openssh", "eden_config_keys"]

requires_pkgmgr = False


def install():
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
