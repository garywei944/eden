import logging

from evakit.logging_utils import setup_root_logger

setup_root_logger()

logging.getLogger("sh").setLevel(logging.INFO)
logging.getLogger("httpcore").setLevel(logging.INFO)

import os
from pathlib import Path

from packaging import version as pv

from eden.args import Args
from eden.context import Context
from eden.esh import esh as sh
from eden.eva import Eva

logger = logging.getLogger(__name__)


def main():

    logger.info("Eden main module executed")

    args = Args()
    logger.info("args: %s", args)

    ctx = Context(args=args)
    logger.info("context: %s", ctx)

    # 0. check for os compatibility
    if ctx.os_id not in ["ubuntu", "debian", "arch"]:
        raise RuntimeError(f"Unsupported OS: {ctx.os_id}")
    if ctx.os_id == "ubuntu" and ctx.os_version < pv.Version("20.04"):
        raise RuntimeError(f"Unsupported Ubuntu version: {ctx.os_version.major}")
    if ctx.os_id == "debian" and ctx.os_version < pv.Version("10"):
        raise RuntimeError(f"Unsupported Debian version: {ctx.os_version.major}")
    if ctx.is_root and ctx.os_id == "arch":
        raise RuntimeError("Running as root on Arch is not supported")

    # 1. create projects, sandbox, and byted folders
    home = Path.home()
    (home / ".local" / "bin").mkdir(exist_ok=True, parents=True)
    (home / ".local" / "share").mkdir(exist_ok=True, parents=True)
    (home / ".local" / "share" / "zoxide").mkdir(exist_ok=True, parents=True)
    (home / "projects").mkdir(exist_ok=True, parents=True)
    (home / "sandbox").mkdir(exist_ok=True, parents=True)
    if ctx.byted:
        (home / "byted").mkdir(exist_ok=True, parents=True)

    # TODO(gary): set up proxy

    eva = Eva(
        args=args,
        ctx=ctx,
        targets=[
            f"eden_{t}" if Path(f"eden/species/eden_{t}.py").exists() else t for t in args.targets
        ],
    )
    logger.info("eva: %s", eva)

    # update package manager
    if eva.sudo and not args.dry_run:
        update_pkg_manager()

    eva.build_graph()

    for targets in eva.plan():
        eva.execute(targets)


def update_pkg_manager():
    ctx = Context.instance()

    if ctx.os_id in ["ubuntu", "debian"]:
        sh.sudo.apt.update()
    elif ctx.os_id in ["arch"]:
        sh.sudo.pacman("-Sy")
    else:
        logger.warning("Unsupported OS for package manager update: %s", ctx.os_id)


def setup_env():
    eva = Eva.instance()

    if eva.pkgmgr == "apt":
        os.environ["DEBIAN_FRONTEND"] = "noninteractive"

    # use multiple CPU for cargo builds
    os.environ["CARGO_BUILD_JOBS"] = str(os.cpu_count() or 1)


main()
