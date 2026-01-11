from eden.eva import Eva

eva = Eva.instance()

is_meta_pkg = True

if eva.sudo:
    depends = [
        "jdk-openjdk",
        "sdkman",
    ]
else:
    depends = [
        "sdkman",
    ]
