import os
import sys
from pathlib import Path

import sh

__all__ = ["DEFAULT_PATHS", "esh", "curl", "which", "sys_which"]

HOME = Path.home()
DEFAULT_PATHS = [str(HOME / ".local/bin"), "/usr/local/bin", "/usr/bin", "/bin"]

esh = sh.bake(_out=sys.stdout, _err=sys.stderr)
which = sh.which
sys_which = sh.which.bake(_env={**os.environ, "PATH": ":".join(DEFAULT_PATHS)})
curl = sh.curl.bake("-fsSL", _piped=True)
