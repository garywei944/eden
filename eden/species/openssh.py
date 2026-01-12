from eden.eva import Eva

eva = Eva.instance()

if eva.sudo and eva.pkgmgr == "apt":
    pkgname = ["openssh-server", "openssh-client"]
