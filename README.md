# CivicTheme Claude Skills
**Repo Name:** `claude-civictheme-skills`

A modular repository of Claude skills designed for deterministic CivicTheme component development and sub-theme maintenance.

## Architecture: Router-plus-Handler

This repository utilizes a distributed architecture to avoid monolithic skill decay and ensure single-responsibility logic.

* **Router (Entry Point):** `civictheme-component-type-selector` orchestrates intent and directs the session to the appropriate handler.
* **Handlers (routed via the type-selector):**
    * **SDC Generator:** For new Single Directory Components.
    * **Override Generator:** For sub-theme component overrides.
    * **Style Override:** Focuses on SCSS variable architecture.
    * **JS Enhancement:** Manages behavior and library overrides.
    * **Paragraph Generator:** Specifically for Drupal paragraph integration.
* **Direct-entry skills (not routed via the type-selector):**
    * **UIKit Component Generator:** SDC-first authoring for CivicTheme UIKit / design-system repos — generates `packages/sdc/` and `packages/twig/` in one pass. Entry point for UIKit work.
    * **UIKit SCSS Iteration:** SCSS edits to existing UIKit components (spacing, colour, layout, selector-scoped overrides). Entry point for UIKit iteration.
    * **Health Check:** Diagnostics pass — lint + validate + a11y anti-pattern grep, consolidated into one report. Entry point for a status/sanity check.

## Shared Reference Patterns

The handlers consume a set of canonical reference files to ensure consistency across output:

* **`twig-patterns.md`:** Standardized markup practices, including `attributes.addClass()` for root elements.
* **`field-naming.md`:** Consistent Drupal field machine name conventions.
* **`libraries-and-assets.md`:** Management of `libraryOverrides` and frontend assets.
* **`storybook-patterns.md`:** SDC story structure and Storybook conventions.
* **`civictheme-field-storage.md`:** CivicTheme field storage export used as reference data.

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
  civictheme-sdc-generator/                     ← handler (routed)
  civictheme-override-generator/                ← handler (routed)
  civictheme-style-override/                    ← handler (routed)
  civictheme-js-enhancement/                    ← handler (routed)
  civictheme-paragraph-generator/               ← handler (routed)

  civictheme-uikit-component-generator/         ← direct entry (UIKit authoring)
  civictheme-uikit-scss-iteration/              ← direct entry (UIKit SCSS edits)
  civictheme-health-check/                      ← direct entry (diagnostics)

  _shared/references/                           ← canonical shared refs
templates/
  consumer-sub-theme-claude-md.md               ← paste into Drupal sub-theme CLAUDE.md
  consumer-uikit-claude-md.md                   ← paste into UIKit repo CLAUDE.md
scripts/
  build-desktop.sh                              ← builds dist/desktop/*.skill
  package_skill.py                              ← vendored Anthropic packager
  lint-skills.py                                ← CI structural validator
  civictheme-compat-review-prompt.md            ← compatibility review prompt
.github/workflows/
  lint.yml                                      ← runs lint-skills.py on PRs
  release.yml                                   ← builds .skill archives on tags
dist/desktop/                                   ← gitignored build output
```

## Continuous integration

* **`lint.yml`** runs `scripts/lint-skills.py` on every pull request and push to `main`. The linter validates SKILL.md frontmatter, keeps `references/*.md` and in-file citations in sync, verifies the router references every handler directory, resolves every relative markdown link, and parses every fenced ```yaml block. See `scripts/lint-skills.py` for the full check list.
* **`release.yml`** is triggered by pushing a `v*.*.*` tag. It lints, runs `scripts/build-desktop.sh`, and attaches the resulting `dist/desktop/*.skill` archives to the GitHub Release.

## Install and routing

Three concerns, three mechanisms. Pick one per concern:

| Concern | Mechanism | Why |
|---|---|---|
| **Discoverability** — Claude can see the skill | Filesystem symlinks into `<project>/.claude/skills/` (Code) or `.skill` archive upload (Desktop) | Skills are loaded at session start from these locations only |
| **Freshness** — the loaded copy matches the repo | Claude Code reads from disk every session; Desktop snapshots at upload time | Edit-and-reload works in Code; Desktop requires re-upload on every release |
| **Routing** — which skill to invoke when the user asks | Skill `description` frontmatter (auto) plus a project CLAUDE.md block (explicit team convention) | Frontmatter handles defaults; CLAUDE.md pins project-specific behaviour frontmatter cannot express |

**Do not use auto-memory or the user's global `~/.claude/skills/` for team conventions.** Memory is personal and not version-controlled, and a global install can only hold one default — which breaks when one machine needs to work on both a Drupal sub-theme (twig-first) and the UIKit repo (SDC-first) in the same week.

### Claude Code (filesystem) — recommended for authors and teammates

Link each skill folder into a project's `.claude/skills/` directory. Check the symlinks into the consumer repo so every teammate gets the same set. Claude Code re-reads from disk each session, so edits in the source clone are visible immediately.

```bash
git clone <repo>              # e.g. into ~/src/claude-civictheme-skills
cd <consumer-project>         # the Drupal sub-theme or UIKit repo
mkdir -p .claude/skills
for d in ~/src/claude-civictheme-skills/skills/*/; do
  name="$(basename "$d")"
  [ "$name" = "_shared" ] && continue
  ln -s "$d" ".claude/skills/$name"
done
```

For a global install that applies to every project on the machine, link into `~/.claude/skills/` instead — but only do this if you work on a single CivicTheme archetype (sub-theme *or* UIKit, not both).

### Claude Desktop (parallel `.skill` uploads) — for users not on Claude Code

Tagged releases ship prebuilt `.skill` archives on the repository's GitHub Releases page — download all attached files and upload them to your Desktop project's skill knowledge. There are nine archives (one per skill: the router, five routed handlers, and three direct-entry skills).

To build the archives locally (for contributing or installing from an untagged commit):

```bash
./scripts/build-desktop.sh
# then upload every dist/desktop/*.skill file via the Desktop UI
```

Each archive is a standard zip with the skill folder at the top level. The packager dereferences symlinks, so every archive is self-contained — Desktop does not need access to `skills/_shared/`.

**Freshness caveat.** Desktop stores each upload as a point-in-time snapshot. Edits to the source repo are not visible to Desktop sessions until the archive is rebuilt and re-uploaded. If the skill and the source repo disagree, trust the source repo — the Desktop copy is stale.

### Routing: paste a CLAUDE.md block into your consumer project

The skill frontmatter handles defaults, but two consumer archetypes need different defaults that only a project CLAUDE.md can express:

- **Drupal sub-theme project** — consuming CivicTheme as a contrib base theme. Paste from [templates/consumer-sub-theme-claude-md.md](templates/consumer-sub-theme-claude-md.md) into the project's CLAUDE.md. Pins the type-selector as the required entry point.
- **CivicTheme UIKit / design system repo** — authoring components directly in `packages/sdc/` and `packages/twig/`. Paste from [templates/consumer-uikit-claude-md.md](templates/consumer-uikit-claude-md.md) into the project's CLAUDE.md. Pins SDC-first authoring and the post-generation toolchain sync loop.

Each template file contains a paste-only section plus a header comment explaining what to copy.
