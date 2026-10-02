# Herdr Sessions

Keep agent names and pane labels in sync, and manage agent sessions.

Commands include `herdr-agents`, `herdr-whoami`, `herdr-unlinked`, and `herdr-link`. Set `HERDR_AGENT_NAME_OFF=1` or `HERDR_TITLE_OFF=1` in `config.sh` to disable either naming hook.

## Install

[Herdr Setup](https://github.com/ariel-ps/herdr-setup) installs prerequisites and lets you select this plugin in `dependencies.json`.

With Herdr 0.9.3+ already installed:

```sh
herdr plugin install ariel-ps/herdr-sessions --ref main --yes
```

Use a commit or release tag instead of `main` to pin a version. Supports macOS and Ubuntu/Debian Linux.

Herdr Setup loads `shell.zsh` for enabled plugins when a new zsh starts. For a manual installation, source the installed plugin’s `shell.zsh` in your `.zshrc`.

Edit `config.sh` in the directory printed by `herdr plugin config-dir dev.ariel.herdr-sessions`. Existing media caches are reused.
