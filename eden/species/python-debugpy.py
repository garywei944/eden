from eden.context import Context
from eden.esh import sys_sh
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

if eva.sudo and ctx.os_id == "arch":
    pass
else:
    depends = ["python", "python-pip"]

    def install():
        sys_sh.python3("-m", "pip", "install", "debugpy")
