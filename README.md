# Herdr Sessions

Launch coding agents with short commands, keep pane labels in sync, and manage agent sessions.

Commands include `herdr-agents`, `herdr-whoami`, `herdr-unlinked`, and `herdr-link`. Set `HERDR_AGENT_NAME_OFF=1` or `HERDR_TITLE_OFF=1` in `config.sh` to disable either naming hook.

## Agent shortcuts

After installing through Herdr Setup, open a new terminal and run a shortcut
from your project directory:

```sh
claude-danger
codex-danger
```

Install and sign into each agent CLI you want to use separately. These commands
forward all arguments and launch the agent with permission prompts bypassed:

| Command | Agent CLI | Flags added |
| --- | --- | --- |
| `claude-danger` | `claude` | `--dangerously-skip-permissions` |
| `codex-danger` | `codex` | `--dangerously-bypass-approvals-and-sandbox` |
| `cursor-danger` | `agent`, falling back to `cursor-agent` | `--force --trust` |
| `deepcode-danger` | `deepcode` | `--access full-access --trust` |

The scripts work in Bash and Zsh, inside or outside Herdr, on macOS and Linux
(including Fedora). They use your current directory and existing agent settings.
They do not install agents, select models, or run personal dev-env repair hooks.
Existing shell aliases and functions take precedence over these executables.

## Install

[Herdr Setup](https://github.com/ariel-ps/herdr-setup) installs prerequisites and lets you select this plugin in `dependencies.json`.

With Herdr 0.9.3+ already installed:

```sh
herdr plugin install ariel-ps/herdr-sessions --ref main --yes
```

Use a commit or release tag instead of `main` to pin a version. Supports macOS, Ubuntu/Debian, and Fedora.

Herdr Setup loads the enabled plugin's helpers in bash or zsh. For a manual installation, source the installed plugin's `shell.bash` in `.bashrc` or `shell.zsh` in `.zshrc`. Bash helpers call the same zsh implementation, so zsh must also be installed; you keep bash as your shell.

Edit `config.sh` in the directory printed by `herdr plugin config-dir dev.ariel.herdr-sessions`. Existing media caches are reused.

Run the shortcut checks without starting real agents:

```sh
python3 tests/test_shortcuts.py
```

## License

Original project code is licensed under the [MIT License](LICENSE). Third-party code and media retain their own terms; this license does not grant rights to game assets, downloaded themes, or other third-party content.
