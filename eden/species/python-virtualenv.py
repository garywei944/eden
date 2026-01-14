from packaging import version as pv

from eden.context import Context
from eden.esh import esh as sh
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

if eva.sudo:
    if eva.pkgmgr == "apt":
        depends = ["python-pip"]

        def install():
            if (eva.sudo and ctx.os_id == "ubuntu" and ctx.os_version < pv.Version("24.04")) or (
                eva.sudo and ctx.os_id == "debian" and ctx.os_version.major < 12
            ):
                sh.sudo.python3("-m", "pip", "install", "--upgrade", "virtualenv")
            else:
                sh.sudo.python3(
                    "-m", "pip", "install", "--upgrade", "--break-system-packages", "virtualenv"
                )
