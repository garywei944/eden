from eden.eva import Eva
from eden.sh import esh as sh

eva = Eva.instance()

if eva.sudo:
    if eva.pkgmgr == "apt":
        depends = ["python-pip"]

        def install():
            sh.sudo.python3(
                "-m", "pip", "install", "--upgrade", "--break-system-packages", "virtualenv"
            )
