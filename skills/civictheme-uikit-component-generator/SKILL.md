---
name: civictheme-uikit-component-generator
description: Generate all files for a new Drupal-agnostic component in the CivicTheme upstream UIKit, design system, design library, or component library — NOT a Drupal sub-theme. Use when the user wants to author a new atom, molecule, organism, or template component in the CivicTheme source. Triggers for "add a component to the UIKit", "create a new UIKit component", "new component in the design system", "scaffold a component in the twig package", "new atom/molecule/organism for CivicTheme", "add to the design system", or "new component in the design library".
---

# CivicTheme UIKit Component Generator

Generate Twig, SCSS, and optional `.component.yml` files for a new component in `packages/twig/components/`.

This skill targets the **UIKit authoring source** (`packages/twig/`) only. For Drupal sub-theme work, use `civictheme-sdc-generator` instead.

## Required inputs

- `[COMPONENT_NAME]` — kebab-case component name, e.g. `summary-list`
- `[ATOMIC_TIER]` — one of `01-atoms`, `02-molecules`, `03-organisms`, `04-templates`
- `[CIVICTHEME_VERSION]` — UIKit version; default `1.12.2` if unknown

## Reference files

Read before generating:

- `references/twig-patterns.md` — docblock format, allowlist validation, class composition, content guard, attributes pattern, include namespaces
- `references/scss-patterns.md` — design system mixins, component-theme pattern, geometry tokens, banned patterns
- `references/component-yml-patterns.md` — schema, enum values, standard props, keeping docblock in sync
- `references/toolchain.md` — post-generation commands, what not to run, Husky behaviour

## What to generate

Files at `packages/twig/components/[tier]/[name]/`:

| File | Condition |
|---|---|
| `[name].twig` | Always |
| `[name].scss` | Always |
| `[name].component.yml` | Always — it is the authoritative prop schema for the twig package |

Do NOT generate: Drupal preprocess hooks, `hook_page_attachments`, `*.libraries.yml`, `*.stories.js` or `*.stories.twig` (unless explicitly requested), anything in `packages/sdc/`.

## Out of scope

**Portable / self-contained components** — components with their own CSS token namespace (`--[prefix]-*`), hardcoded fallback values alongside CivicTheme token references, and multi-site portability as a design constraint. These intentionally bypass `ct-component-theme()`, `ct-typography()`, and the mixin system. They live in Drupal themes under their own SDC namespace, not in `packages/twig/`. Do not generate them with this skill.

Signals: `--dgag-*` / `--[prefix]-*` token declarations, `var(--ct-color-*, #fallback)` patterns, "portable across sites" language, a non-`civictheme:` SDC namespace.

## Post-generation

1. `npm run dist` — compile SCSS → CSS
2. `npm run validate` — validate `.component.yml` enum values and theme variables
3. `npm run dev:twig` — preview in Storybook
4. `npm run lint` — run before committing

See `references/toolchain.md` for full context and scripts that are NOT relevant to this workflow.

## Output contract

```yaml
component_path: packages/twig/components/[tier]/[name]/
files:
  - path: packages/twig/components/[tier]/[name]/[name].twig
    purpose: parameterised Twig template
    contents: |
      <full file contents>
  - path: packages/twig/components/[tier]/[name]/[name].scss
    purpose: component styles using design system mixins
    contents: |
      <full file contents>
  - path: packages/twig/components/[tier]/[name]/[name].component.yml  # only if warranted
    purpose: prop schema documentation
    contents: |
      <full file contents>
post_generation_notes:
  - Run node tools/scripts/validate-component-enums.js if .component.yml was generated.
  - Run npm run dist to compile SCSS.
```

