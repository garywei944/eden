from eden.eva import Eva

eva = Eva.instance()

if eva.sudo and eva.pkgmgr == "apt":
    pkgname = "default-jdk"
