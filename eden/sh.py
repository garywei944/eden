import sys
from pathlib import Path

import sh
from sh.contrib import bash, git

__all__ = ["DEFAULT_PATHS", "esh", "curl", "which", "sys_which", "git"]

HOME = Path.home()
DEFAULT_PATHS = [str(HOME / ".local/bin"), "/usr/local/bin", "/usr/bin", "/bin"]

# esh = sh.bake(_fg=True)
esh = sh.bake(_in=sys.stdin, _out=sys.stdout, _err=sys.stderr)


def which(cmd) -> str:
    """Find the full path to a command in the default PATHs."""
    return bash(f"command -v {cmd}").strip()


def sys_which(cmd) -> str:
    """Find the full path to a command in the system PATH."""
    return bash(f"command -v {cmd}", _env={"PATH": ":".join(DEFAULT_PATHS)}).strip()


# _piped=True makes wait=False, so RunningCommand is returned
curl = sh.curl.bake("-fsSL", _piped=True)
git = git.bake(_in=sys.stdin, _out=sys.stdout, _err=sys.stderr)

if __name__ == "__main__":
    # test the return types and behavior

    print("Which git:", which("git"))
    print("System which git:", sys_which("git"))
    print("Curling example.com:")

    curl_obj = curl("http://example.com")
    print(type(curl_obj))
    print(curl_obj.stdout.decode())

    branch_name = git("symbolic-ref", "--short", "HEAD")
    print("Current git branch:", branch_name.strip())
    print(type(branch_name))

    branch_name = git("symbolic-ref", "--short", "HEAD", _out=None)
    print("Current git branch:", branch_name.strip())
    print(type(branch_name))
