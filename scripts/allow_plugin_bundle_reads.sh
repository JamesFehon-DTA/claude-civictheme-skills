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
# Scope is deliberately narrow and checked against the RESOLVED path:
#   - only Read/Glob/Grep targets whose real path (symlinks + ".." resolved)
#     is inside $CLAUDE_PLUGIN_ROOT - a link inside the bundle that points
#     outside it is rejected, not followed
#   - any non-match, or a missing python3/jq, produces NO output, so the normal
#     permission flow and the user's own allow/deny rules are untouched. The
#     hook never emits "deny" and fails closed.
#
# $1 = plugin root, passed from the hook command as "${CLAUDE_PLUGIN_ROOT}".

root=$1
[ -n "$root" ] || exit 0

payload=$(cat)

# Fast path: skip everything when the bundle path is not even mentioned.
case "$payload" in
  *"$root"*) ;;
  *) exit 0 ;;
esac

target=$(printf '%s' "$payload" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null)
[ -n "$target" ] || exit 0

# Cheap pre-filters before the authoritative resolved-path check.
case "$target" in *..*) exit 0 ;; esac
case "$target" in "$root"/*) ;; *) exit 0 ;; esac

# Authoritative check: resolve symlinks on BOTH the root and the target, then
# require the resolved target to sit inside the resolved root. This is what
# stops an in-bundle symlink pointing outside the bundle from being allowed -
# the earlier string match only checks the literal path. python3 is already a
# plugin dependency (the SessionStart prime hook uses it); if it is absent or
# errors, the check is false, no output is emitted, and the read defers to the
# normal permission prompt (fail closed).
if python3 -c '
import os, sys
root = os.path.realpath(sys.argv[1])
tgt = os.path.realpath(sys.argv[2])
sys.exit(0 if tgt == root or tgt.startswith(root + os.sep) else 1)
' "$root" "$target" 2>/dev/null; then
  jq -n '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"allow",permissionDecisionReason:"civictheme-skills: auto-allowed read within the plugin bundle (own reference files)."}}'
fi

exit 0
