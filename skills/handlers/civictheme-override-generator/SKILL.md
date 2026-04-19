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
- **Maintenance obligation:** after each CivicTheme update, diff the override against the updated base and merge changes.

## Decision logic

- User only wants visual changes → stop; recommend `civictheme-style-override` and explain the maintenance cost avoided.
- Markup or structural changes needed → proceed with the full override.
- New props requested → add them after the verbatim copy of base props.
- Always generate `.component.yml` and `.twig` as complete, valid files. Generate `.scss` and `.js` only if changes are requested to those files.

## Field naming for custom props

If the override adds fields intended for use in Drupal content, consult `references/field-naming.md` for the correct prefix convention (`field_[THEME_MACHINE_NAME]_` for sub-theme fields).

## Reference files

Read before generating:

- `references/component-yml-patterns.md` — full schema, enum rules, `replaces` directive, override-specific notes
- `references/twig-patterns.md` — prop validation, `only` keyword, class construction
- `references/field-naming.md` — field prefix rules for any custom fields added to the override

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
