<!--
This is the sub-theme variant of the civictheme-skills managed block.

Preferred: run `/civictheme-skills:init` in the repo root – it detects the repo
type and writes the section below into CLAUDE.md inside managed markers, and
`/civictheme-skills:update` re-syncs it when the package ships new guidance.

Manual paste: copy only the "## CivicTheme component work" section (everything
below the closing of this comment). Delete this comment block before committing.
-->

## CivicTheme component work – route through the skills first

This is a CivicTheme Drupal sub-theme (consumes CivicTheme as a contrib base theme; no `packages/sdc/`). Run `/civictheme-skills:civictheme-component-type-selector` to classify before any component change – including bare "fix the X", "tweak the X", or "the X looks wrong" requests, and ports or one-file edits – then follow its routing. The selector captures the project context (theme machine name, paths, CivicTheme version) every downstream skill needs.

**Dispatch the Skill tool – never substitute a Read of SKILL.md.** Reading the markdown reproduces the prose but skips classification, project-context capture, and the routing handoff. If you reach for Read on a CivicTheme SKILL.md, stop and dispatch the Skill instead – even when the user names a downstream skill by hand ("use `civictheme-js-enhancement`"); run the type-selector first.

**Style-first.** When the change is appearance-only (colour, spacing, typography), the selector routes to `civictheme-style-override`, not `civictheme-override-generator`. Prefer SCSS variable overrides over component overrides whenever either would satisfy the need.

Conventions the skills enforce and hand-coding breaks:

- `attributes` is the reserved Drupal `Attribute` object, injected automatically. Never declare it under `props` in any `*.component.yml`. Render it as `{% if attributes is defined and attributes is not null %}{{- attributes -}}{% endif %}` (see `alert.twig`).

**Out of scope – no skill covers these:**

- Portable / self-contained components – their own `--prefix-*` token namespace and hardcoded fallbacks alongside CivicTheme token references. These intentionally bypass the CivicTheme mixin system.
- UIKit source authoring. To add a component to the CivicTheme UIKit / design system itself (the repo with `packages/sdc/`), open that repo instead – it has its own managed block and uses `civictheme-uikit-component-generator`.

**GovCMS SaaS – dual-context.** SaaS production prohibits custom modules; the local docker scaffold permits them. This stack uses local custom modules (e.g. `dga_content_import`) for development imports. Theme-layer patterns from these skills are SaaS-compatible regardless. Don't apply a flat "no custom modules" rule.
