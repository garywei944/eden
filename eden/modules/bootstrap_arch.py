import logging
import shutil

from eden.context import RuntimeContext
from eden.modules.packages import run

logger = logging.getLogger(__name__)


AUR_HELPERS = {
    "paru": "https://aur.archlinux.org/paru.git",
    "yay": "https://aur.archlinux.org/yay.git",
}


def _build_aur_helper(name: str, repo: str) -> None:
    ctx = RuntimeContext.instance()

    build_root = ctx.eden_home / "build" / name
    build_root.parent.mkdir(parents=True, exist_ok=True)

    if build_root.exists():
        run(["rm", "-rf", str(build_root)])

    logger.info("cloning %s", name)
    run(["git", "clone", repo, str(build_root)])

    logger.info("building %s", name)
    run(["makepkg", "-si", "--noconfirm"], env=None, cwd=str(build_root))


def _ensure_base_devel() -> None:
    ctx = RuntimeContext.instance()

    if not ctx.has_sudo:
        logger.warning(
            "sudo not available: skipping base-devel installation; " "AUR helper build may fail"
        )
        return

    logger.info("ensuring base-devel and git are installed")
    run(["sudo", "pacman", "-S", "--needed", "--noconfirm", "base-devel", "git"])


def ensure_aur_helpers() -> None:
    """
    Ensure both paru and yay are available on Arch Linux.

    Raises RuntimeError if installation fails.
    """
    ctx = RuntimeContext.instance()

    if not ctx.has_pacman:
        logger.debug("not an Arch system; skipping AUR helpers")
        return

    _ensure_base_devel()

    failures: list[str] = []

    for name, repo in AUR_HELPERS.items():
        if shutil.which(name):
            logger.info("%s already installed", name)
            continue

        logger.info("%s not found; attempting installation", name)

        try:
            _build_aur_helper(name, repo)
        except Exception as e:
            logger.error("failed to install %s: %s", name, e)
            failures.append(name)

    if failures:
        raise RuntimeError(f"failed to install AUR helpers: {', '.join(failures)}")

    logger.info("AUR helpers ready: paru, yay")
