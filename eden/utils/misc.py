from eden.sh import esh as sh

__all__ = ["command_exists"]


def command_exists(command: str) -> bool:
    """Check if a command exists in the system PATH."""
    try:
        sh.Command(command)
        return True
    except sh.CommandNotFound:
        return False
