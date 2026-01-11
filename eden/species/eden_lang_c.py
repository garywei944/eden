from eden.eva import Eva

eva = Eva.instance()

is_meta_pkg = True

if eva.sudo:
    depends = [
        "cmake",
        "ninja",
        "clang",
        "clang-format",
        "ctags",
        "valgrind",
    ]
