from eden.context import Context
from eden.esh import curl, sys_sh
from eden.esh import esh as sh
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

if eva.sudo:
    if eva.pkgmgr == "apt":
        depends = ["gnupg"]
        """
        ```
        curl -SsL https://packages.httpie.io/deb/KEY.gpg | sudo gpg --dearmor \
            -o /usr/share/keyrings/httpie.gpg
        echo "deb [arch=amd64 signed-by=/usr/share/keyrings/httpie.gpg] \
            https://packages.httpie.io/deb ./" | sudo tee /etc/apt/sources.list.d/httpie.list \
                > /dev/null
        sudo apt update
        sudo apt install httpie
        ```
        """

        def pre_install():
            sh.sudo.gpg(
                "--dearmor",
                "-o",
                "/usr/share/keyrings/httpie.gpg",
                _in=curl("https://packages.httpie.io/deb/KEY.gpg"),
            )
            payload = "deb [arch=amd64 signed-by=/usr/share/keyrings/httpie.gpg] " "https://packages.httpie.io/deb ./"
            sh.sudo.tee("/etc/apt/sources.list.d/httpie.list", _in=payload)
            sh.sudo("apt-get", "update")

else:
    depends = ["python", "python-pip"]

    def install():
        sys_sh.python3("-m", "pip", "install", "httpie")
