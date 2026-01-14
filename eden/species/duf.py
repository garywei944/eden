import shutil

from packaging import version as pv

from eden.context import Context
from eden.esh import esh as sh
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

if (
    not eva.sudo
    or (eva.sudo and ctx.os_id == "ubuntu" and ctx.os_version < pv.Version("22.04"))
    or (eva.sudo and ctx.os_id == "debian" and ctx.os_version.major < 12)
):
    depends = ["git", "go"]

    # build from source
    def install():
        with sh.pushd("/tmp"):
            shutil.rmtree("duf", ignore_errors=True)
            sh.git.clone("https://github.com/muesli/duf.git")
            with sh.pushd("duf"):
                sh.go.build()
