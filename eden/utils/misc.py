import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import httpx

from eden.esh import DEFAULT_PATHS
from eden.esh import esh as sh

__all__ = ["command_exists", "download_file"]


def command_exists(command: str, sys_path: bool = False) -> bool:
    """Check if a command exists in the system PATH."""
    try:
        sh.Command(command, search_paths=DEFAULT_PATHS if sys_path else None)
        return True
    except sh.CommandNotFound:
        return False


def download_file(url: str, dest: Path | str) -> None:
    """Download a file from a URL to a destination path."""
    with httpx.stream("GET", url, follow_redirects=True) as response:
        response.raise_for_status()
        with Path(dest).open("wb") as file:
            for chunk in response.iter_bytes():
                file.write(chunk)


@contextmanager
def get_tmpfs_dir(pushd: bool = False) -> Iterator[Path]:
    """Get a temporary directory in tmpfs if available, otherwise use system temp."""
    tmpfs_paths = [Path("/dev/shm"), Path("/run/user") / str(os.getuid()) / "tmp"]
    for path in tmpfs_paths:
        if path.is_dir() and os.access(path, os.W_OK):
            with tempfile.TemporaryDirectory(dir=path) as tmpdir:
                if pushd:
                    with sh.pushd(tmpdir):
                        yield Path(tmpdir)
                else:
                    yield Path(tmpdir)
                return
    with tempfile.TemporaryDirectory() as tmpdir:
        if pushd:
            with sh.pushd(tmpdir):
                yield Path(tmpdir)
        else:
            yield Path(tmpdir)
