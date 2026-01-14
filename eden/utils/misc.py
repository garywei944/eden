import os
import tempfile
from pathlib import Path

import httpx

from eden.sh import DEFAULT_PATHS
from eden.sh import esh as sh

__all__ = ["command_exists", "download_file"]


def command_exists(command: str, sys_path: bool = False) -> bool:
    """Check if a command exists in the system PATH."""
    try:
        sh.Command(command, search_paths=DEFAULT_PATHS if sys_path else None)
        return True
    except sh.CommandNotFound:
        return False


def download_file(url: str, dest: str) -> None:
    """Download a file from a URL to a destination path."""
    with httpx.stream("GET", url, follow_redirects=True) as response:
        response.raise_for_status()
        with open(dest, "wb") as file:
            for chunk in response.iter_bytes():
                file.write(chunk)


def get_tmpfs_dir() -> Path:
    """Get a temporary directory in tmpfs if available, otherwise use system temp."""
    tmpfs_paths = [Path("/dev/shm"), Path("/run/user") / str(os.getuid()) / "tmp"]
    for path in tmpfs_paths:
        if path.is_dir() and os.access(path, os.W_OK):
            return Path(tempfile.mkdtemp(dir=path))
    return Path(tempfile.mkdtemp())
