# UIKit Toolchain Reference

Source: `package.json` and `README.md` in the UIKit repo root.

---

## Canonical sync loop

Run from the UIKit repo root, in this order, after generating a new component:

| # | Command | Purpose |
|---|---|---|
| 1 | `npm run components:update:sdc` | Regenerate authoritative SDC twig docblocks from `.component.yml` |
| 2 | `npm run components:update:twig` | Regenerate `packages/twig/` from SDC source (namespace transform + docblock copy) |
| 3 | `npm run validate` | Validate `.component.yml` enum values and theme variables |
| 4 | `npm run dist` | Compile SCSS → CSS across all workspaces |
| 5 | `npm run dev:twig` | Start Storybook dev server for the twig package |
| 6 | `npm run lint` | Lint all workspaces — run before committing |

Step order matters. `validate` depends on the twig package reflecting the current SDC source, so running it before the two sync steps reports spurious failures. `npm run components:update` runs steps 1 and 2 together if you prefer a single command.

`npm run validate` covers both `validate-component-enums.js` and `validate-theme-variables.js`. Use it rather than calling either script directly.

---

## Sync direction — SDC is canonical

`packages/sdc/` → `packages/twig/` is the only supported direction. There is no reverse script. Edits that land only in `packages/twig/` are overwritten by the next `components:update:twig` run.

| Command | What it does |
|---|---|
| `npm run components:update:sdc` | Regenerates SDC `.twig` docblock headers from `.component.yml` |
| `npm run components:update:twig` | Copies SDC twig/scss/stories into `packages/twig/`, transforms `civictheme:` includes into `@tier/` path-based includes, and drops the `.component.yml` (twig-package docblock is the schema there) |
| `npm run components:update` | Runs both of the above |
| `npm run components:check` | Fails if `packages/twig/` does not match what `components:update:twig` would produce from current SDC source |

---

## Pre-commit hooks (Husky)

Husky runs quality checks before each commit: lint, tests, and `components:check`. Because `components:check` asserts that `packages/twig/` is a byte-accurate derivative of `packages/sdc/`, commits must happen **after** `components:update:twig` has run against the current SDC source. Committing a freshly generated component without running the sync loop first will fail the pre-commit hook.

To bypass hooks in exceptional circumstances only:

```bash
HUSKY=0 git push
```

Do not use this to ship out-of-sync component pairs — it just defers the failure to CI.

---

## Authoring workflow (this skill)

This skill targets SDC-first authoring. Every new component is scaffolded in both `packages/sdc/components/[tier]/[name]/` and `packages/twig/components/[tier]/[name]/` in one pass, with the SDC side as the source of truth. The twig-package output is a bootstrap — `components:update:twig` overwrites it with namespace-transformed, docblock-correct content derived from the SDC source.

The generator's job is to produce a starting pair that survives the first `components:update` run with minimal diff. To do that, the emitted SDC twig docblock must already match the `.component.yml`, the SDC twig must already use `civictheme:` namespaces, and the twig-package twig must already use `@tier/` namespaces for the same includes.
