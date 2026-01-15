from pathlib import Path

from eden.esh import esh as sh

depends = ["git", "eden_dotfiles", "ohmyzsh"]


def install():
    """```
    # Configure zsh
    chsh -s /bin/zsh

    # sudo vim /etc/passwd
    wget https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh -O - | sh
    git clone https://github.com/zsh-users/zsh-autosuggestions \
        ~/.config/zsh_custom/plugins/zsh-autosuggestions
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git \
        ~/.config/zsh_custom/plugins/zsh-syntax-highlighting

    echo '. ~/.zsh.bashrc' >>~/.bashrc
    # shellcheck disable=SC2016
    echo '[[ -z "$EVA" ]] && . ~/.profile.sh' >>~/.zprofile
    echo '. ~/.rc.zsh' >~/.zshrc

    # Config
    if [[ ! -d ~/.ssh ]]; then
      mkdir -p ~/.ssh
      chmod 700 ~/.ssh
    fi
    echo 'Include ~/.config/ssh.conf' >>~/.ssh/config```
    """

    sh.chsh("-s", "/bin/zsh")

    with sh.pushd(Path.home() / ".config/zsh_custom/plugins"):
        sh.git.clone("https://github.com/zsh-users/zsh-autosuggestions", depth=1)
        sh.git.clone("https://github.com/zsh-users/zsh-syntax-highlighting", depth=1)

    with sh.pushd(Path.home()):
        with Path(".bashrc").open("a", encoding="utf-8") as bashrc:
            bashrc.write("\n. ~/.zsh.bashrc\n")
        with Path(".zprofile").open("a", encoding="utf-8") as zprofile:
            zprofile.write('\n[[ -z "$EVA" ]] && . ~/.profile.sh\n')
        with Path(".zshrc").open("w", encoding="utf-8") as zshrc:
            zshrc.write(". ~/.rc.zsh\n")
        with Path(".ssh/config").open("a", encoding="utf-8") as ssh_config:
            ssh_config.write("Include ~/.config/ssh.conf\n")
