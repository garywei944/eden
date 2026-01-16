from typing import override

from eden.utils.args_base import ArgsBase

__all__ = ["Args"]


class Args(ArgsBase):
    targets: list[str] = ["all"]
    excludes: list[str] = []

    standalone: bool = False
    dry_run: bool = False

    byted: bool = False

    @override
    def _add_args(self) -> None:
        # ! note that this make --targets to be separated by spaces, not commas
        self.add_argument("-t", "--targets")
        self.add_argument("-e", "--excludes")

        self.add_argument("-sa", "--standalone")
        self.add_argument("-dr", "--dry_run")
