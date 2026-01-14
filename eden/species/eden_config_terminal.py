from eden.sh import esh as sh

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
