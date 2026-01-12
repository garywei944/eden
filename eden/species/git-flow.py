import logging

from eden.context import Context
from eden.eva import Eva

logger = logging.getLogger(__name__)

ctx = Context.instance()
eva = Eva.instance()

VERSION = "0.2.0"

if eva.sudo and ctx.os_id == "arch":
    pkgname = "gitflow-cjs"
else:
    logger.warning(
        "Skipping git-flow installation - prebuilt binaries only available for Arch with sudo."
    )
    pkgname = None  # type: ignore[assignment]
    # with sh.pushd("/tmp"):
    #     download_file(
    #         f"https://github.com/gittower/git-flow-next/releases/download/v{VERSION}/git-flow-next-v{VERSION}-linux-amd64.tar.gz",
    #         f"git-flow-next-v{VERSION}-linux-amd64.tar.gz",
    #     )

    #     with tarfile.open(f"git-flow-next-v{VERSION}-linux-amd64.tar.gz", "r:gz") as tar:
    #         # extract the contents of the tarball to the current directory
    #         tar.extractall()

    #     bin_file = f"git-flow-next-v{VERSION}-linux-amd64/git-flow-v{VERSION}-linux-amd64"

    #     if eva.sudo:
    #         sh.sudo.mv(
    #             bin_file,
    #             "/usr/local/bin/git-flow",
    #         )
    #         sh.chmod("+x", "/usr/local/bin/git-flow")
    #     else:
    #         bin_path = Path.home() / ".local" / "bin"
    #         bin_path.mkdir(parents=True, exist_ok=True)
    #         Path(bin_file).rename(bin_path / "git-flow")
    #         sh.chmod("+x", str(bin_path / "git-flow"))
