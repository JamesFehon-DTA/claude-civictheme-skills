#!/bin/sh
# PreToolUse hook for the civictheme-skills plugin.
#
# Auto-allow read-only access to the plugin's OWN bundle - the SKILL.md
# reference files under the plugin install root. Skills use progressive
# disclosure (SKILL.md points to references/*.md the agent reads on demand);
# those files live in the plugin cache, outside the project workspace, so in
# default permission mode each reference read raises a separate prompt. This
# grants the read scope the plugin declares for itself, once, at the source.
#
# Scope is deliberately narrow:
#   - only Read/Glob/Grep targets that resolve under $CLAUDE_PLUGIN_ROOT
#   - paths containing ".." are never allowed (no parent-dir escape)
#   - any non-match produces NO output, so the normal permission flow and the
#     user's own allow/deny rules are untouched. This hook never emits "deny".
#
# $1 = plugin root, passed from the hook command as "${CLAUDE_PLUGIN_ROOT}".

root=$1
[ -n "$root" ] || exit 0

payload=$(cat)

# Fast path: skip jq entirely when the bundle path is not even mentioned.
case "$payload" in
  *"$root"*) ;;
  *) exit 0 ;;
esac

target=$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null)

# Reject parent-directory traversal outright.
case "$target" in
  *..*) exit 0 ;;
esac

# Allow only when the target sits under the plugin root.
case "$target" in
  "$root"/*)
    jq -n '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"allow",permissionDecisionReason:"civictheme-skills: auto-allowed read within the plugin bundle (own reference files)."}}'
    ;;
esac

exit 0
