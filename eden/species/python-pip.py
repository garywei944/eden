from eden.eva import Eva

eva = Eva.instance()

if eva.sudo:
    if eva.pkgmgr == "apt":
        pkgname = "python3-pip"
