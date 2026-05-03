<!--
Paste the section below into the CLAUDE.md of a CivicTheme UIKit,
design system, or component library repository — i.e. a repo that contains
packages/sdc/ and packages/twig/ and authors components directly, rather
than consuming CivicTheme as a base theme.

Do not paste this file verbatim — copy only the "## CivicTheme UIKit
component authoring" section. Delete this comment block before committing.
-->

## CivicTheme UIKit component authoring

Authoring is SDC-first. The canonical toolchain flows SDC → twig via `components:update:sdc` and `components:update:twig`; there is no reverse path. Every new component must be scaffolded in both packages in one pass, with `packages/sdc/` as the source of truth.

**Use `civictheme-uikit-component-generator`** for all new atoms, molecules, organisms, and templates in this repo. Do not invoke `civictheme-sdc-generator` — that skill targets Drupal sub-themes and encodes different constraints (Drupal include namespaces, hook integration, `libraryOverrides`).

**After generation, run the toolchain sync before treating output as final:**

```sh
npm run components:update:sdc   # regenerate authoritative docblocks from .component.yml
npm run components:update:twig  # regenerate packages/twig/ from SDC source
npm run validate                # lint + schema + theme-variable checks
```

The generator's twig output is a bootstrap. `components:update:twig` overwrites it with namespace-transformed, docblock-correct content — this is intentional and is what makes the twig package a genuine derivative of SDC.

**Always dispatch the Skill tool — never substitute a Read of SKILL.md.** Reading the markdown produces the same prose but skips the SDC-vs-twig package routing and the project-context capture. If you find yourself reaching for the Read tool on a CivicTheme SKILL.md file, stop and dispatch the Skill instead. This applies even when the user explicitly names a downstream skill — UIKit work has three direct-entry skills (`civictheme-uikit-component-generator`, `civictheme-uikit-scss-iteration`, `civictheme-health-check`) and the right one is determined by intent, not by the user repeating a name in the prompt.

**No `.component.yml` in `packages/twig/`.** The twig docblock is the schema there, generated from the SDC `.component.yml` by `components:update:twig`. Writing a second schema in the twig package creates a divergence the moment either side is edited.
