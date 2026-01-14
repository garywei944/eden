import os
import shutil
from pathlib import Path

from eden.context import Context
from eden.eva import Eva
from eden.sh import esh as sh
from eden.sh import git

ctx = Context.instance()
eva = Eva.instance()

if eva.sudo and ctx.os_id == "arch":
    pass
elif eva.sudo and ctx.os_id == "ubuntu":
    depends = ["software-properties-common"]

    def pre_install():
        sh.sudo("add-apt-repository", "-y", "ppa:bashtop-monitor/bashtop")

else:
    depends = ["git", "base-devel", "python", "python-pip"]

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
        git.clone("--depth", "1", "https://github.com/aristocratos/bashtop.git", "/tmp/bashtop")
        with sh.pushd("/tmp/bashtop"):
            sh.make(f"-j{str(os.cpu_count() or 1)}")
            if eva.sudo:
                sh.sudo.make.install()
            else:
                sh.make.install(f"PREFIX={str(Path.home() / '.local')}")
