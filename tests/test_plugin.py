"""Run directly: python3 tests/test_plugin.py."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def check_manifest(plugin):
    manifest = tomllib.loads((plugin / 'herdr-plugin.toml').read_text())
    assert manifest['id'] == 'dev.ariel.herdr-sessions'
    assert manifest['version'] == '0.1.0'
    assert manifest['events'] == [
        {
            'on': 'pane.agent_status_changed',
            'command': ['zsh', './hooks/on-pane-agent-status-changed-name.zsh'],
        },
        {
            'on': 'pane.agent_status_changed',
            'command': ['zsh', './hooks/on-pane-agent-status-changed-title.zsh'],
        },
    ]
    assert manifest['actions'] == [
        {
            'id': 'names',
            'title': 'Sync agent names from sessions',
            'command': ['sh', './bin/herdr-agent-name', '--all'],
        },
    ]
    for event in manifest['events']:
        hook = plugin / event['command'][1]
        assert hook.is_file(), hook
        assert os.access(hook, os.X_OK), hook


def check_hook_root_resolution(plugin, home):
    fake_bin = home / 'fake bin'
    fake_bin.mkdir()
    jq = fake_bin / 'jq'
    jq.write_text(
        """#!/bin/sh
case "$2" in
  *pane_id*) printf '%s\\n' 'w1:p1' ;;
  *agent_status*) printf '%s\\n' 'working' ;;
  *agent*) printf '%s\\n' 'claude' ;;
esac
"""
    )
    jq.chmod(0o755)

    stubs = {
        'herdr-agent-name': ['--quiet', '--pane', 'w1:p1'],
        'herdr-title': [
            '--quiet', '--pane', 'w1:p1', '--status', 'working',
            '--agent', 'claude',
        ],
    }
    hooks = {
        'herdr-agent-name': 'on-pane-agent-status-changed-name.zsh',
        'herdr-title': 'on-pane-agent-status-changed-title.zsh',
    }
    for command, expected_arguments in stubs.items():
        executable = plugin / 'bin' / command
        executable.write_text(
            '#!/bin/sh\n'
            '{ printf "%s\\n" "$0"; printf "%s\\n" "$@"; } > "$HOOK_CAPTURE"\n'
        )
        executable.chmod(0o755)
        capture = home / f'{command}.capture'
        env = {
            **os.environ,
            'PATH': f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}",
            'HOOK_CAPTURE': str(capture),
            'HERDR_PLUGIN_EVENT_JSON': '{}',
        }
        env.pop('HERDR_PLUGIN_ROOT', None)
        env.pop('HERDR_PLUGIN_CONFIG_DIR', None)
        for name in [
            'HERDR_AGENT_NAME_OFF',
            'HERDR_TITLE_OFF',
            'HERDR_TITLE_SEP',
            'HERDR_TITLE_BRANCH',
            'HERDR_TITLE_MAX_BRANCH',
        ]:
            env.pop(name, None)
        result = subprocess.run(
            ['zsh', str(plugin / 'hooks' / hooks[command])],
            cwd=home, env=env, text=True, capture_output=True,
        )
        assert result.returncode == 0, result.stderr
        assert capture.read_text().splitlines() == [
            str(executable.resolve()), *expected_arguments,
        ]


def check_custom_herdr(plugin, home):
    executable = home / 'custom-herdr'
    executable.write_text("""#!/bin/sh
case "$*" in
  "status server") printf 'status: running\\n' ;;
  "pane list") printf '%s\\n' '{"result":{"panes":[{"pane_id":"w1:p1","label":"pane","agent":"claude","agent_status":"idle","agent_session":{"value":"s1"},"workspace_id":"w1","tab_id":"w1:t1"}]}}' ;;
  "agent list") printf '%s\\n' '{"result":{"agents":[{"pane_id":"w1:p1","name":"agent-one"}]}}' ;;
  *) exit 2 ;;
esac
""")
    executable.chmod(0o755)
    env = {**os.environ, 'HERDR_BIN_PATH': str(executable)}
    result = subprocess.run(
        [str(plugin / 'bin/herdr-whoami'), '--pane', 'w1:p1'],
        env=env, text=True, capture_output=True,
    )
    assert result.returncode == 0 and result.stdout.strip() == 'agent-one', result
    result = subprocess.run(
        [str(plugin / 'bin/herdr-agents'), '--names'],
        env=env, text=True, capture_output=True,
    )
    assert result.returncode == 0 and result.stdout.strip() == 'agent-one', result
    result = subprocess.run(
        ['zsh', '-fc', 'source "$1/shell.zsh"; __herdr_sessions_ready', 'check', str(plugin)],
        env=env, text=True, capture_output=True,
    )
    assert result.returncode == 0, result


def check():
    # A relocated standalone plugin must work without the old toolkit or siblings.
    with tempfile.TemporaryDirectory(prefix='plugin user ') as temporary:
        home = Path(temporary)
        plugin = home / 'plugin copy'
        shutil.copytree(ROOT, plugin, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        check_manifest(plugin)
        result = subprocess.run(
            ['zsh', '-fc', 'plugin=$1; source "$plugin/shell.zsh"; whence herdr-link herdr-agents', 'check', str(plugin)],
            env={**os.environ, 'HOME': str(home), 'XDG_CONFIG_HOME': str(home / 'config'),
                 'XDG_CACHE_HOME': str(home / 'cache')}, text=True, capture_output=True)
        assert result.returncode == 0, result.stderr
        assert 'herdr-link' in result.stdout
        assert str(plugin / 'bin/herdr-agents') in result.stdout
        check_hook_root_resolution(plugin, home)
        check_custom_herdr(plugin, home)

        # Verify bash forwards literal arguments, cwd, and failures to the implementation.
        commands = ["herdr-unlinked","herdr-link"]
        (plugin / 'shell.zsh').write_text('\n'.join(
            name + '() { printf "%s\\n" "$PWD" "${HERDR_AGENT_ARGS:-}" "$@"; return 7; }'
            for name in commands))
        arguments = ['two words', '$(touch unexpected)', '', '--option']
        for command in commands:
            result = subprocess.run(
                ['bash', '--noprofile', '--norc', '-c',
                 'source "$1/shell.bash"; shift; HERDR_AGENT_ARGS="two flags"; "$@"',
                 'check', str(plugin), command, *arguments], cwd=home,
                env={**os.environ, 'HOME': str(home)}, text=True, capture_output=True)
            assert result.returncode == 7, result.stderr
            assert result.stdout.splitlines() == [str(home.resolve()), os.environ.get('HERDR_AGENT_ARGS', ''), *arguments], result.stdout
        assert not (home / 'unexpected').exists()


if __name__ == '__main__':
    check()
