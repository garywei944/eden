import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import httpx

from eden.context import Context
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
    """Get a temporary directory in tmpfs if available, otherwise use system temp.

    Priority:
      1. Environment override (e.g. EDEN_TMPDIR)
      2. GitHub Actions (/tmp)
      3. tmpfs locations
      4. system default
    """

    ctx = Context.instance()

    # 1. Explicit override
    override = os.getenv("EDEN_TMPDIR")
    if override:
        base = Path(override)
    # 2. GitHub Actions
    elif ctx.github_actions:
        base = Path("/tmp")
    # 3. tmpfs candidates
    else:
        base = next(
            (
                p
                for p in (
                    # Path("/dev/shm"),  # ! files in /dev/shm are not executable
                    Path("/run/user") / str(os.getuid()) / "tmp",
                    Path("/mnt/tmpfs"),
                    Path("/scratch"),
                    Path("/tmp"),
                )
                if p.is_dir() and os.access(p, os.W_OK)
            ),
            Path(tempfile.gettempdir()),
        )

    with tempfile.TemporaryDirectory(dir=base) as tmpdir:
        path = Path(tmpdir)
        if pushd:
            with sh.pushd(path):
                yield path
        else:
            yield path
