import sys

import sh

__all__ = ["esh", "curl"]


esh = sh.bake(_out=sys.stdout, _err=sys.stderr)
curl = sh.curl.bake("-fsSL", _piped=True)
