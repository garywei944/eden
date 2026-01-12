import sh

from eden.eva import Eva

eva = Eva.instance()

if eva.sudo:
    if eva.pkgmgr == "apt":
        pkgname = "python3-pip"
else:
    # check if pip exists
    try:
        sh.python3("-m", "pip", "--version")
    except (sh.CommandNotFound, sh.ErrorReturnCode):
        raise RuntimeError("pip is not installed and sudo is not available to install it")
    pkgname = None  # type: ignore[assignment]
