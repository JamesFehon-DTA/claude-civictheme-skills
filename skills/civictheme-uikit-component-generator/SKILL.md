---
name: civictheme-uikit-component-generator
description: Generate all files for a new Drupal-agnostic component in the CivicTheme upstream UIKit, design system, design library, or component library — NOT a Drupal sub-theme. SDC-first — scaffolds both packages/sdc/ (source of truth) and packages/twig/ (derivative bootstrap) in a single pass. Use when the user wants to author a new atom, molecule, organism, or template component in the CivicTheme source. Triggers for "add a component to the UIKit", "create a new UIKit component", "new component in the design system", "scaffold a component in the twig package", "new atom/molecule/organism for CivicTheme", "add to the design system", or "new component in the design library".
---

# CivicTheme UIKit Component Generator

Generate SDC source files and twig-package bootstrap files for a new component in a CivicTheme UIKit, design system, design library, or component library repo.

This skill targets the **UIKit authoring source** only. For Drupal sub-theme work, use `civictheme-sdc-generator` instead.

## Authoring model — SDC-first

CivicTheme UIKit authoring flows one direction: `packages/sdc/` → `packages/twig/`, via `npm run components:update:sdc` then `npm run components:update:twig`. There is no reverse script. Maintainers author in `packages/sdc/` as the source of truth; the twig package is a machine-generated derivative.

This generator scaffolds both packages in a single pass:

- **`packages/sdc/`** — canonical. `.component.yml` (with `$schema`), `.twig` using `civictheme:` include namespaces, `.scss`, and `.stories.js` when Storybook is wired up.
- **`packages/twig/`** — bootstrap. `.twig` using `@tier/` include namespaces, `.scss`. **No `.component.yml`** — the twig docblock is the schema in this package, regenerated from the SDC `.component.yml` by `components:update:sdc`.

The twig-package output is intentionally ephemeral. `components:update:twig` overwrites it with namespace-transformed, docblock-correct content derived from the SDC source. That overwrite is what keeps the twig package a genuine derivative of SDC.

## Required inputs

- `[COMPONENT_NAME]` — kebab-case component name, e.g. `summary-list`
- `[ATOMIC_TIER]` — one of `01-atoms`, `02-molecules`, `03-organisms`, `04-templates`
- `[CIVICTHEME_VERSION]` — UIKit version; default `1.12.2` if unknown
- Whether Storybook is present — include `.stories.js` in the SDC output only when confirmed

## Reference files

Read before generating:

- `references/twig-patterns.md` — docblock format, prop validation, class composition, content guard, SDC `civictheme:` vs twig-package `@tier/` namespacing
- `references/scss-patterns.md` — design system mixins, component-theme pattern, geometry tokens, banned patterns, contextual override scoping, `<fieldset>` and flex gotchas
- `references/js-patterns.md` — constructor + root-level `querySelectorAll` init, `data-collapsible-collapsed` state attribute, collapsible panel `!important` pitfall (read when emitting JS behaviour)
- `references/component-yml-patterns.md` — SDC `.component.yml` schema (including `$schema`), enum values, standard props, sync with the twig docblock
- `references/storybook-patterns.md` — story file structure for the SDC side; only include when Storybook is confirmed
- `references/toolchain.md` — canonical sync loop (`components:update:sdc` → `components:update:twig` → `validate`), Husky behaviour, `components:check` semantics
- `references/variables-pipeline.md` — shared flow from `ct-component-property()` → `--ct-*` custom property → `components/variables.components.scss` → `style.css_variables.scss` export; read before scaffolding the variable block

## What to generate

Two packages, one pass.

**SDC (source of truth) — `packages/sdc/components/[tier]/[name]/`:**

| File | Condition |
|---|---|
| `[name].component.yml` | Always — includes `$schema`; authoritative prop schema for the repo |
| `[name].twig` | Always — uses `civictheme:` include namespaces |
| `[name].scss` | Always |
| `[name].stories.js` | Only when Storybook is present |

**Twig package (derivative bootstrap) — `packages/twig/components/[tier]/[name]/`:**

| File | Condition |
|---|---|
| `[name].twig` | Always — uses `@tier/` include namespaces; overwritten by `components:update:twig` |
| `[name].scss` | Always |
| ~~`[name].component.yml`~~ | Never — the docblock is the schema in this package |

**Variables (shared) — `packages/sdc/components/variables.components.scss`:**

Append a per-component block declaring the SCSS variables for every `ct-component-property` call in the component SCSS. `components:update:twig` carries the file into the twig package; never write the twig-package copy directly.

Do NOT generate: Drupal preprocess hooks, `hook_page_attachments`, `*.libraries.yml`, `*.stories.twig`, or anything outside the two component directories above (and the shared variables file).

## Variables pipeline — scaffold after emitting SCSS

Every `ct-component-property($root, $theme, …args)` call in the generated component SCSS needs a matching SCSS-variable declaration pair (light + dark) in `packages/sdc/components/variables.components.scss`, otherwise the rendered component has no value to resolve against at runtime.

After generating the component SCSS:

1. Enumerate every `ct-component-property` call you just emitted.
2. Derive the variable base name from the call: `[component]-[theme]-[joined-path-segments]-[property]`. The component segment is `$root` with the leading `.ct-` stripped; all positional args after `$theme` join with hyphens; the last arg is the CSS property.
3. Scaffold a block with one declaration per call per theme, using `ct-color-light('token')` / `ct-color-dark('token')` as default values (pick a sensible token name — `typography`, `background-light`, `interactive`, etc. — and let the author refine). For non-colour properties use the appropriate CivicTheme token function (`ct-particle`, `ct-typography-size`, etc.) or a raw value.
4. Append the block to `packages/sdc/components/variables.components.scss`. Match the surrounding convention for `!default` (upstream base declarations use it; custom additions in the same file typically follow the same convention so sub-themes can still override).
5. Include the variables file in the output contract alongside the component files.

**Never write to `00-base/_variables.components.scss`** — that is upstream CivicTheme base content. The custom/authoring file is always `components/variables.components.scss` (in `packages/sdc/`). `components:update:twig` syncs it into the twig package; do not write the twig-package copy directly.

See `references/variables-pipeline.md` for the full flow (`ct-component-property()` → `--ct-*` custom property → `components/variables.components.scss` → `style.css_variables.scss` export) and examples of how the call shape maps to variable names.

## Out of scope

**Portable / self-contained components** — components with their own CSS token namespace (`--[prefix]-*`), hardcoded fallback values alongside CivicTheme token references, and multi-site portability as a design constraint. These intentionally bypass `ct-component-theme()`, `ct-typography()`, and the mixin system. They live in Drupal themes under their own SDC namespace, not in `packages/sdc/` or `packages/twig/`. Do not generate them with this skill.

Signals: `--dgag-*` / `--[prefix]-*` token declarations, `var(--ct-color-*, #fallback)` patterns, "portable across sites" language, a non-`civictheme:` SDC namespace.

## Post-generation

Run from the UIKit repo root, in this order:

1. `npm run components:update:sdc` — regenerate authoritative SDC twig docblocks from `.component.yml`
2. `npm run components:update:twig` — regenerate `packages/twig/` from SDC source (overwrites the bootstrap twig-package files)
3. `npm run validate` — schema, enum, and theme-variable checks; only meaningful after the two sync steps have run
4. `npm run dist` — compile SCSS → CSS
5. `npm run dev:twig` — preview in Storybook
6. `npm run lint` — run before committing

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
    purpose: SDC Twig template — civictheme: include namespaces
    contents: |
      <full file contents>
  - path: packages/sdc/components/[tier]/[name]/[name].scss
    purpose: SDC component styles
    contents: |
      <full file contents>
  - path: packages/sdc/components/[tier]/[name]/[name].stories.js  # only if Storybook confirmed
    purpose: SDC Storybook story
    contents: |
      <full file contents>
  - path: packages/twig/components/[tier]/[name]/[name].twig
    purpose: twig-package bootstrap — @tier/ include namespaces; overwritten by components:update:twig
    contents: |
      <full file contents>
  - path: packages/twig/components/[tier]/[name]/[name].scss
    purpose: twig-package styles (content matches the SDC file)
    contents: |
      <full file contents>
  # Do NOT also write packages/twig/components/variables.components.scss — the twig package is a generated derivative of SDC, and components:update:twig will overwrite any hand-written copy.
  - path: packages/sdc/components/variables.components.scss
    purpose: per-theme variable declarations matching every ct-component-property call in the component SCSS; synced into packages/twig/ by components:update:twig
    contents: |
      <appended block for this component — include surrounding file if creating from scratch, block only if appending>
post_generation_notes:
  - Run npm run components:update:sdc to regenerate authoritative SDC twig docblocks from .component.yml.
  - Run npm run components:update:twig to regenerate packages/twig/ from the SDC source — this overwrites the bootstrap twig-package files, and is intentional.
  - Run npm run validate to check schema, enum, and theme-variable correctness — only meaningful after both sync steps.
  - Run npm run dist to compile SCSS → CSS, then npm run dev:twig to preview in Storybook.
  - Run npm run lint before committing.
```
