import logging
import os
from abc import ABC
from argparse import ArgumentParser, ArgumentTypeError, Namespace
from functools import partial
from typing import Self, final, get_args, get_origin, override

from tap import Tap

from eden.utils.python_tricks import freeze_dataclass
from eden.utils.singleton import Singleton

__all__ = [
    "ArgsBase",
    "str2bool",
    "add_bool_arg",
    "move_arg_from_to",
    "env_to_bool",
    "arg_env_consistent_bool",
]

logger = logging.getLogger(__name__)


class ArgsBase(Tap, Singleton, ABC):
    """Base class for argument parsing using Tap.

    Supports
    - Type hinting
    - Automatic argument parsing
    - Singleton pattern with Dependency Injection
    """

    @final
    def __init__(self, args: list[str] | None = None, *, frozen: bool = True) -> None:
        self.parser: Self = self
        self.args: Self = self
        super().__init__(explicit_bool=True, allow_abbrev=False)

        self.parse_args(args=args, known_only=True)

        # only for backward compatibility
        self.unknown_args = self.extra_args

        if frozen:
            freeze_dataclass(self.__class__)

    def _add_args(self) -> None:
        """Add arguments to the parser.

        Equivalent to self.configure(), only keep for backward compatibility.
        """

    @final
    @override
    def configure(self) -> None:

        # The Tap accepts `--ports p1 p2 p3` as a list input, which is different from
        # `--ports=p1,p2,p3`. To keep backward compatibility, we override them here.
        # self._annotations is a dict of arg name to type hint Types.GenericAlias
        for arg_name, type_hint in self._annotations.items():

            arg_flag, default = f"--{arg_name}", getattr(self, arg_name)
            type_origin, type_args = get_origin(type_hint), get_args(type_hint)

            # 1. handler bool to add_bool_arg
            if type_hint is bool:
                add_bool_arg(self, arg_flag, default=getattr(self, arg_name))
            # 2. handle list or set
            elif type_origin in {list, set}:
                elem_type = type_args[0]
                if elem_type is int:
                    self.add_argument(arg_flag, type=partial(_str2container, int, type_origin))
                elif elem_type is float:
                    self.add_argument(arg_flag, type=partial(_str2container, float, type_origin))
                elif elem_type is bool:
                    self.add_argument(arg_flag, type=partial(_str2container, str2bool, type_origin))
                elif elem_type is str:
                    self.add_argument(arg_flag, type=partial(_str2container, str, type_origin))
            # 3. handle tuple
            elif type_origin is tuple:

                # homogeneous tuple: tuple[int, ...]
                if len(type_args) == 2 and type_args[1] is ...:
                    elem_type = type_args[0]
                    self.add_argument(
                        arg_flag,
                        type=partial(_str2container, elem_type, tuple),
                        default=default,
                    )
                else:
                    self.add_argument(
                        arg_flag,
                        type=partial(_tuple_parser, type_args),
                        default=default,
                    )

        self._add_args()

    @final
    @override
    def process_args(self) -> None:
        self._merge_args()
        self._process_args()
        self._check_args()

    def _merge_args(self) -> None:
        """Merge some arguments for compatibility."""

    def _process_args(self) -> None:
        """Process the arguments after parsing."""

    def _check_args(self) -> None:
        """Check the arguments for validity."""


def str2bool(v: str) -> bool:
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise ArgumentTypeError("Boolean value expected.")


def add_bool_arg(parser: ArgumentParser, *args, default=False, help=None, **kwargs):
    # https://stackoverflow.com/a/43357954

    parser.add_argument(
        *args,
        type=str2bool,
        metavar="BOOLEAN",
        nargs="?",
        const=True,
        default=default,
        help=help,
        **kwargs,
    )


def move_arg_from_to(
    args: Namespace | ArgsBase,
    old_arg: str,
    new_arg: str,
    final_value,
    print_deprecated_msg: bool,
):
    setattr(args, new_arg, final_value)
    setattr(args, old_arg, final_value)  # for backward compatibility
    if print_deprecated_msg:
        logger.warning(
            '[ArgParser] --%s is deprecated, please use "--%s" instead!',
            old_arg,
            new_arg,
        )


def env_to_bool(env_var: str) -> bool:
    return os.getenv(env_var, "0").lower() not in ["0", "false"]


def arg_env_consistent_bool(args: Namespace | ArgsBase, arg_name: str, env_var: str):
    """Make sure argument and environment variable are consistent.

    Taking the logical OR of both values.
    """
    arg_value = bool(getattr(args, arg_name, False))
    env_value = env_to_bool(env_var)

    if arg_value or env_value:
        setattr(args, arg_name, True)
        os.environ[env_var] = "1"
    else:
        setattr(args, arg_name, False)
        os.environ[env_var] = "0"


def _str2container(elem_type, container_type: type = list, value: str = ""):
    if value == "":
        return container_type()
    try:
        return container_type(elem_type(v) for v in value.split(","))
    except Exception as e:
        raise ArgumentTypeError(f"Invalid CSV {elem_type.__name__} list: {value}") from e


def _tuple_parser(type_args, value: str):
    parts = value.split(",")
    if len(parts) != len(type_args):
        raise ArgumentTypeError(f"Expected {len(type_args)} values, got {len(parts)}")

    return tuple(t(p) for t, p in zip(type_args, parts))
