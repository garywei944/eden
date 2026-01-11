from eden.eva import Eva

eva = Eva.instance()

is_meta_pkg = True

if eva.sudo:
    depends = [
        "openjdk",
        "jdk8",
        "sdkman",
    ]
else:
    depends = [
        "sdkman",
    ]
