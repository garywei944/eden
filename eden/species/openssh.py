from eden.eva import Eva
from eden.utils.misc import command_exists

eva = Eva.instance()

if eva.sudo and eva.pkgmgr == "apt":
    pkgname = ["openssh-server", "openssh-client"]

if not eva.sudo:
    assert command_exists("ssh")
    assert command_exists("sshd")
    assert command_exists("ssh-keygen")
    assert command_exists("ssh-keyscan")
    pkgname = None  # type: ignore
