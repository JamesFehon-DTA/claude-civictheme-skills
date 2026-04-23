---
name: civictheme-override-generator
description: Generate a full override of an existing CivicTheme SDC component in a Drupal sub-theme. Use when the type-selector returns override_existing_civictheme_component, or when the user needs to replace markup, structure, or behaviour of a base CivicTheme component. Do not use for appearance-only changes — recommend civictheme-style-override instead.
---

# CivicTheme Override Generator

Generate files for a full component override in a CivicTheme sub-theme.

## Required inputs

- `[THEME_MACHINE_NAME]` — sub-theme machine name
- `[BASE_THEME_DIR]` — path to the CivicTheme base theme
- Target component name and atomic level (e.g. `button` / atom, `card` / molecule)
- What the user wants to change: markup, props, JS, or combination
- Whether new props are needed

## Core rules

- Overrides require copying the entire component directory from the base theme.
- `.component.yml` must include `replaces: civictheme:[name]`.
- All base props must be preserved verbatim — removing or renaming any prop breaks base preprocess hooks.
- Existing enum values must match exactly — additional values are safe; removed or renamed values break data.
- New props may be added after the verbatim copy of base props.
- Preserve `{{ attributes }}` on the root element and any `#cache` or `#attached` keys the base template emits — stripping them hides cache metadata that CivicTheme bubbles from its preprocess hooks (see `civictheme-paragraph-generator` §Cacheability for the upstream convention).
- **Maintenance obligation:** after each CivicTheme update, diff the override against the updated base and merge changes.

## Decision logic

- User only wants visual changes → stop; recommend `civictheme-style-override` and explain the maintenance cost avoided.
- Markup or structural changes needed → proceed with the full override.
- New props requested → add them after the verbatim copy of base props.
- Always generate `.component.yml` and `.twig` as complete, valid files. Generate `.scss` and `.js` only if changes are requested to those files.

## Namespace & include strategy

CivicTheme 1.12.x runs two Twig resolution systems side-by-side: Drupal core SDC (machine-name includes like `civictheme:button`) and the `components` contrib module (namespaced paths like `@atoms/button/button.twig`). Upstream CivicTheme uses SDC machine-name includes exclusively — the contrib-module namespaces are registered in `civictheme.info.yml` but not exercised internally.

Rules for overrides:

- Use `{% include 'civictheme:name' %}` inside overridden templates. Do not rewrite upstream machine-name includes to `@atoms/...` or `@civictheme/...` paths — it's a silent stability regression.
- `replaces: civictheme:[name]` in the override's `.component.yml` is the only mechanism needed for SDC machine-name routing. No `.info.yml` edit required for standard overrides.
- A sub-theme only needs its own `components: namespaces:` entry in `.info.yml` if it publishes Twig templates meant to be included by other themes via `@[THEME_MACHINE_NAME]/...` paths. Not required for standard overrides.

See `references/namespace-and-includes.md` for the dual-system explanation, the registration schema used by CivicTheme, and the three failure modes (stale `@namespace/...` include, stale SDC cache, prop API drift).

## Post-generation verification

After generating an override, check:

1. `.component.yml` contains `replaces: civictheme:[name]` and all base props appear verbatim before any new props.
2. The overridden `.twig` uses `civictheme:name` machine-name includes only — no `@civictheme/...` or `@atoms/...` paths.
3. `{{ attributes }}` is present on the root element (required for cache metadata and Drupal attribute injection).
4. `drush cr` has been run — SDC discovery is cached; `replaces:` will not take effect otherwise.
5. If the base theme was recently updated, diff `[BASE_THEME_DIR]/components/[level]/[name]/[name].component.yml` against the override and reconcile prop drift.

## Field naming for custom props

If the override adds fields intended for use in Drupal content, consult `references/field-naming.md` for the correct prefix convention (`field_[THEME_MACHINE_NAME]_` for sub-theme fields).

## Reference files

Read before generating:

- `references/component-yml-patterns.md` — full schema, enum rules, `replaces` directive, override-specific notes
- `references/twig-patterns.md` — prop validation, `only` keyword, class construction
- `references/js-patterns.md` — constructor + root-level `querySelectorAll` init, `data-collapsible-collapsed` state attribute, collapsible panel `!important` pitfall (read when the override reworks component behaviour)
- `references/namespace-and-includes.md` — SDC vs components-contrib resolution, include style for overrides, registration schema, failure modes
- `references/field-naming.md` — field prefix rules for any custom fields added to the override
- `references/component-taxonomy.md` — tier and CSS-only status for all CivicTheme components; use to determine the component's atomic tier and whether it is CSS-only (both affect story pattern selection)
- `references/storybook-patterns.md` — story file structure, args/argTypes mapping from `.component.yml`, Pattern A vs B selection (optional — only if Storybook is present)

## Output contract

```yaml
override_target: civictheme:[component-name]
component_namespace: civictheme:[component-name]  # Drupal routes to the override automatically
files:
  - path: components/[level]/[name]/[name].component.yml
    purpose: override metadata and full prop schema — base props first, new props appended
    contents: |
      <full file contents>
  - path: components/[level]/[name]/[name].twig
    purpose: overridden template
    contents: |
      <full file contents>
  - path: components/[level]/[name]/[name].scss  # only if style changes requested
    purpose: overridden or extended styles
    contents: |
      <full file contents>
  - path: components/[level]/[name]/[name].js  # only if behaviour changes requested
    purpose: overridden behaviour
    contents: |
      <full file contents>
maintenance_notes:
  - After each CivicTheme update, diff components/[level]/[name]/ against [BASE_THEME_DIR]/components/[level]/[name]/ and merge new props, enum values, and template changes.
```
