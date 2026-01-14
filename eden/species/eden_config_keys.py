import getpass
import os
import shutil
from pathlib import Path

import pyzipper

from eden.context import Context
from eden.sh import esh as sh

ctx = Context.instance()

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
        try:
            # sh.unzip("keys.zip", "-d", "keys")
            if ctx.stdin_isatty:
                zip_passwd = getpass.getpass("Enter password for decrypting keys.zip: ")
            else:
                zip_passwd = os.getenv("ENEN_SECRETS_ZIP_PASSWORD", "")

            Path("keys").mkdir(exist_ok=True)
            with pyzipper.AESZipFile("keys.zip") as zf:
                zf.extractall("keys", pwd=zip_passwd.encode())

            with sh.pushd("keys"):
                shutil.copy("id_rsa", home / ".ssh" / "id_rsa")
                home.joinpath(".ssh", "id_rsa").chmod(0o600)
                shutil.copy("id_rsa.pub", home / ".ssh" / "id_rsa.pub")
                home.joinpath(".ssh", "id_rsa.pub").chmod(0o644)

                # GPG key
                if ctx.stdin_isatty:
                    sh.gpg("--import", "garywei944_github.asc", "garywei944_github_key.gpg")
                else:
                    gpg_passwd = os.getenv("ENEN_SECRETS_GPG_PASSWORD", "")
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
        finally:
            # cleanup
            shutil.rmtree("keys", ignore_errors=True)
