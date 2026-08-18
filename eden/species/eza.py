from eden.context import Context
from eden.esh import esh as sh
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

if eva.sudo and ctx.is_arch:
    pass
else:
    depends = ["rust"]

    def install():
        sh.cargo.install("eza", "--locked")
