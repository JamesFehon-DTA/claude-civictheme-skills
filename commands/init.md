---
description: Detect the CivicTheme repo type and write the civictheme-skills routing block into CLAUDE.md (idempotent bootstrap).
---

Bootstrap the civictheme-skills routing block in this repo's root `CLAUDE.md`. This block forces CivicTheme component work through the skills instead of being hand-authored, which is the failure it exists to prevent.

Run the injector in **init** mode from the repo root:

```sh
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/inject_claude_md.py" --mode init --repo .
```

The script detects the repo type, writes a managed block (delimited by `<!-- BEGIN civictheme-skills ... -->` markers) into `CLAUDE.md`, creating the file if absent, and prints a diff. It is idempotent: if a block is already present it makes no change and tells you to run `/civictheme-skills:update` to re-sync.

Handling the result:

- **Exit 0** – report the printed summary/diff to the user. Done.
- **Exit 3 (ambiguous)** – the repo is neither a detectable UIKit (`packages/sdc/`) nor a detectable sub-theme (`*.info.yml` with `base theme: civictheme`). Do **not** guess. Use the `AskUserQuestion` tool to ask whether this is a CivicTheme UIKit / design-system repo or a Drupal sub-theme, then re-run with the answer:

  ```sh
  python3 "${CLAUDE_PLUGIN_ROOT}/scripts/inject_claude_md.py" --mode init --repo . --type uikit
  # or, for a sub-theme (pass --theme if the machine name isn't auto-detected):
  python3 "${CLAUDE_PLUGIN_ROOT}/scripts/inject_claude_md.py" --mode init --repo . --type sub-theme
  ```

- **Exit 2** – usage/IO error; surface the stderr message.

Do not hand-edit `CLAUDE.md` to insert the block – always go through the script so the markers and content stay managed.
