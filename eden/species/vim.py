from pathlib import Path

from eden.context import Context
from eden.eva import Eva
from eden.utils.misc import command_exists, download_file

ctx = Context.instance()
eva = Eva.instance()

if not eva.sudo:
    assert command_exists("vim")
    pkgname = None


def post_install():
    """Install vim-plug"""
    Path.home().joinpath(".vim/autoload").mkdir(parents=True, exist_ok=True)
    download_file(
        "https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim",
        Path.home() / ".vim" / "autoload" / "plug.vim",
    )
