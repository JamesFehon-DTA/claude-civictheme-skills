---
name: civictheme-style-override
description: Generate SCSS variable overrides to change the appearance of CivicTheme components without copying component files. Use when the type-selector returns style_only_override_existing_civictheme_component, or when the user wants to change colours, spacing, borders, or typography in a CivicTheme sub-theme. Always suggest this before civictheme-override-generator when the user describes appearance changes.
---

# CivicTheme Style Override

Generate SCSS variable overrides in a CivicTheme sub-theme. No component files are copied or created.

## Required inputs

- Target component(s) or scope of change (global vs per-component)
- Which properties to change (colour, spacing, border, typography)

## Core rules

- CivicTheme declares all variables with `!default`. Sub-theme overrides must **not** include `!default` — the build imports sub-theme files before base theme files, so the sub-theme value wins.
- Two target files:
  - `components/variables.base.scss` — global design tokens: brand colours, typography scale, spacing particle, breakpoints
  - `components/variables.components.scss` — per-component appearance: colour, border, spacing per component
- For SASS map variables (colour palettes, breakpoints), always use `map.merge()` to extend — never replace the entire map.

## Decision logic

- Change affects brand colours, global typography, or global spacing → `variables.base.scss`
- Change affects one component or a small set → `variables.components.scss`
- Change spans both scopes → use both files
- Variable is a SASS map → `map.merge()`, not full map replacement
- User doesn't know the variable name → infer from pattern `$ct-[component]-[theme]-[subcomponent]-[state]-[property]` and note where to verify in the base theme source

## Variable naming pattern

`$ct-[component]-[theme]-[subcomponent]-[state]-[property]`

Examples:
- `$ct-button-light-primary-background-color`
- `$ct-button-light-primary-hover-background-color`
- `$ct-card-light-title-color`
- `$ct-tag-dark-background-color`

## Reference files

Read before generating:

- `references/variables-and-theming.md` — full naming conventions, three levels of colour override, map extension patterns, SCSS mixin usage, where to find available variables
- `../../references/civictheme-field-storage.md` — storage type, cardinality, and HTML support for every canonical `field_c_p_*` / `field_c_n_*`. Relevant when a requested style change depends on markup shape (e.g. "style the summary text as multi-paragraph rich text"): confirm the backing field actually stores that shape before committing to SCSS selectors that assume paragraph-level descendants. If the field is `string`/`string_long`, the rendered output is a single text node, not wrapped block elements — recommend a markup-level change instead of a style override.

## Output contract

```yaml
files:
  - path: components/variables.base.scss
    purpose: global design token overrides
    contents: |
      <SCSS without !default — omit this file entry if no global changes needed>
  - path: components/variables.components.scss
    purpose: per-component appearance overrides
    contents: |
      <SCSS without !default>
post_generation_notes:
  - Run npm run dist to regenerate CSS.
  - No Drupal cache clear or template changes required for variable-only overrides.
```
