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
- Storybook story pattern (when Storybook is confirmed): organism/template → Pattern A + Pattern B (theme argType + separate `Dark` export with `globals: { backgrounds: { value: 'dark' } }`); atom/molecule → Pattern A only. SDC always has a Twig template, so the CSS-class-only branch in `references/storybook-patterns.md` does not apply here.

## Variables pipeline — scaffold after emitting SCSS

Every `ct-component-property($root, $theme, …args)` call in the generated component SCSS needs a matching SCSS-variable declaration pair (light + dark) in the sub-theme's `components/variables.components.scss`, otherwise the rendered component has no value to resolve against at runtime.

After generating the component SCSS:

1. Enumerate every `ct-component-property` call you just emitted.
2. Derive the variable base name from the call: `[component]-[theme]-[joined-path-segments]-[property]`. The component segment is `$root` with the leading `.ct-` stripped; all positional args after `$theme` join with hyphens; the last arg is the CSS property.
3. Scaffold a block in `components/variables.components.scss` with one declaration per call per theme, using `ct-color-light('token')` / `ct-color-dark('token')` as default values (pick a sensible token name — `typography`, `background-light`, `interactive`, etc. — and let the author refine). For non-colour properties use the appropriate CivicTheme token function (`ct-particle`, `ct-typography-size`, etc.) or a raw value.
4. Append the block to `components/variables.components.scss` if it exists; create the file if it does not. Do **not** add `!default` — sub-theme values must win.
5. Include the variables file in the output contract alongside the component files.

**Never write to `00-base/_variables.components.scss`** — that is upstream CivicTheme base content. The custom file is always `components/variables.components.scss` in the sub-theme.

See `references/variables-pipeline.md` for the full flow (`ct-component-property()` → `--ct-*` custom property → `components/variables.components.scss` → `style.css_variables.scss` export) and examples of how the call shape maps to variable names.

## Reference files

Read before generating:

- `references/component-yml-patterns.md` — full `.component.yml` schema, prop types, slots, SDC loading notes
- `references/twig-patterns.md` — prop validation, class construction, `only` keyword, ARIA patterns, data-attribute selectors
- `references/js-patterns.md` — constructor + root-level `querySelectorAll` init, `data-collapsible-collapsed` state attribute, collapsible panel `!important` pitfall (read when emitting JS behaviour)
- `references/libraries-and-assets.md` — library declaration format, CSS vs JS loading, `components_combined/` rule
- `references/component-taxonomy.md` — all CivicTheme components by tier; confirms that this is a new component not already present in the base theme
- `references/storybook-patterns.md` — story file structure, args/argTypes mapping from `.component.yml` (optional — only if Storybook is present)
- `references/variables-pipeline.md` — shared flow from `ct-component-property()` → `--ct-*` custom property → `components/variables.components.scss` → `style.css_variables.scss` export; read before scaffolding the variable block
- `references/civictheme-field-storage.md` — storage shape of every canonical `field_c_p_*` / `field_c_n_*`. Consult when a component is expected to back a specific CivicTheme field: declare the prop's `type` (`string` vs rich `object`/HTML-bearing) and whether it is single or array-shaped to match the storage. If the intended paragraph field is `string`/`string_long` and your prop expects HTML, either change the prop to plain text or require a custom sub-theme `text_long` field — the base storage will emit escaped markup otherwise.
- `references/accessibility.md` — repo-wide a11y rules enforced at generation: disabled links (no `disabled` on `<a>`), new-tab notices (append, don't replace accessible name), decorative icons (`aria-hidden="true"`). Read before emitting any interactive markup or ARIA attributes.

## Accessibility — enforced at generation

Emit these patterns inline when the component produces link-shaped controls, new-tab links, or decorative icons. Keep the inline comments in the generated `.twig` — they cite `references/accessibility.md` so downstream maintainers know which rule applies:

```twig
{# a11y #A: disabled link — aria-disabled + tabindex="-1" + omit href.
   Never emit `disabled` on <a>. See references/accessibility.md. #}
{% if is_disabled %}
  <a class="ct-[name]" aria-disabled="true" tabindex="-1">{{ label }}</a>
{% else %}
  <a class="ct-[name]" href="{{ url }}">{{ label }}</a>
{% endif %}

{# a11y #B: new-tab notice — append via visually-hidden span.
   Never replace the accessible name with aria-label="Opens in a new tab". #}
<a href="{{ url }}" target="_blank" rel="noopener noreferrer">
  {{ label }}<span class="ct-visually-hidden"> (opens in a new tab)</span>
</a>

{# a11y #C: decorative icon — aria-hidden on the wrapping span so AT does not double-announce. #}
<span class="ct-[name]__icon" aria-hidden="true">
  {% include 'civictheme:icon' with { symbol: icon_name, size: 'small' } only %}
</span>
```

Icon-only controls (no accompanying text) are *not* decorative — give the control a visually-hidden label and hide the icon. See rule #C in `references/accessibility.md`.

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
  # Do NOT write 00-base/_variables.components.scss — that path is upstream CivicTheme base content. The custom file is always components/variables.components.scss in the sub-theme.
  - path: components/variables.components.scss
    purpose: per-theme variable declarations matching every ct-component-property call in the component SCSS
    contents: |
      <appended block for this component — include surrounding file if creating from scratch, block only if appending>
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
