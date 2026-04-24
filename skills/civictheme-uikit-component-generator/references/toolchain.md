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

## Sync exclusions

`components:update:twig` copies SDC twig, JS, and SCSS **verbatim** into `packages/twig/`. Three file types are excluded wholesale:

| Excluded pattern | Reason |
|---|---|
| `.component.yml` | The twig-package docblock is the schema in that package; a second YAML would diverge on first edit |
| `.css` | The twig package has no per-component CSS — all styles compile into the `civictheme.storybook.css` bundle |
| `.stories.twig` | Story fixtures are SDC-side only; the twig package uses `.stories.js` render functions |

Everything else — twig, JS, SCSS — is overwritten on every sync. Upstream CivicTheme ships no mechanism to preserve intentional SDC-vs-twig drift in non-excluded files; local divergence in those files is a known sharp edge of the one-way sync model. The typical trigger is a `.stories.js` that needs SDC-specific imports the twig package cannot accept — see "Asset discovery" below.

---

## Asset discovery — pure-CSS atoms and raw-HTML components

The SDC-side Storybook build relies on the sdc-plugin to auto-discover each component's `.css` and `.js` alongside its `.twig`. The plugin walks `Component from './x.twig'` imports — whatever it finds a Twig file for, it bundles the adjacent assets for. Two situations defeat that walk:

**1. Component has no Twig template.** Pure-CSS-and-JS atoms (e.g. Table Sort, Summary List) live as `.css`/`.js` pairs with no `.twig` to import. Their stories use Pattern B's `render` function to build DOM by hand (see `_shared/references/storybook-patterns.md`). Nothing triggers the sdc-plugin walk, so the atom's own `.css` and `.js` are not bundled.

**2. Component emits raw atom HTML instead of a `civictheme:` include.** A molecule or organism that writes `<input class="ct-input">` or `<select class="ct-select">` directly — rather than `{% include 'civictheme:input' %}` / `{% include 'civictheme:select' %}` — doesn't pull the atom's Twig file into the build graph. The markup renders, but the atom's `.css` / `.js` never load, so the atom looks unstyled inside the parent component.

**The mitigation is asymmetric between packages.** In the SDC `.stories.js`, import the needed atom assets explicitly:

```js
import './table-sort.css';
import './table-sort.js';
import '../../01-atoms/input/input.css';
```

These imports belong **only** in the SDC copy. The twig-package `.stories.js` must omit them — the twig package loads all component styles via its global `civictheme.storybook.css` bundle, and per-component `.css` imports resolve to nothing and fail the twig-side Vite build.

This is the upstream sharp edge. Upstream CivicTheme has no sync-skip mechanism, so the next `components:update:twig` run copies the SDC version — imports and all — over the twig copy, and the twig build breaks until the imports are manually removed again. The workflow today:

1. Edit SDC `.stories.js` with the explicit imports.
2. Hand-maintain the twig `.stories.js` without them.
3. After every `components:update:twig` run, remove the imports from the twig copy again.

Forks of the UIKit sometimes patch the sync script to honour a skip marker, which automates step 3; that is not part of upstream CivicTheme and should not be assumed by skill-scaffolded components. Flag step 3 as a required post-generation action whenever the generator emits the SDC-side imports.

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

---

## SDC maintainer sync loop — `dist:sdc` → `components:update` → `dist:twig`

When editing an existing component's SCSS or twig (not scaffolding a new one), use the dist-scoped loop rather than the full top-level sync. This is the day-to-day iteration path — faster than the full `components:update:sdc` → `components:update:twig` → `validate` cycle and safe for incremental edits:

| # | Command | Purpose |
|---|---|---|
| 1 | `npm run dist:sdc` | Compile SCSS → CSS for the SDC workspace only |
| 2 | `npm run components:update` | Regenerate SDC docblocks and copy SDC → twig package (runs `components:update:sdc` then `components:update:twig`) |
| 3 | `npm run dist:twig` | Compile SCSS → CSS for the twig workspace only, producing the files Storybook serves |

Treat this as a first-class workflow, not a shortcut. The full sync loop earlier in this doc is the pre-commit contract; this loop is what you run while iterating on a component. Storybook's HMR does not always pick up SCSS changes in other packages, so `dist:twig` is what actually refreshes the styles the dev server serves.

---

## Storybook viewport presets — avoid the "desktop" preset for breakpoint checks

Storybook's built-in "desktop" viewport preset can resolve to a pixel width below the `l` breakpoint (≥1200px in CivicTheme), depending on the Storybook version and addon-viewport defaults. That means stories previewed under the "desktop" preset may render in the `m` breakpoint range despite the label, masking desktop-only layout bugs.

When verifying breakpoint behaviour, set explicit pixel widths rather than trusting the preset name:

- For `l` breakpoint verification: set the viewport width to 1200px or wider.
- For `xl` verification: 1440px or wider.
- Prefer the addon-viewport's custom width controls, or resize the browser window, over selecting the "desktop" preset.

Document the explicit width used when reporting a visual check ("verified at 1280px") — a bare "looks fine on desktop" does not identify which breakpoint range was actually tested.
