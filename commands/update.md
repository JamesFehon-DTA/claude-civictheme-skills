---
description: Re-sync the civictheme-skills routing block in CLAUDE.md to the current package guidance (idempotent, in place).
---

Re-sync the civictheme-skills routing block in this repo's root `CLAUDE.md` to the guidance shipped with the installed package version. Use this after upgrading the plugin, or any time the block may be stale.

Run the injector in **update** mode from the repo root:

```sh
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/inject_claude_md.py" --mode update --repo .
```

The script replaces the content **between** the `<!-- BEGIN civictheme-skills ... -->` and `<!-- END civictheme-skills -->` markers in place, leaving the rest of `CLAUDE.md` untouched. If no block exists it inserts one (same as `init`). If duplicate blocks exist it collapses them to one. Re-running on an unchanged repo is byte-stable (no change). It prints a diff of what changed.

Handling the result:

- **Exit 0** – report the printed summary/diff. If it says "already current – no change", say so plainly.
- **Exit 3 (ambiguous)** – repo type undetectable. Do **not** guess. Ask via `AskUserQuestion` (UIKit vs Drupal sub-theme), then re-run with `--type uikit` or `--type sub-theme` (add `--theme NAME` for a sub-theme if the machine name isn't auto-detected).
- **Exit 2** – usage/IO error; surface the stderr message.

Do not hand-edit the managed block – always re-sync through the script.
