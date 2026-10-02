# Bash entry points reuse the plugin's zsh implementation.
_HERDR_SESSIONS_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
export PATH="$_HERDR_SESSIONS_ROOT/bin:$PATH"

herdr-unlinked() {
  zsh -fc 'source "$1/shell.zsh"; shift; herdr-unlinked "$@"' herdr-unlinked "$_HERDR_SESSIONS_ROOT" "$@"
}

herdr-link() {
  zsh -fc 'source "$1/shell.zsh"; shift; herdr-link "$@"' herdr-link "$_HERDR_SESSIONS_ROOT" "$@"
}
