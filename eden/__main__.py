import logging

from eden.utils.logging_utils import setup_root_logger

setup_root_logger()

logging.getLogger("sh").setLevel(logging.INFO)

from pathlib import Path

from packaging import version as pv

from eden.args import Args
from eden.context import Context
from eden.eva import Eva
from eden.sh import esh as sh

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

    # 1. create projects, sandbox, and byted folders
    (Path.home() / "projects").mkdir(exist_ok=True, parents=True)
    (Path.home() / "sandbox").mkdir(exist_ok=True, parents=True)
    if ctx.byted:
        (Path.home() / "byted").mkdir(exist_ok=True, parents=True)

    # TODO(gary): set up proxy

    # update package manager
    if ctx.is_root:
        update_pkg_manager()
    elif ctx.has_sudo:
        with sh.contrib.sudo:
            update_pkg_manager()

    eva = Eva(
        args=args,
        ctx=ctx,
        targets=[f"eden_{t}" for t in args.targets],
    )
    logger.info("eva: %s", eva)

    eva.build_graph()

    for targets in eva.plan():
        eva.execute(targets)


def update_pkg_manager():
    ctx = Context.instance()

    if ctx.os_id in ["ubuntu", "debian"]:
        sh.apt.update()
    elif ctx.os_id in ["arch"]:
        sh.pacman("-Sy")
    else:
        logger.warning("Unsupported OS for package manager update: %s", ctx.os_id)


main()
