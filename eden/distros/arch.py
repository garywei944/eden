import os
import sh
import shutil
import requests

from absl import logging

from .distro import PackageManager, Distro


class PACMAN(PackageManager):
    flags = ["--noconfirm", "--assume-installed"]

    def setup(self, rank_mirrors: bool = True):
        logging.info("Setting up pacman")
        with sh.sudo(_with=True):
            # echo 'MAKEFLAGS="-j$(nproc)"' | sudo tee -a /etc/makepkg.conf
            sh.tee("-a", "/etc/makepkg.conf", _in=sh.echo('MAKEFLAGS="-j$(nproc)"'))

            # sudo pacman -Syu --noconfirm
            sh.pacman("-Sy", _fg=True)
            sh.pacman(
                "-S",
                *self.flags,
                "base-devel",
                "git",
                "pacman-contrib",
                _fg=True,
            )

            # rank mirrors
            # sudo cp /etc/pacman.d/mirrorlist /etc/pacman.d/mirrorlist.bak
            # export COUNTRY=US
            # curl -s "https://archlinux.org/mirrorlist/?country=US&protocol=http&protocol=https&ip_version=4&ip_version=6&use_mirror_status=on" |
            #   sed -e 's/^#Server/Server/' -e '/^#/d' |
            #   rankmirrors -n 5 - |
            #   sudo tee /etc/pacman.d/mirrorlist
            if self.ctx.sudo and rank_mirrors:
                logging.info("Ranking mirrors")
                sh.cp("/etc/pacman.d/mirrorlist", "/etc/pacman.d/mirrorlist.bak")
                # read COUNTRY from the environment
                country = os.getenv("COUNTRY", "US")
                url = f"https://archlinux.org/mirrorlist/?country={country}&protocol=http&protocol=https&ip_version=4&ip_version=6&use_mirror_status=on"
                response = requests.get(url)

                # 4. Filter the content using Python (replacing sed functionality)
                mirrorlist = response.text
                filtered_mirrorlist = []
                for line in mirrorlist.splitlines():
                    if line.startswith("#Server"):
                        # Uncomment lines that start with #Server
                        line = line.lstrip("#")
                    if not line.startswith("#"):
                        filtered_mirrorlist.append(line)

                filtered_mirrorlist_text = "\n".join(filtered_mirrorlist)
                # Use subprocess to run rankmirrors and pipe the output to sudo tee
                sh.tee(
                    "/etc/pacman.d/mirrorlist",
                    _in=sh.rankmirrors("-n", "5", "-", _in=filtered_mirrorlist_text),
                )

    def upgrade_system(self):
        sh.sudo.pacman("-Su", *self.flags, _fg=True)

    def _install_package(self, package: str):
        sh.sudo.pacman("-S", *self.flags, *package, _fg=True)


class PARU(PACMAN):
    def setup(self):
        super().setup()

        # TODO: check if paru is already installed

        # install paru
        sh.git.clone("https://aur.archlinux.org/paru.git", "--depth=1", _fg=True)
        os.chdir("paru")
        sh.makepkg("-si", "--needed", "--noconfirm", _fg=True)
        os.chdir("..")
        shutil.rmtree("paru")

    def _install_package(self, package: str):
        sh.paru("-S", *self.flags, *package, _fg=True)


class YAY(PACMAN):
    def setup(self):
        super().setup()

        # TODO: check if yay is already installed

        # install yay
        sh.git.clone("https://aur.archlinux.org/yay.git", "--depth=1", _fg=True)
        os.chdir("yay")
        sh.makepkg("-si", "--needed", "--noconfirm", _fg=True)
        os.chdir("..")
        shutil.rmtree("yay")

    def _install_package(self, package: str):
        sh.yay("-S", *self.flags, *package, _fg=True)


class ArchLinux(Distro):
    def __init__(self, ctx):
        super().__init__(ctx)

        self.package_manager = PARU(ctx)
