import sys

import sh

from eden.eva import Eva

sh = sh.bake(_out=sys.stdout, _err=sys.stderr)

eva = Eva.instance()

if eva.sudo:
    if eva.pkgmgr == "apt":
        depends = ["python-pip"]

        def install():
            sh.sudo.python3(
                "-m", "pip", "install", "--upgrade", "--break-system-packages", "virtualenv"
            )
