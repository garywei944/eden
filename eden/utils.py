import sh

from absl import logging
from functools import partial

__all__ = ["sh_", "sh_contrib_"]


def sh_(cmd: str, *args, contrib=False, **kwargs):
    logging.info(f"Running command: {cmd} {' '.join(args)}")
    return getattr(sh.contrib if contrib else sh, cmd)(*args, **kwargs, _fg=True)


sh_contrib_ = partial(sh_, contrib=True)
