import shutil
import sys
from pathlib import Path

import sh

from eden.context import Context
from eden.eva import Eva

sh = sh.bake(_out=sys.stdout, _err=sys.stderr)

ctx = Context.instance()
eva = Eva.instance()

if eva.sudo and ctx.os_id == "arch":
    pkgname = "bashtop-git"
elif eva.sudo and ctx.os_id == "ubuntu":
    depends = ["software-properties-common"]

    def pre_install():
        sh.sudo.add_apt_repository("-y", "ppa:bashtop-monitor/bashtop")

else:
    depends = ["git", "eden_devel"]

    def install():
        """
        ```bash
        python3 -m pip install bpytop --upgrade --break-system-packages \
        && git clone --depth 1 https://github.com/aristocratos/bashtop.git /tmp/bashtop \
        && cd /tmp/bashtop \
        && sudo make install \
        && rm -fr /tmp/bashtop
        ```
        """
        shutil.rmtree("/tmp/bashtop", ignore_errors=True)
        sh.python3("-m", "pip", "install", "--upgrade", "--break-system-packages", "bpytop")
        sh.git.clone("--depth", "1", "https://github.com/aristocratos/bashtop.git", "/tmp/bashtop")
        with sh.pushd("/tmp/bashtop"):
            if eva.sudo:
                sh.sudo.make.install()
            else:
                sh.make.install(f"PREFIX={str(Path.home() / '.local')}")
