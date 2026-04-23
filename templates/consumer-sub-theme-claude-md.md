<!--
Paste the section below into the CLAUDE.md of a Drupal project that consumes
CivicTheme as a contrib base theme (web/themes/contrib/civictheme/) and
authors a sub-theme against it.

Do not paste this file verbatim — copy only the "## CivicTheme component work"
section. Delete this comment block before committing.
-->

## CivicTheme component work

All CivicTheme component work starts with `civictheme-component-type-selector`. It classifies the request into one of the sub-theme patterns and routes to the correct generator. Do not invoke a generator directly — the selector captures the project context (theme machine name, paths, CivicTheme version) that every downstream skill requires.

**Style-first rule.** When the change is appearance-only (colour, spacing, typography), the selector routes to `civictheme-style-override`, not `civictheme-override-generator`. Prefer SCSS variable overrides over component overrides whenever either would satisfy the need.

**Out of scope — no skill covers these:**

- Portable / self-contained components — components with their own `--prefix-*` token namespace and hardcoded fallbacks alongside CivicTheme token references. These intentionally bypass the CivicTheme mixin system.
- UIKit source authoring. If the task is to add a component to the CivicTheme UIKit, design system, or component library itself (not a sub-theme), stop and open the UIKit repo instead — it has its own CLAUDE.md block and uses `civictheme-uikit-component-generator`.

**GovCMS SaaS constraint.** Custom modules are unavailable; the theme layer is the only PHP extension point. All generated patterns are theme-layer only.
