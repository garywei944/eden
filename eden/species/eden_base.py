from eden.context import Context
from eden.eva import Eva

ctx = Context.instance()
eva = Eva.instance()

is_meta_pkg = True

# These packages require sudo to install system-wide. So we simple ignore them if we
# don't have sudo permissions.
system_depends = [
    "git",
    "curl",
    "wget",
    "openssh",
    "rsync",
    "ncdu",
    "htop",
    "tmux",
    "zsh",
    "gnupg",
    "ca-certificates",
    "lsb-release",
    "jq",
    "traceroute",
    "nmap",
    "netcat",
    "ncat",
    "tcpdump",
    "ltrace",
    "strace",
]

base_depends = [
    "fzf",
    "ripgrep",
    "fd",
    "bat",
    "tree",
    "dust",
    "bashtop",
    "duf",
    "zoxide",
    "sd",
    "lsd",
    "eza",
    "procs",
    "broot",
    "lolcat",
    "figlet",
    # "neofetch",
    "fastfetch",
]


if eva.sudo:
    depends = system_depends + base_depends
    if ctx.os_id == "ubuntu":
        depends += ["software-properties-common", "apt-transport-https"]
else:
    depends = base_depends
