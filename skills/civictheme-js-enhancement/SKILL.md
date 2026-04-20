---
name: civictheme-js-enhancement
description: Generate JS and CSS enhancements targeting existing CivicTheme markup without creating or modifying an SDC component. Use when the type-selector returns js_css_enhancement_without_sdc_component, or when the user wants to add behaviour or progressive enhancement to existing CivicTheme elements, add a sortable table, add a filterable interaction, or enhance existing markup with JS.
---

# CivicTheme JS/CSS Enhancement

Generate JS, CSS, and library files for a behaviour enhancement on existing CivicTheme markup.

Enhancements **extend** CivicTheme — they do not override it. Files ship as plain `.css` and `.js` (no `.scss`, no `npm run dist`) and declare their own library that loads alongside CivicTheme's.

## Required inputs

- `[THEME_MACHINE_NAME]` — sub-theme machine name
- Enhancement name (kebab-case)
- What markup is being targeted (classes, `data-` attributes, element types)
- Whether the enhancement should be site-wide or context-specific

## Core rules

- Enhancements have **no** `.component.yml`. Drupal's SDC system will not auto-load any assets.
- Both CSS and JS must be declared in a library — neither loads automatically.
- Use `data-` attribute selectors for JS targeting — not classes or IDs. This decouples JS from markup changes.
- Use `Drupal.behaviors` and `once()` for all JS. Never use `document.addEventListener('DOMContentLoaded', ...)`.
- If the enhancement targets CivicTheme CSS classes on native HTML elements (e.g. `ct-select` on a `<select>`), the component CSS will not auto-load. Include the base component CSS from `components_combined/` in the library.
- Always use `components_combined/[level]/[name]/[name].css` for base CivicTheme component CSS — never `../../contrib/civictheme/`.

## Decision logic

- Enhancement needed on every page → attach globally via `libraries:` in `[THEME_MACHINE_NAME].info.yml`
- Enhancement needed only on specific pages or paragraph types → attach conditionally via `$variables['#attached']['library'][]` in a preprocess hook; include the attachment code in `attachment_notes`
- Enhancement targets CivicTheme classes on native elements → add `components_combined/[level]/[name]/[name].css` to the library CSS
- Enhancement uses only custom CSS → reference `components/[level]/[name]/[name].css` in the library

## Reference files

Read before generating:

- `references/libraries-and-assets.md` — library declaration format, `components_combined/` rule, global vs conditional attachment, CSS weight and preprocessing options

## Output contract

```yaml
enhancement_name: <kebab-case-name>
files:
  - path: components/[level]/[enhancement-name]/[enhancement-name].css
    purpose: enhancement styles (plain CSS — no SCSS, no build step)
    contents: |
      <full file contents>
  - path: components/[level]/[enhancement-name]/[enhancement-name].js
    purpose: enhancement behaviour using Drupal.behaviors and once()
    contents: |
      <full file contents>
  - path: [THEME_MACHINE_NAME].libraries.yml
    purpose: library declaration — both CSS and JS required (no SDC auto-loading)
    contents: |
      <only the new or updated library entry — not the entire file>
attachment_notes:
  - <global: add [THEME_MACHINE_NAME]/[name] to libraries: in [THEME_MACHINE_NAME].info.yml>
  - <OR conditional: $variables['#attached']['library'][] = '[THEME_MACHINE_NAME]/[name]'; in preprocess hook — include the specific hook name>
```
