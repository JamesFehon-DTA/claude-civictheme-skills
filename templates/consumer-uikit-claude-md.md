<!--
This is the UIKit variant of the civictheme-skills managed block.

Preferred: run `/civictheme-skills:init` in the repo root – it detects the repo
type and writes the section below into CLAUDE.md inside managed markers, and
`/civictheme-skills:update` re-syncs it when the package ships new guidance.

Manual paste: copy only the "## CivicTheme component work" section (everything
below the closing of this comment). Delete this comment block before committing.
-->

## CivicTheme component work – route through the skills first

This repo is the CivicTheme UIKit (design system), identified by `packages/sdc/` and `packages/twig/`. It is not a Drupal sub-theme. `packages/sdc/` is the source of truth; `packages/twig/` is its generated derivative.

Before creating, porting/migrating in, editing (markup/SCSS/JS), adding a variant or type to, or fixing the rendering of any component here, dispatch the matching skill first. Do not hand-author component files, and do not classify a request as "not component work" because it is a port, a one-file edit, or files you already have:

- New, ported-in, or extended component (new variant/type/option) → `/civictheme-skills:civictheme-uikit-component-generator`
- SCSS change to an existing component → `/civictheme-skills:civictheme-uikit-scss-iteration`
- Validation / pre-PR check → `/civictheme-skills:civictheme-health-check`

Porting a component from another repo is component work – classify before copying, not after. Adding a new variant or type to an existing component (a new enum value, twig branch, draw routine, story) is component work too.

**Dispatch the Skill tool – never substitute a Read of SKILL.md.** Reading the markdown reproduces the prose but skips the SDC-vs-twig package routing and project-context capture. If you reach for Read on a CivicTheme SKILL.md, stop and dispatch the Skill instead – even when the user names a downstream skill by hand.

Conventions the skills enforce and hand-coding breaks:

- `attributes` is the reserved Drupal `Attribute` object, injected automatically. Never declare it under `props`. Render it as `{% if attributes is defined and attributes is not null %}{{- attributes -}}{% endif %}` (see `alert.twig`).
- Theme variables stay light/dark paired (checked by `npm run validate`).
- Regenerate the `packages/twig/` derivative with `npm run components:update`; never hand-edit `packages/twig/` component files.
- `civictheme:` namespace includes become `@organisms/...` (etc.) path namespaces in the twig package via the update script.
- External vendor JS (e.g. D3) loads via a `.storybook/preview-head.html` plus a static vendor dir; the repo gitignores `vendor`, so committed copies live elsewhere.
