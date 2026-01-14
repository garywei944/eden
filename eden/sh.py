import sys
from pathlib import Path

import sh

__all__ = ["DEFAULT_PATHS", "esh", "curl", "which", "sys_which"]

HOME = Path.home()
DEFAULT_PATHS = [str(HOME / ".local/bin"), "/usr/local/bin", "/usr/bin", "/bin"]

# esh = sh.bake(_fg=True)
esh = sh.bake(_in=sys.stdin, _out=sys.stdout, _err=sys.stderr)


def which(cmd):
    """Find the full path to a command in the default PATHs."""
    return sh.bash("-c", f"command -v {cmd}").strip()


def sys_which(cmd):
    """Find the full path to a command in the system PATH."""
    return sh.bash("-c", f"command -v {cmd}", _env={"PATH": ":".join(DEFAULT_PATHS)}).strip()


curl = sh.curl.bake("-fsSL", _piped=True)
