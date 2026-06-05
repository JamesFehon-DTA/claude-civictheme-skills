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
    * **UIKit Component Generator:** SDC-first authoring for CivicTheme UIKit / design-system repos – generates `packages/sdc/` and `packages/twig/` in one pass. Entry point for UIKit work.
    * **UIKit SCSS Iteration:** SCSS edits to existing UIKit components (spacing, colour, layout, selector-scoped overrides). Entry point for UIKit iteration.
    * **Health Check:** Diagnostics pass – lint + validate + a11y anti-pattern grep, consolidated into one report. Entry point for a status/sanity check.

## Shared Reference Patterns

The handlers consume a set of canonical reference files to ensure consistency across output:

* **`twig-patterns.md`:** Standardized markup practices, including `attributes.addClass()` for root elements.
* **`field-naming.md`:** Consistent Drupal field machine name conventions.
* **`libraries-and-assets.md`:** Management of `libraryOverrides` and frontend assets.
* **`storybook-patterns.md`:** SDC story structure and Storybook conventions.
* **`civictheme-field-storage.md`:** CivicTheme field storage export used as reference data.

Cross-handler references are stored once under `skills/_shared/references/` and symlinked into each handler's `references/` folder. Symlinks resolve at session load time in Claude Code and are followed when the plugin is cached on install, so every handler gets a self-contained copy without duplication in the source tree.

## Deterministic Principles

Skills were created by referencing CivicTheme technical facts:

* **Inheritance:** `libraryOverrides` must be explicitly redeclared in sub-theme overrides.
* **Security:** The `|raw` filter is prohibited (removed in v1.12.2).
* **Extension:** Use full replacement; `{% extends %}` is no longer supported as of v1.11.0.
* **SDC Integration:** An SDC auto-loads its own co-located library (CSS and JS from the component directory). Enhancements targeting existing CivicTheme markup without a new SDC must attach a library manually.

## Repository layout

```
.claude-plugin/
  plugin.json                                   ← plugin manifest (name + version)
  marketplace.json                              ← digital-gov-au marketplace catalog
commands/
  init.md                                       ← /civictheme-skills:init   – bootstrap the CLAUDE.md routing block
  update.md                                     ← /civictheme-skills:update – re-sync the routing block
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
  lint-skills.py                                ← CI structural validator
  inject_claude_md.py                           ← managed-block writer behind init/update
  civictheme-compat-review-prompt.md            ← compatibility review prompt
CHANGELOG.md                                    ← per-release summary
.github/workflows/
  lint.yml                                      ← runs lint-skills.py on PRs
  release.yml                                   ← dispatch-triggered plugin release
```

## Continuous integration

* **`lint.yml`** runs `scripts/lint-skills.py` on every pull request and push to `main`. The linter validates SKILL.md frontmatter, keeps `references/*.md` and in-file citations in sync, verifies the router references every handler directory, resolves every relative markdown link, and parses every fenced ```yaml block. See `scripts/lint-skills.py` for the full check list.
* **`release.yml`** is triggered by `workflow_dispatch` with a `release-level` input (`patch` | `minor` | `major`). It lints, bumps the version in `.claude-plugin/plugin.json`, commits the bump as `GitHub Actions release workflow`, tags `claude-civictheme-skills--v<version>`, pushes to `main`, and publishes a GitHub release with auto-generated notes. No build artefacts – installs go via the plugin marketplace.

## Install

This repo is a Claude Code plugin distributed via the `digital-gov-au` marketplace. The same plugin works in Claude Code and Claude Desktop (local and SSH sessions; Desktop's remote-session mode does not support plugins).

```
/plugin marketplace add JamesFehon-DTA/claude-civictheme-skills
/plugin install civictheme-skills@digital-gov-au
```

Claude Code refreshes the marketplace on startup and pulls new tagged versions automatically. Desktop users re-run `/plugin marketplace update digital-gov-au` to pick up the latest version.

### Filesystem install (for authors iterating on this repo)

When editing skills in this repo and wanting the changes to show up immediately in a consumer project's Claude Code session, symlink individual skill folders into the project's `.claude/skills/` directory. This bypasses the plugin install and reads directly from disk each session.

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

End users should prefer the `/plugin install` path above – symlinks are for contributors whose edits need to land in a live session without a release.

### Legacy `.skill` archive install (deprecated)

Releases up to and including [v1.2.0](https://github.com/JamesFehon-DTA/claude-civictheme-skills/releases/tag/v1.2.0) shipped nine `.skill` archives per release for Claude Desktop. The v1.3.0 plugin migration replaces that flow with a two-step marketplace install. The archives attached to v1.2.0 remain available for users who have not migrated, but no new archives will be produced.

### Routing: inject a CLAUDE.md block into your consumer project

The skill frontmatter handles defaults, but two consumer archetypes need different defaults that only a project CLAUDE.md can express – and a project CLAUDE.md is what stops the manual path winning when an agent is mid-task and not thinking about skills.

**Preferred – let the commands do it.** From the consumer repo root:

```
/civictheme-skills:init      # detect repo type, write the managed routing block into CLAUDE.md
/civictheme-skills:update    # re-sync the block after upgrading the plugin
```

`init` detects the repo type (UIKit via `packages/sdc/`, or a Drupal sub-theme via a `*.info.yml` with `base theme: civictheme`), then writes a managed block delimited by `<!-- BEGIN civictheme-skills … -->` / `<!-- END civictheme-skills -->` markers, creating `CLAUDE.md` if absent. It is idempotent – re-running makes no change and points you at `update`, which re-syncs the block content in place without touching the rest of your file. When the repo type can't be detected, the command asks rather than guessing.

**Manual fallback – paste the section.** The same block bodies live in the templates, for repos that prefer a hand-managed CLAUDE.md:

- **Drupal sub-theme project** – paste the section from [templates/consumer-sub-theme-claude-md.md](templates/consumer-sub-theme-claude-md.md). Pins the type-selector as the required entry point.
- **CivicTheme UIKit / design system repo** – paste the section from [templates/consumer-uikit-claude-md.md](templates/consumer-uikit-claude-md.md). Pins SDC-first authoring, the post-generation toolchain sync loop, and the reserved-`attributes` rule.

Each template file contains a paste-only section plus a header comment explaining what to copy. The commands read these same files, so the injected block and the manual paste stay identical.

**Belt and braces – the SessionStart prime hook.** A CLAUDE.md block only helps when the agent reads CLAUDE.md. The plugin also ships a `SessionStart` hook (`scripts/inject_claude_md.py --mode prime`) that, in a detected CivicTheme repo, injects a terse "route through the skills" primer into context at session start. Because `SessionStart` re-fires with the `compact` matcher after a compaction, the rule is restored exactly when a long, mid-task session would otherwise drop it – the scenario where skills got bypassed. The hook is silent (no output, exit 0) in every non-CivicTheme repo, so it is inert everywhere else. `PreCompact` is not used for this: its stdout is not added to context, so a primer there would do nothing.

**Do not use auto-memory or the user's global `~/.claude/skills/` for team conventions.** Memory is personal and not version-controlled, and a global install can only hold one default – which breaks when one machine needs to work on both a Drupal sub-theme (twig-first) and the UIKit repo (SDC-first) in the same week. Conventions that the whole team needs belong in the consumer project's CLAUDE.md.
