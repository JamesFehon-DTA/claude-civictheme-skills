---
name: civictheme-sdc-generator
description: Generate all files for a new CivicTheme-compatible SDC component inside a Drupal sub-theme. Use when the type-selector returns new_sdc_component, or when the user asks to create a new component, atom, molecule, or organism that doesn't exist in CivicTheme. Always use this skill before civictheme-paragraph-generator when a new component is also needed.
---

# CivicTheme SDC Generator

Generate all files for a new SDC component in a CivicTheme sub-theme.

## Required inputs

- `[THEME_MACHINE_NAME]` — sub-theme machine name
- Component name (kebab-case, no "civic" prefix)
- Atomic level: `atom` | `molecule` | `organism` | `template`
- Props needed (infer from user description; always add standard shared props unless explicitly excluded)
- Whether JS behaviour is needed

## Core rules

- CSS auto-loads when the component template is rendered via `{% include %}`. No library entry needed for CSS.
- JS never auto-loads. Attach via a library — globally in `.info.yml` or conditionally in a preprocess hook.
- Namespace: `[THEME_MACHINE_NAME]:[component-name]`
- Directory: `components/[01-atoms|02-molecules|03-organisms|04-templates]/[name]/`
- All files share the same base name as the directory.
- Storybook is optional — include `.stories.js` only if the user confirms Storybook is present. See `references/storybook-patterns.md` for the story file structure.

## Standard shared props

Always include unless explicitly excluded:

```yaml
theme:
  type: string
  enum: [light, dark]
vertical_spacing:
  type: string
  enum: [top, bottom, both, none]
with_background:
  type: boolean
attributes:
  type: Drupal\Core\Template\Attribute
modifier_class:
  type: string
```

## Decision logic

- JS requested → generate `.js` file + JS-only library entry (omit CSS from library — SDC auto-loads it)
- Storybook not confirmed → omit `.stories.js`; note it as optional
- Atomic level: standalone UI element with no children → atom; composition of atoms → molecule; complex section → organism

## Reference files

Read before generating:

- `references/component-yml-patterns.md` — full `.component.yml` schema, prop types, slots, SDC loading notes
- `references/twig-patterns.md` — prop validation, class construction, `only` keyword, ARIA patterns, data-attribute selectors
- `references/libraries-and-assets.md` — library declaration format, CSS vs JS loading, `components_combined/` rule
- `references/storybook-patterns.md` — story file structure, args/argTypes mapping from `.component.yml` (optional — only if Storybook is present)
- `references/civictheme-field-storage.md` — storage shape of every canonical `field_c_p_*` / `field_c_n_*`. Consult when a component is expected to back a specific CivicTheme field: declare the prop's `type` (`string` vs rich `object`/HTML-bearing) and whether it is single or array-shaped to match the storage. If the intended paragraph field is `string`/`string_long` and your prop expects HTML, either change the prop to plain text or require a custom sub-theme `text_long` field — the base storage will emit escaped markup otherwise.

## Output contract

```yaml
component_namespace: <[THEME_MACHINE_NAME]:[component-name]>
atomic_level: <atom | molecule | organism | template>
files:
  - path: components/[level]/[name]/[name].component.yml
    purpose: SDC registration and prop schema
    contents: |
      <full file contents>
  - path: components/[level]/[name]/[name].twig
    purpose: component template
    contents: |
      <full file contents>
  - path: components/[level]/[name]/[name].scss
    purpose: component styles
    contents: |
      <full file contents>
  - path: [THEME_MACHINE_NAME].libraries.yml  # only if JS requested
    purpose: JS-only library entry
    contents: |
      <only the new library entry — not the entire file>
  - path: components/[level]/[name]/[name].js  # only if JS requested
    purpose: component behaviour
    contents: |
      <full file contents>
post_generation_notes:
  - Run npm run dist to compile SCSS → CSS.
  - If JS exists, attach the library globally (info.yml libraries:) or conditionally ($variables['#attached'] in preprocess hook).
  - Drupal configuration must exist before testing: field.storage.*, field.field.*, core.entity_form_display.*, core.entity_view_display.*, paragraphs.paragraphs_type.*. Export from a working environment via `drush cex` or create manually in config/install.
  - If this component backs a paragraph type, paragraph configuration (see above) must also exist before the full stack can be tested.
```
