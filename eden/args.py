from typing import override

from eden.utils.args_base import ArgsBase

__all__ = ["Args"]


class Args(ArgsBase):
    standalone: bool = False
    dry_run: bool = False

    byted: bool = False

    @override
    def _add_args(self) -> None:
        self.add_argument("-sa", "--standalone")
        self.add_argument("-dr", "--dry_run")
