from eden.context import Context
from eden.esh import curl
from eden.esh import esh as sh
from eden.eva import Eva

INSTALL_URL = "https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh"

ctx = Context.instance()
eva = Eva.instance()

depends = ["curl", "git", "zsh"]

if eva.sudo and ctx.os_id == "arch":
    pkgname = "oh-my-zsh.git."
else:
    # sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
    sh.sh(_in=curl(INSTALL_URL))
