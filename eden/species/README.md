# Species Specification

Basically follows the syntax of Arch Linux PKGBUILD files, with some modifications to fit into Eden's architecture.

## Entries

- `pkgname`: The name of the package.
- `depends`: A list of package dependencies required for the package.
- `is_meta_pkg`: A boolean indicating if the package is a meta package (a group of packages).
- `requires_pkgmgr`: A boolean indicating if the package requires the package manager to be installed before it can be installed.

- `pre_install()`: A method to execute commands before the main installation.
- `install()`: A method to execute the main installation commands for the package.
- `post_install()`: A method to execute commands after the main installation.
