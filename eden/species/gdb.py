"""
cd /tmp \
&& wget https://sourceware.org/pub/gdb/releases/gdb-16.3.tar.xz \
&& tar -xf gdb-16.3.tar.xz \
&& cd gdb-16.3 \
&& mkdir build && cd build \
&& sudo apt-get install -y build-essential texinfo bison flex \
&& sudo apt-get install -y libgmp-dev libmpfr-dev libreadline-dev texinfo  \
&& sudo apt-get install -y build-essential texinfo libexpat1-dev libncurses-dev \
libbz2-dev liblzma-dev binutils-dev zlib1g-dev \
&& CFLAGS="-g -O2 -fPIC -march=icelake-server" CXXFLAGS="$CFLAGS" \
../configure --disable-nls --disable-werror --with-system-readline --with-system-zlib \
--with-python="$(which python3)" --with-system-gdbinit=/etc/gdb/gdbinit \
--enable-targets=all --enable-tui \
&& make "-j$(nproc)" \
&& sudo make install
"""

import io
import os
import shutil
import tarfile
from pathlib import Path

from eden.context import Context
from eden.eva import Eva
from eden.sh import esh as sh
from eden.utils.misc import command_exists, download_file

ctx = Context.instance()
eva = Eva.instance()

GDB_VERSION = "17.1"


def _install():

    with sh.pushd("/tmp"):
        download_file(
            f"https://sourceware.org/pub/gdb/releases/gdb-{GDB_VERSION}.tar.xz",
            f"gdb-{GDB_VERSION}.tar.xz",
        )

        with tarfile.open(f"gdb-{GDB_VERSION}.tar.xz", "r:xz") as tar:
            tar.extractall()
        with sh.pushd(f"gdb-{GDB_VERSION}"):
            shutil.rmtree("build", ignore_errors=True)
            sh.mkdir("build")
            with sh.pushd("build"):
                build_args = []

                if eva.sudo:
                    build_args.append("--prefix=/usr/local")
                else:
                    build_args.append(f"--prefix={Path.home()}/.local")
                build_args += [
                    "--disable-nls",
                    "--disable-werror",
                    "--with-system-readline",
                    "--with-system-zlib",
                    "--with-system-gdbinit=/etc/gdb/gdbinit",
                    "--enable-targets=all",
                    "--enable-tui",
                ]

                # try to find python3 path
                try:
                    python3_path = io.StringIO()
                    env = os.environ.copy()
                    env["PATH"] = "/usr/local/bin:/usr/bin:/bin"
                    sh.which("python3", _out=python3_path, _env=env)
                    build_args.append(f"--with-python={python3_path.getvalue().strip()}")
                except sh.ErrorReturnCode:
                    pass

                sh.Command("../configure")(build_args)
                sh.make(f"-j{str(os.cpu_count() or 1)}")
                if eva.sudo:
                    sh.sudo.make.install()
                else:
                    sh.make.install()


if not eva.sudo:
    depends = ["git", "base-devel", "python"]

    if command_exists("gdb"):
        pkgname = None
    else:
        install = _install

elif eva.sudo and ctx.os_id == "debian" and ctx.os_version.major < 12:

    depends = [
        "git",
        "base-devel",
        "python",
        "build-essential",
        "texinfo",
        "bison",
        "flex",
        "libgmp-dev",
        "libmpfr-dev",
        "readline",
        "libexpat1-dev",
        "libncurses-dev",
        "libbz2-dev",
        "liblzma-dev",
        "binutils-dev",
        "zlib1g-dev",
    ]

    install = _install
