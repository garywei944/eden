from eden.eva import Eva

eva = Eva.instance()

is_meta_pkg = True

if eva.sudo:
    depends = [
        "python",
        "python-pip",
        "python-venv",
        "micromamba",
    ]
else:
    depends = [
        "micromamba",
    ]
