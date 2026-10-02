# Herdr Sessions

Keep agent names and pane labels in sync, and manage agent sessions.

Commands include `herdr-agents`, `herdr-whoami`, `herdr-unlinked`, and `herdr-link`. Set `HERDR_AGENT_NAME_OFF=1` or `HERDR_TITLE_OFF=1` in `config.sh` to disable either naming hook.

## Install

[Herdr Setup](https://github.com/ariel-ps/herdr-setup) installs prerequisites and lets you select this plugin in `dependencies.json`.

With Herdr 0.9.3+ already installed:

```sh
herdr plugin install ariel-ps/herdr-sessions --ref main --yes
```

Use a commit or release tag instead of `main` to pin a version. Supports macOS, Ubuntu/Debian, and Fedora.

Herdr Setup loads the enabled plugin's helpers in bash or zsh. For a manual installation, source the installed plugin's `shell.bash` in `.bashrc` or `shell.zsh` in `.zshrc`. Bash helpers call the same zsh implementation, so zsh must also be installed; you keep bash as your shell.

Edit `config.sh` in the directory printed by `herdr plugin config-dir dev.ariel.herdr-sessions`. Existing media caches are reused.
