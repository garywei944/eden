from pathlib import Path

from eden.context import Context
from eden.esh import curl
from eden.esh import esh as sh
from eden.eva import Eva

INSTALL_URL = "https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh"

ctx = Context.instance()
eva = Eva.instance()

depends = ["curl", "git", "zsh"]
# if we don't clone the dotfiles first, then there might be conflicts when cloning the dotfiles.
optdepends = ["eden_dotfiles"]

if eva.sudo and ctx.is_arch:
    pkgname = "oh-my-zsh-git"
else:
    # sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
    def install():
        sh.sh(_in=curl(INSTALL_URL))


def post_install():

    with sh.pushd(Path.home() / ".config/zsh_custom/plugins"):
        sh.git.clone("https://github.com/zsh-users/zsh-autosuggestions", depth=1)
        sh.git.clone("https://github.com/zsh-users/zsh-syntax-highlighting", depth=1)

    with sh.pushd(Path.home()):
        with Path(".zshrc").open("w", encoding="utf-8") as zshrc:
            zshrc.write(". ~/.rc.zsh\n")
