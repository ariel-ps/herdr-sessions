# Source this file from zsh to load this plugin's commands.
typeset -g _HERDR_SESSIONS_ROOT="${0:A:h}"
typeset -U path
path=("$_HERDR_SESSIONS_ROOT/bin" $path)

__herdr_sessions_ready() {
  command -v herdr >/dev/null 2>&1 || { echo "herdr: not installed" >&2; return 1; }
  command -v jq >/dev/null 2>&1 || { echo "herdr: jq not found" >&2; return 1; }
  [ "$(herdr status server 2>/dev/null | awk '/^status:/{print $2}')" = running ] || {
    echo "herdr: server not running" >&2; return 1
  }
}

# usage: herdr-unlinked
#   Panes with no native session ref. These lose their conversation on restart.
herdr-unlinked() {
  __herdr_sessions_ready || return 1
  local rows
  rows=$(herdr agent list | jq -r '
    .result.agents[]
    | select(.agent_session.value == null)
    | [.pane_id, .agent, .terminal_title_stripped] | @tsv')
  [ -n "$rows" ] || { echo "all agent panes are linked"; return 0; }
  print -r -- "$rows" | column -t -s $'\t'
}

# usage: herdr-link <pane-id> <native-session-id>
#   Agent kind is read back from the pane, so only the ref has to be right.
herdr-link() {
  __herdr_sessions_ready || return 1
  local pane=$1 sid=$2 kind
  [ -n "$pane" ] && [ -n "$sid" ] || { echo "usage: herdr-link <pane-id> <session-id>" >&2; return 2; }
  kind=$(herdr agent list | jq -r --arg p "$pane" '.result.agents[] | select(.pane_id==$p) | .agent')
  [ -n "$kind" ] || { echo "herdr: no agent in $pane" >&2; return 1; }
  herdr pane report-agent-session "$pane" --source "herdr:$kind" --agent "$kind" \
    --agent-session-id "$sid" || return 1
  herdr agent list | jq -r --arg p "$pane" '
    .result.agents[] | select(.pane_id==$p)
    | "\(.pane_id) \(.agent) -> \(.agent_session.value // "STILL UNLINKED")"'
}
