import sh

__all__ = ["command_exists"]


def command_exists(command: str) -> bool:
    """Check if a command exists in the system PATH."""
    # return (
    #     sh.Command("command")(
    #         ["-v", command],
    #         _out=subprocess.DEVNULL,
    #         _err=subprocess.DEVNULL,
    #         _no_out=True,
    #         _no_err=True,
    #         no_pipe=True,
    #         ok_code=[0, 1],
    #     ).exit_code
    #     == 0
    # )
    try:
        sh.Command(command)
        return True
    except sh.CommandNotFound:
        return False
