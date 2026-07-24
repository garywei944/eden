from eden.context import Context
from eden.esh import esh as sh
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

if eva.sudo and ctx.is_arch:
    pass
else:
    depends = ["curl", "go"]

    def install():
        # sh.sh(_in=curl("https://raw.githubusercontent.com/mr-karan/doggo/main/install.sh"))
        sh.go.install("github.com/rs/curlie@latest")
