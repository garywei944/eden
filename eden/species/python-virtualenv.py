import sh

from eden.eva import Eva

sh = sh.bake(_fg=True)

eva = Eva.instance()

if eva.sudo:
    if eva.pkgmgr == "apt":
        depends = ["python-pip"]

        def install():
            sh.sudo.python3(
                "-m", "pip", "install", "--upgrade", "--break-system-packages", "virtualenv"
            )
