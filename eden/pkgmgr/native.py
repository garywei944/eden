import os
import sh
import shutil
import requests

from absl import logging, flags
from attrs import define, field
from overrides import overrides
from morecontext import dirchanged

from .pkgmgr import PackageManager

__all__ = ["NativePM"]


@define
class NativePM(PackageManager): ...
