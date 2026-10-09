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
| `agy-danger` | `agy` | `--dangerously-skip-permissions` |
| `claude-danger` | `claude` | `--dangerously-skip-permissions` |
| `cline-danger` | `cline` | `--auto-approve true` |
| `codex-danger` | `codex` | `--dangerously-bypass-approvals-and-sandbox` |
| `continue-danger` | `cn` | `--auto` |
| `copilot-danger` | `copilot` | `--allow-all` |
| `crush-danger` | `crush` | `--yolo` |
| `cursor-danger` | `agent`, falling back to `cursor-agent` | `--force --trust` |
| `deepcode-danger` | `deepcode` | `--access full-access --trust` |
| `droid-danger` | `droid exec` | `--skip-permissions-unsafe` |
| `gemini-danger` | `gemini` | `--skip-trust --approval-mode=yolo` |
| `kimi-danger` | `kimi` | `--yolo` |
| `kiro-danger` | `kiro-cli` | `--trust-all-tools` |
| `opencode-danger` | `opencode` | `--auto` |
| `openhands-danger` | `openhands` | `--always-approve` |
| `qwen-danger` | `qwen` | `--approval-mode=yolo` |
| `claude-danger-docker` | `docker agent run coder` | `--yolo --sandbox` |
| `codex-danger-docker` | `docker agent run coder --model openai/gpt-5.3-codex` | `--yolo --sandbox` |

`droid-danger` is headless and requires a prompt argument or input accepted by
`droid exec`. Tool policies and administrator-enforced blocks still take
precedence over bypass flags where the agent supports them.

The `-docker` variants are not wrappers around `claude`/`codex`. They run
Docker's own [Agent Builder and Runtime](https://docker.github.io/docker-agent/)
(`docker agent`, package `docker-agent`, formerly `cagent`) against a model
provider directly, using its built-in `coder` catalog agent. `--yolo`
auto-approves tool calls (the "danger" part) and `--sandbox` runs the agent
inside a [Docker sandbox](https://docs.docker.com/ai/sandboxes/) VM, so the
auto-approval is contained to that VM. `claude-danger-docker` uses the
`coder` agent's default Anthropic model and needs `ANTHROPIC_API_KEY`;
`codex-danger-docker` overrides it to the OpenAI `gpt-5.3-codex` model and
needs `OPENAI_API_KEY`. Both require the `docker agent` plugin (`docker
agent version` to check) in addition to Docker Desktop's sandbox support.

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

Edit `config.sh` in the directory printed by `herdr plugin config-dir dev.ariel.herdr-sessions`.

## Plugin profile

This is a shell-profile plugin. Stable commands remain in `bin/`, the bash and
zsh integration contracts remain at the repository root, and
`pane.agent_status_changed` adapters live in `hooks/`.

## Development

Run the contract and relocation tests with:

```sh
python3 tests/test_plugin.py
```

Run the shortcut checks without starting real agents:

```sh
python3 tests/test_shortcuts.py
```

## License

Original project code is licensed under the [MIT License](LICENSE). Third-party code and media retain their own terms; this license does not grant rights to game assets, downloaded themes, or other third-party content.
