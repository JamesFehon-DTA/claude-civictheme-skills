# CivicTheme Claude Skills
**Repo Name:** `claude-civictheme-skills`

A modular repository of Claude skills designed for deterministic CivicTheme component development and sub-theme maintenance.

## Architecture: Router-plus-Handler

This repository utilizes a distributed architecture to avoid monolithic skill decay and ensure single-responsibility logic.

* **Router (Entry Point):** `civictheme-component-type-selector` orchestrates intent and directs the session to the appropriate handler.
* **Handlers:**
    * **SDC Generator:** For new Single Directory Components.
    * **Override Generator:** For sub-theme component overrides.
    * **Style Override:** Focuses on SCSS variable architecture.
    * **JS Enhancement:** Manages behavior and library overrides.
    * **Paragraph Generator:** Specifically for Drupal paragraph integration.

## Shared Reference Patterns

The handlers consume a set of canonical reference files to ensure consistency across output:

* **Component YAML:** Defined patterns for `.component.yml` structures.
* **Twig Patterns:** Standardized markup practices, including `attributes.addClass()` for root elements.
* **Field Naming:** Consistent Drupal field machine name conventions.
* **Libraries & Assets:** Management of `libraryOverrides` and frontend assets.
* **Variables:** Centralized SCSS theming tokens and variables.

Cross-handler references are stored once under `skills/_shared/references/` and symlinked into each handler's `references/` folder. The Desktop packager follows symlinks, so every `.skill` archive ships a self-contained copy.

## Deterministic Principles

Skills were created by referencing CivicTheme technical facts:

* **Inheritance:** `libraryOverrides` must be explicitly redeclared in sub-theme overrides.
* **Security:** The `|raw` filter is prohibited (removed in v1.12.2).
* **Extension:** Use full replacement; `{% extends %}` is no longer supported as of v1.11.0.
* **SDC Integration:** An SDC auto-loads its own co-located library (CSS and JS from the component directory). Enhancements targeting existing CivicTheme markup without a new SDC must attach a library manually.

## Repository layout

```
skills/
  civictheme-component-type-selector/SKILL.md   ← router
  civictheme-sdc-generator/                     ← handler
  civictheme-override-generator/                ← handler
  civictheme-style-override/                    ← handler
  civictheme-js-enhancement/                    ← handler
  civictheme-paragraph-generator/               ← handler
  _shared/references/                           ← canonical shared refs
scripts/
  build-desktop.sh                              ← builds dist/desktop/*.skill
  package_skill.py                              ← vendored Anthropic packager
dist/desktop/                                   ← gitignored build output
```

## Install

### Claude Code (filesystem)

Link each skill folder into your Claude Code skills directory. Symlinks are resolved at runtime, so shared references load correctly.

```bash
git clone <repo>
cd <repo>
for d in skills/*/; do
  name="$(basename "$d")"
  [ "$name" = "_shared" ] && continue
  ln -s "$(pwd)/$d" "$HOME/.claude/skills/$name"
done
```

For a per-project install, link into the project's `.claude/skills/` directory instead of `~/.claude/skills/`.

### Claude Desktop (parallel `.skill` uploads)

Build the six `.skill` archives and upload them to your Desktop project's skill knowledge:

```bash
./scripts/build-desktop.sh
# then upload all 6 dist/desktop/*.skill files via the Desktop UI
```

Each archive is a standard zip with the skill folder at the top level. The packager dereferences symlinks, so every archive is self-contained — Desktop does not need access to `skills/_shared/`.
