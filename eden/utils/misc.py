import httpx

from eden.sh import esh as sh

__all__ = ["command_exists", "download_file"]


def command_exists(command: str) -> bool:
    """Check if a command exists in the system PATH."""
    try:
        sh.Command(command)
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
