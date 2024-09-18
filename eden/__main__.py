import sys
import sh
import questionary
from absl import logging, flags, app

from .context import Context, OSType
from .eden import Eden

FLAGS = flags.FLAGS
flags.DEFINE_bool("config_sudo", True, "Configure sudo")
flags.DEFINE_alias("cs", "config_sudo")
flags.DEFINE_bool("config_keys", True, "Configure keys")
flags.DEFINE_alias("ck", "config_keys")


def main(argv: list[str]):
    # logging.set_verbosity(logging.INFO)

    ctx = Context()

    if ctx.root_privileges:
        logging.error("Please run this script without sudo")
        sys.exit(1)

    eden = Eden(ctx)

    # For readability, all actions are stated explicitly here

    # 0. Configure sudo
    if FLAGS.config_sudo:
        eden.config_sudo()
    else:
        logging.info("Skipping configuring sudo")

    # 1. Set up package manager
    eden.pkgmgr.setup_pkgmgr()

    # 2. Configure keys
    if FLAGS.config_keys:
        eden.config_keys()
    else:
        logging.info("Skipping configuring keys")

    # 3. Upgrade system
    eden.pkgmgr.upgrade_system()

    # 4. Install Evangelion Command Collection (ECC)
    eden.install_ecc()

    # 5. Configure dotfiles
    eden.config_dotfiles()

    # 6. Configure shell
    eden.config_shell()

app.run(main)
