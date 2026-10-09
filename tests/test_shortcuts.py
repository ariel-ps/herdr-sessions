"""Exercise portable launchers with fake agents: python3 tests/test_shortcuts.py."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = {
    'agy-danger': ('agy', ['--dangerously-skip-permissions']),
    'claude-danger': ('claude', ['--dangerously-skip-permissions']),
    'cline-danger': ('cline', ['--auto-approve', 'true']),
    'codex-danger': ('codex', ['--dangerously-bypass-approvals-and-sandbox']),
    'continue-danger': ('cn', ['--auto']),
    'copilot-danger': ('copilot', ['--allow-all']),
    'crush-danger': ('crush', ['--yolo']),
    'cursor-danger': ('agent', ['--force', '--trust']),
    'deepcode-danger': ('deepcode', ['--access', 'full-access', '--trust']),
    'droid-danger': ('droid', ['exec', '--skip-permissions-unsafe']),
    'gemini-danger': ('gemini', ['--skip-trust', '--approval-mode=yolo']),
    'kimi-danger': ('kimi', ['--yolo']),
    'kiro-danger': ('kiro-cli', ['--trust-all-tools']),
    'opencode-danger': ('opencode', ['--auto']),
    'openhands-danger': ('openhands', ['--always-approve']),
    'qwen-danger': ('qwen', ['--approval-mode=yolo']),
    'claude-danger-docker': ('docker', ['agent', 'run', 'coder', '--yolo', '--sandbox']),
    'codex-danger-docker': ('docker', [
        'agent', 'run', 'coder', '--model', 'openai/gpt-5.3-codex', '--yolo', '--sandbox',
    ]),
}
SUBCOMMANDS = {
    'opencode-danger': (['run'], ['run', '--auto']),
    'openhands-danger': (['acp'], ['acp', '--always-approve']),
}


def check():
    with tempfile.TemporaryDirectory(prefix='agent user ') as temporary:
        home = Path(temporary).resolve()
        plugin = home / 'relocated plugin'
        shutil.copytree(ROOT / 'bin', plugin / 'bin')
        for name in ('shell.bash', 'shell.zsh'):
            shutil.copy2(ROOT / name, plugin / name)
        tools = home / 'fake tools'
        tools.mkdir()
        (tools / 'dirname').symlink_to(shutil.which('dirname'))
        env = {'HOME': str(home), 'ZDOTDIR': str(home), 'PATH': str(tools)}
        arguments = ['two words', '$(touch unexpected)', '*', '', '--resume', 'a;b']
        for name, (agent, flags) in COMMANDS.items():
            stub = tools / agent
            stub.write_text(f'#!{sys.executable}\n' +
                            'import json, os, sys\n'
                            'print(json.dumps([sys.argv, os.getcwd(), sys.stdin.read(), os.getpid(), '
                            'os.environ.get("HERDR_AGENT")]))\n'
                            'sys.exit(23)\n')
            stub.chmod(0o755)
            for executable in ([agent, 'cursor-agent'] if name == 'cursor-danger' else [agent]):
                if executable != agent:
                    stub = stub.rename(tools / executable)
                for shell in ('bash', 'zsh'):
                    process = subprocess.Popen([
                        shutil.which(shell), '-fc',
                        f'source "$1/shell.{shell}"; shift; exec "$@"',
                        'check', str(plugin), name, *arguments,
                    ], cwd=home, env=env, text=True, stdin=subprocess.PIPE,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = process.communicate('input preserved\n', timeout=10)
                    assert process.returncode == 23, (name, shell, stderr)
                    assert json.loads(stdout) == [
                        [str(stub), *flags, *arguments], str(home), 'input preserved\n', process.pid,
                        {'claude-danger-docker': 'claude',
                         'codex-danger-docker': 'codex'}.get(name),
                    ], stdout
            if name in SUBCOMMANDS:
                passed, expected = SUBCOMMANDS[name]
                result = subprocess.run(
                    [str(plugin / 'bin' / name), *passed, *arguments],
                    cwd=home, env=env, input='input preserved\n',
                    capture_output=True, text=True, timeout=10,
                )
                assert result.returncode == 23, (name, result.stderr)
                actual = json.loads(result.stdout)
                assert actual[:3] == [
                    [str(stub), *expected, *arguments], str(home), 'input preserved\n',
                ], actual
            stub.unlink()
            result = subprocess.run([str(plugin / 'bin' / name)], env=env,
                                    capture_output=True, text=True, timeout=10)
            assert result.returncode == 127, (name, result)
            assert 'not found on PATH' in result.stderr
            assert not result.stdout
        assert not (home / 'unexpected').exists()


if __name__ == '__main__':
    check()
    print('Agent shortcuts passed (bash and zsh).')
