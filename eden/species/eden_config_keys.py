import getpass
import os
import shutil
from pathlib import Path

import pyzipper

from eden.context import Context
from eden.esh import esh as sh
from eden.eva import Eva
from eden.utils.misc import get_tmpfs_dir

ctx = Context.instance()
eva = Eva.instance()

depends = ["openssh", "gnupg"]


def install():
    """```
    # Configure SSH key
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    cp -f id_rsa id_rsa.pub ~/.ssh
    chmod 600 ~/.ssh/id_rsa
    chmod 644 ~/.ssh/id_rsa.pub

    # Configure GPG key
    gpg --import garywei944_github*

    # Configure AWS
    mkdir -p ~/.aws
    cp -f config ~/.aws
    chmod 600 ~/.aws/config

    # Configure OSS util
    cp -f .ossutilconfig ~
    chmod 600 ~/.ossutilconfig
    ```
    """
    home = Path.home()
    home.joinpath(".ssh").mkdir(mode=0o700, exist_ok=True, parents=True)

    with sh.pushd(ctx.project_root / "secrets"):
        # sh.unzip("keys.zip", "-d", "keys")
        if ctx.stdin_isatty:
            zip_passwd = getpass.getpass("Enter password for decrypting keys.zip: ")
        else:
            zip_passwd = os.getenv("EDEN_SECRETS_ZIP_PASSWORD", "")

            assert zip_passwd, "EDEN_SECRETS_ZIP_PASSWORD environment variable is not set"

        with get_tmpfs_dir(pushd=True):

            with pyzipper.AESZipFile("keys.zip") as zf:
                zf.extractall(pwd=zip_passwd.encode())

            # ! For security reasons, we need to remove this file after installation

            if ctx.byted:
                eva.exit_hooks.append(
                    lambda: home.joinpath(".ssh", "id_rsa").unlink(missing_ok=True)
                )
                # ssh-keygen -t ed25519 -C "your_email@example.com" -N "" -f ~/.ssh/id_ed25519
                sh.ssh_keygen(
                    "-t",
                    "ed25519",
                    "-C",
                    "gary.wei@bytedance.com",
                    "-N",
                    "",
                    "-f",
                    str(home / ".ssh" / "bytedance"),
                )
                sh.ssh_add(str(home / ".ssh" / "bytedance"))

            shutil.copy("id_rsa", home / ".ssh" / "id_rsa")
            home.joinpath(".ssh", "id_rsa").chmod(0o600)
            shutil.copy("id_rsa.pub", home / ".ssh" / "id_rsa.pub")
            home.joinpath(".ssh", "id_rsa.pub").chmod(0o644)

            # GPG key
            if ctx.stdin_isatty:
                sh.gpg("--import", "garywei944_github.asc", "garywei944_github_key.gpg")
            else:
                gpg_passwd = os.getenv("EDEN_SECRETS_GPG_PASSWORD", "")
                assert gpg_passwd, "EDEN_SECRETS_GPG_PASSWORD environment variable is not set"
                sh.gpg(
                    "--batch",
                    "--yes",
                    "--pinentry-mode",
                    "loopback",
                    "--passphrase",
                    gpg_passwd,
                    "--import",
                    "garywei944_github.asc",
                    "garywei944_github_key.gpg",
                )

            # AWS config
            home.joinpath(".aws").mkdir(exist_ok=True, parents=True)
            shutil.copy("config", home / ".aws" / "config")
            home.joinpath(".aws", "config").chmod(0o600)

            # OSS util config
            shutil.copy(".ossutilconfig", home / ".ossutilconfig")
            home.joinpath(".ossutilconfig").chmod(0o600)
