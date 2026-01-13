import sys
from pathlib import Path

import sh

sh = sh.bake(_out=sys.stdout, _err=sys.stderr)


def post_install():
    Path.home().joinpath(".ssh").mkdir(mode=0o700, parents=True, exist_ok=True)
    sh.ssh_keygen("-R", "github.com")
    sh.ssh_keyscan("github.com", _out=Path.home() / ".ssh/known_hosts")


post_install()
