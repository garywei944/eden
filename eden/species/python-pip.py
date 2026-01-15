import sh

from eden.esh import sys_sh
from eden.eva import Eva

eva = Eva.instance()

if eva.sudo:
    if eva.pkgmgr == "apt":
        pkgname = "python3-pip"
else:
    # check if pip exists
    try:
        sys_sh.python3("-m", "pip", "--version")
    except (sh.CommandNotFound, sh.ErrorReturnCode) as e:
        raise RuntimeError("pip is not installed and sudo is not available to install it") from e
    pkgname = None  # type: ignore[assignment]
