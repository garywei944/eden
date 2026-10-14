from packaging import version as pv

from eden.context import Context
from eden.esh import esh as sh
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

if eva.sudo:
    if eva.pkgmgr == "apt":
        if (ctx.os_id == "ubuntu" and ctx.os_version < pv.Version("24.04")) or (
            ctx.os_id == "debian" and ctx.os_version.major < 12
        ):
            depends = ["python-pip"]

            def install():
                sh.sudo.python3("-m", "pip", "install", "--upgrade", "virtualenv")

        else:
            # PEP 668 distros: system pip cannot replace apt-owned deps such as packaging
            pkgname = "python3-virtualenv"
