---
name: civictheme-uikit-component-generator
description: Generate or extend a Drupal-agnostic component in the CivicTheme upstream UIKit, design system, design library, or component library – identified by `packages/sdc/`, NOT a Drupal sub-theme. SDC-first – scaffolds both packages/sdc/ (source of truth) and packages/twig/ (derivative bootstrap) in a single pass. Use when the user wants to author a new atom/molecule/organism/template in the CivicTheme source, OR port/migrate/copy a component in from another repo, OR add a new variant/type/option to an existing component (a new enum value, twig branch, draw routine, SCSS, story). Triggers for "add a component to the UIKit", "create a new UIKit component", "pull/port/migrate/copy the [component] into packages/sdc from another repo", "add a new [variant/type] to the [component]", "new atom/molecule/organism for CivicTheme", "scaffold a component in the twig package", or "add to the design system". Porting an existing component in counts as authoring – classify before copying, not after.
---

# CivicTheme UIKit Component Generator

Generate SDC source files and twig-package bootstrap files for a new component in a CivicTheme UIKit, design system, design library, or component library repo.

This skill targets the **UIKit authoring source** only. For Drupal sub-theme work, use `civictheme-sdc-generator` instead.

## Authoring model – SDC-first

CivicTheme UIKit authoring flows one direction: `packages/sdc/` → `packages/twig/`, via `npm run components:update:sdc` then `npm run components:update:twig`. There is no reverse script. Maintainers author in `packages/sdc/` as the source of truth; the twig package is a machine-generated derivative.

This generator scaffolds both packages in a single pass:

- **`packages/sdc/`** – canonical. `.component.yml` (with `$schema`), `.twig` using `civictheme:` include namespaces, `.scss`, and `.stories.js` when Storybook is wired up.
- **`packages/twig/`** – bootstrap. `.twig` using `@tier/` include namespaces, `.scss`. **No `.component.yml`** – the twig docblock is the schema in this package, regenerated from the SDC `.component.yml` by `components:update:sdc`.

The twig-package output is intentionally ephemeral. `components:update:twig` overwrites it with namespace-transformed, docblock-correct content derived from the SDC source. That overwrite is what keeps the twig package a genuine derivative of SDC.

## Porting and extending – both are authoring, run them through this skill

**Porting / migrating / copying a component in from another repo.** Do not drop the donor files into `packages/sdc/` verbatim. Treat the donor as a spec: read its markup/SCSS/JS/stories, then regenerate against this skill's output contract so the result obeys the UIKit's stricter rules – `civictheme:` include namespaces, the variables pipeline, the reserved-`attributes` rule below, the a11y patterns, and the two-package layout. The donor's `.component.yml` props and enums carry over; its hand-written conventions do not. After generating, run the post-generation sync loop so `packages/twig/` is a true derivative.

**Extending an existing component (new variant / type / option).** Adding a new enum value, twig branch, draw routine, SCSS, or story to a component that already exists in `packages/sdc/` is authoring, not SCSS iteration. Edit in place:

1. Add the new value to the relevant enum in `[name].component.yml` (e.g. a new `type` option).
2. Add the matching allowlist/branch entry in `[name].twig` (and the SDC `civictheme:` form first; the twig package is regenerated).
3. Add the behaviour (new JS routine, SCSS block) and a Storybook story exercising the new value.
4. Run the post-generation sync loop and `validate` – a new enum value with no twig/SCSS handling fails `validate-component-enums`.

Pure appearance tweaks to an *existing* variant, with no schema/markup/JS change, belong to `civictheme-uikit-scss-iteration` instead.

## Reserved props – never declare `attributes`

`attributes` is the reserved `Drupal\Core\Template\Attribute` object. SDC injects it automatically at render; declaring it under `props` (e.g. `attributes: { type: string }`) **fails Drupal/CivicTheme SDC validation**. No CivicTheme component declares it.

- **Do not** add `attributes` to the `.component.yml` `props`.
- **Do** render it on the root element with the guard (see `alert.twig`):

  ```twig
  <div class="ct-[name]"{% if attributes is defined and attributes is not null %} {{- attributes -}}{% endif %}>
  ```

`civictheme-health-check` fails any `*.component.yml` that declares `attributes` under `props`; keep the schema clean at generation so it never reaches that check.

## Required inputs

- `[COMPONENT_NAME]` – kebab-case component name, e.g. `summary-list`
- `[ATOMIC_TIER]` – one of `01-atoms`, `02-molecules`, `03-organisms`, `04-templates`
- `[CIVICTHEME_VERSION]` – UIKit version; default `1.12.2` if unknown
- Whether Storybook is present – include `.stories.js` in the SDC output only when confirmed

## Reference files

Read before generating:

- `references/twig-patterns.md` – docblock format, prop validation, class composition, content guard, SDC `civictheme:` vs twig-package `@tier/` namespacing
- `references/scss-patterns.md` – design system mixins, component-theme pattern, geometry tokens, banned patterns, contextual override scoping, `<fieldset>` and flex gotchas
- `references/js-patterns.md` – constructor + root-level `querySelectorAll` init, `data-collapsible-collapsed` state attribute, collapsible panel `!important` pitfall (read when emitting JS behaviour)
- `references/component-yml-patterns.md` – SDC `.component.yml` schema (including `$schema`), enum values, standard props, sync with the twig docblock
- `references/storybook-patterns.md` – story file structure for the SDC side; only include when Storybook is confirmed
- `references/toolchain.md` – canonical sync loop (`components:update:sdc` → `components:update:twig` → `validate`), Husky behaviour, `components:check` semantics, sync exclusions, asset discovery for pure-CSS atoms and raw-HTML components
- `references/variables-pipeline.md` – shared flow from `ct-component-property()` → `--ct-*` custom property → `components/variables.components.scss` → `style.css_variables.scss` export; read before scaffolding the variable block
- `references/accessibility.md` – repo-wide a11y rules enforced at generation: disabled links (no `disabled` on `<a>`), new-tab notices (append, don't replace accessible name), decorative icons (`aria-hidden="true"`). Read before emitting any interactive markup or ARIA attributes in either package.

## Accessibility – enforced at generation

Emit these patterns in the SDC `.twig` (source of truth); `components:update:twig` carries them into the twig package unchanged. Keep the inline comments so maintainers can trace each rule back to `references/accessibility.md`:

```twig
{# a11y #A: disabled link – aria-disabled + tabindex="-1" + omit href.
   Never emit `disabled` on <a>. See references/accessibility.md. #}
{% if is_disabled %}
  <a class="ct-[name]" aria-disabled="true" tabindex="-1">{{ label }}</a>
{% else %}
  <a class="ct-[name]" href="{{ url }}">{{ label }}</a>
{% endif %}

{# a11y #B: new-tab notice – append via visually-hidden span.
   Never replace the accessible name with aria-label="Opens in a new tab". #}
<a href="{{ url }}" target="_blank" rel="noopener noreferrer">
  {{ label }}<span class="ct-visually-hidden"> (opens in a new tab)</span>
</a>

{# a11y #C: decorative icon – aria-hidden on the wrapping span so AT does not double-announce. #}
<span class="ct-[name]__icon" aria-hidden="true">
  {% include 'civictheme:icon' with { symbol: icon_name, size: 'small' } only %}
</span>
```

SCSS that styles a disabled-link state should key on `[aria-disabled="true"]`, not `:disabled` – `<a>` never matches `:disabled`. See rule #A in `references/accessibility.md`.

## What to generate

Two packages, one pass.

**SDC (source of truth) – `packages/sdc/components/[tier]/[name]/`:**

| File | Condition |
|---|---|
| `[name].component.yml` | Always – includes `$schema`; authoritative prop schema for the repo |
| `[name].twig` | Always – uses `civictheme:` include namespaces |
| `[name].scss` | Always |
| `[name].stories.js` | Only when Storybook is present |

**Twig package (derivative bootstrap) – `packages/twig/components/[tier]/[name]/`:**

| File | Condition |
|---|---|
| `[name].twig` | Always – uses `@tier/` include namespaces; overwritten by `components:update:twig` |
| `[name].scss` | Always |
| ~~`[name].component.yml`~~ | Never – the docblock is the schema in this package |

**Variables (shared) – `packages/sdc/components/variables.components.scss`:**

Append a per-component block declaring the SCSS variables for every `ct-component-property` call in the component SCSS. `components:update:twig` carries the file into the twig package; never write the twig-package copy directly.

Do NOT generate: Drupal preprocess hooks, `hook_page_attachments`, `*.libraries.yml`, `*.stories.twig`, or anything outside the two component directories above (and the shared variables file).

## Variables pipeline – scaffold after emitting SCSS

Every `ct-component-property($root, $theme, …args)` call in the generated component SCSS needs a matching SCSS-variable declaration pair (light + dark) in `packages/sdc/components/variables.components.scss`, otherwise the rendered component has no value to resolve against at runtime.

After generating the component SCSS:

1. Enumerate every `ct-component-property` call you just emitted.
2. Derive the variable base name from the call: `[component]-[theme]-[joined-path-segments]-[property]`. The component segment is `$root` with the leading `.ct-` stripped; all positional args after `$theme` join with hyphens; the last arg is the CSS property.
3. Scaffold a block with one declaration per call per theme, using `ct-color-light('token')` / `ct-color-dark('token')` as default values (pick a sensible token name – `typography`, `background-light`, `interactive`, etc. – and let the author refine). For non-colour properties use the appropriate CivicTheme token function (`ct-particle`, `ct-typography-size`, etc.) or a raw value.
4. Append the block to `packages/sdc/components/variables.components.scss`. Match the surrounding convention for `!default` (upstream base declarations use it; custom additions in the same file typically follow the same convention so sub-themes can still override).
5. Include the variables file in the output contract alongside the component files.

**Never write to `00-base/_variables.components.scss`** – that is upstream CivicTheme base content. The custom/authoring file is always `components/variables.components.scss` (in `packages/sdc/`). `components:update:twig` syncs it into the twig package; do not write the twig-package copy directly.

See `references/variables-pipeline.md` for the full flow (`ct-component-property()` → `--ct-*` custom property → `components/variables.components.scss` → `style.css_variables.scss` export) and examples of how the call shape maps to variable names.

## Asset discovery – explicit SDC imports and a post-sync manual step

The SDC Storybook build auto-discovers per-component `.css` / `.js` via `Component from './x.twig'` includes. Two cases defeat that walk; both produce a component whose atom styles appear broken at runtime even though the SCSS compiles cleanly:

1. **Component has no Twig template** – e.g. a pure-CSS / JS atom like Table Sort or Summary List. The story uses a Pattern B `render` function (see `_shared/references/storybook-patterns.md`); there is no `.twig` import to trigger discovery of the component's own assets.
2. **Component emits raw atom HTML** – e.g. a molecule that writes `<input class="ct-input">` directly instead of `{% include 'civictheme:input' %}`. The atom's `.twig` is never pulled into the build graph, so its `.css` / `.js` never load.

When scaffolding a component in either category:

- **SDC `[name].stories.js`** – emit explicit imports at the top of the file for every atom the component depends on:
  ```js
  import './[name].css';             // for case 1 – the component's own assets
  import './[name].js';              // for case 1 – if JS behaviour exists
  import '../../01-atoms/input/input.css';  // for case 2 – each raw-HTML atom
  import '../../01-atoms/select/select.css';
  ```
- **twig-package `[name].stories.js`** – emit the file **without** those imports. The twig package loads all component styles via its global `civictheme.storybook.css` bundle; per-component `.css` imports would resolve to nothing and fail the Vite build.

**Flag the upstream limitation in the output.** CivicTheme ships no sync-skip mechanism for `.stories.js` drift, so the next `components:update:twig` run will copy the SDC version – imports and all – over the twig copy and break the twig Vite build until the imports are manually removed again. Call this out in the output contract's `post_generation_notes` so the user knows to either avoid running the sync after editing these files, or restore the twig-side stories.js by hand after each sync. Do not emit fork-specific skip-marker headers; those depend on patched sync scripts that are not part of upstream CivicTheme.

See `references/toolchain.md` – "Sync exclusions" and "Asset discovery" – for the full sync behaviour and exclusion list.

If Storybook is not present and no `.stories.js` is being emitted, neither addition applies – asset discovery is a story-file concern.

## Out of scope

**Portable / self-contained components** – components with their own CSS token namespace (`--[prefix]-*`), hardcoded fallback values alongside CivicTheme token references, and multi-site portability as a design constraint. These intentionally bypass `ct-component-theme()`, `ct-typography()`, and the mixin system. They live in Drupal themes under their own SDC namespace, not in `packages/sdc/` or `packages/twig/`. Do not generate them with this skill.

Signals: `--dgag-*` / `--[prefix]-*` token declarations, `var(--ct-color-*, #fallback)` patterns, "portable across sites" language, a non-`civictheme:` SDC namespace.

## Post-generation

Run from the UIKit repo root, in this order:

1. `npm run components:update:sdc` – regenerate authoritative SDC twig docblocks from `.component.yml`
2. `npm run components:update:twig` – regenerate `packages/twig/` from SDC source (overwrites the bootstrap twig-package files)
3. `npm run validate` – schema, enum, and theme-variable checks; only meaningful after the two sync steps have run
4. `npm run dist` – compile SCSS → CSS
5. `npm run dev:twig` – preview in Storybook
6. `npm run lint` – run before committing

Step order matters. Running `validate` before the sync steps reports spurious failures because the twig package still holds pre-sync bootstrap content. See `references/toolchain.md` for the full toolchain and Husky behaviour.

## Output contract

```yaml
component_path_sdc: packages/sdc/components/[tier]/[name]/
component_path_twig: packages/twig/components/[tier]/[name]/
files:
  - path: packages/sdc/components/[tier]/[name]/[name].component.yml
    purpose: SDC registration and authoritative prop schema (includes $schema)
    contents: |
      <full file contents>
  - path: packages/sdc/components/[tier]/[name]/[name].twig
    purpose: SDC Twig template – civictheme: include namespaces
    contents: |
      <full file contents>
  - path: packages/sdc/components/[tier]/[name]/[name].scss
    purpose: SDC component styles
    contents: |
      <full file contents>
  - path: packages/sdc/components/[tier]/[name]/[name].stories.js  # only if Storybook confirmed
    purpose: SDC Storybook story – include explicit atom .css/.js imports when the component has no Twig template or emits raw atom HTML (see "Asset discovery")
    contents: |
      <full file contents>
  - path: packages/twig/components/[tier]/[name]/[name].twig
    purpose: twig-package bootstrap – @tier/ include namespaces; overwritten by components:update:twig
    contents: |
      <full file contents>
  - path: packages/twig/components/[tier]/[name]/[name].scss
    purpose: twig-package styles (content matches the SDC file)
    contents: |
      <full file contents>
  - path: packages/twig/components/[tier]/[name]/[name].stories.js  # only when the SDC stories.js carries imports that would break the twig Vite build; otherwise omit and let components:update:twig produce it
    purpose: twig-package story emitted WITHOUT the per-component .css/.js imports (twig uses the civictheme.storybook.css bundle instead). IMPORTANT – upstream has no sync-skip mechanism, so components:update:twig will overwrite this file with the SDC version; the user must manually remove the imports again after every sync (see post_generation_notes)
    contents: |
      <full file contents>
  # Do NOT also write packages/twig/components/variables.components.scss – the twig package is a generated derivative of SDC, and components:update:twig will overwrite any hand-written copy.
  - path: packages/sdc/components/variables.components.scss
    purpose: per-theme variable declarations matching every ct-component-property call in the component SCSS; synced into packages/twig/ by components:update:twig
    contents: |
      <appended block for this component – include surrounding file if creating from scratch, block only if appending>
post_generation_notes:
  - Run npm run components:update:sdc to regenerate authoritative SDC twig docblocks from .component.yml.
  - Run npm run components:update:twig to regenerate packages/twig/ from the SDC source – this overwrites the bootstrap twig-package files, and is intentional.
  - Run npm run validate to check schema, enum, and theme-variable correctness – only meaningful after both sync steps.
  - Run npm run dist to compile SCSS → CSS, then npm run dev:twig to preview in Storybook.
  - Run npm run lint before committing.
  # Emit only when asset-discovery applied (the component has no Twig template, or emits raw atom HTML):
  - ASSET DISCOVERY – manual step required after every sync. components:update:twig will overwrite the twig-package stories.js with the SDC version, re-introducing the per-component .css/.js imports that break the twig Vite build. After each sync, remove those imports from packages/twig/components/[tier]/[name]/[name].stories.js by hand. This is an upstream limitation of the one-way sync model; see references/toolchain.md "Asset discovery".
```
