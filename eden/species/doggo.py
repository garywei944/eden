from eden.context import Context
from eden.esh import esh as sh
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

if not eva.sudo or not ctx.is_arch:

    depends = ["curl", "go"]

    def install():
        # sh.sh(_in=curl("https://raw.githubusercontent.com/mr-karan/doggo/main/install.sh"))
        sh.go.install("github.com/mr-karan/doggo/cmd/doggo@latest")
