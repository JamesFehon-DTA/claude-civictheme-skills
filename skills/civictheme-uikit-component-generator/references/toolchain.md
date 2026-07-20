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
| `.stories.twig` | Not transformed by the sync, but the file **does** exist in both packages and is hand-maintained on the twig side (see note) |

Everything else — twig, JS, SCSS — is overwritten on every sync. Upstream CivicTheme ships no mechanism to preserve intentional SDC-vs-twig drift in non-excluded files; local divergence in those files is a known sharp edge of the one-way sync model. The typical trigger is a `.stories.js` that needs SDC-specific imports the twig package cannot accept — see "Asset discovery" below.

**`.stories.twig` are hand-maintained, not SDC-only.** Both packages carry the same story-twig fixtures (`colors`, `typography`, `data-vis`, …), but the sync skips them (this exclusion is upstream CivicTheme, not fork-local), so the twig copy is maintained by hand. Most are self-contained – no component `{% include %}` – so the SDC and twig copies are byte-identical and the exclusion costs nothing (`colors.stories.twig` diffs to nothing between packages). The one exception is a fixture that includes a component: `data-vis.stories.twig` pulls in `summary-list`, so its twig copy needs the `civictheme:` → `@tier/` namespace transform applied by hand – `{% include 'civictheme:summary-list' %}` in SDC becomes `{% include '@atoms/summary-list/summary-list.twig' %}` in twig. The sync will not do this for an excluded file, so after adding or editing a component-including `.stories.twig`, transform its twig copy by hand.

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

**DTA-fork escape hatch.** The DTA `civictheme-uikit` fork patches `components:update:twig` to honour an `@sync-ignore` marker in the first 2 KB of the destination file, which automates step 3 – add it to the twig `.stories.js` docblock and the sync preserves the drift instead of overwriting it:

```
 * @sync-ignore
 * Intentionally drifts from SDC: the SDC version imports per-component .css for
 * sdc-plugin discovery; the twig build resolves styles globally, no such files.
```

This is fork-local, not upstream CivicTheme – a component targeted at upstream must not assume it. Whenever the generator emits the SDC-side imports, flag step 3 (or the `@sync-ignore` marker on a fork that has it) as a required post-generation action.

## Fonts and vendored assets in the SDC Storybook

A SCSS swap to a self-hosted font renders in the twig Storybook but 404s in the **SDC** Storybook: `civictheme.base.css` bakes the Drupal asset path, and the build only path-swaps assets in the twig flow. The body still looks right because the font falls back to a metric-identical system face, masking the failure. Re-emit the `@font-face` (via `ct-font-include()`) in `packages/sdc/components/style.stories.scss` – it is compiled with the Storybook `/assets/` path and already imported by SDC `preview.js` – while keeping `#{$ct-assets-directory}` in `variables.base.scss` so each build context fills its own path. Do not add a staticDir.

---

## JS output — two bundles and the classic-script contract

The UIKit ships JS through **two separate build worlds**, and they have incompatible module formats. Confusing them is a live source of "every behaviour on the page is dead" bugs.

| World | Artifact | Format | Consumed as |
|---|---|---|---|
| Storybook / Vite (dev + preview) | `dist/civictheme.storybook.js` | **ESM** — carries top-level `export` statements (e.g. the chart code: `export const …`, `export function …`) | ES module, bundled by `@storybook/html-vite` |
| Runtime (Drupal / static-site consumers) | `dist/civictheme.base.js` (Drupal library `dist/scripts.drupal.base.js`) | **classic script** — no `import`/`export`, global scope | plain `<script>` tag, **not** `type="module"` |

Component JS is authored (and copied `components:update:twig`-verbatim) as **classic browser scripts** — `Drupal.behaviors` + `once()`, constructor + `querySelectorAll` sweep, globals on `window` (see `js-patterns.md`). The runtime bundle is loaded with a classic `<script>` — Drupal's library system and downstream consumers (e.g. an Astro `BaseLayout` loading `civictheme.base.js`) both omit `type="module"`.

**The failure mode.** A classic `<script>` cannot parse a top-level `export`. If ESM-authored source leaks an `export` into the bundle that ships to the classic-script world, the browser throws `SyntaxError: Unexpected token 'export'` and **aborts the entire bundle** — so *all* CivicTheme behaviours (navigation, collapsible, mobile menu tray, …) silently die, not just the offending module. The symptom looks like "the JS didn't load"; the cause is one stray `export` at the top of a concatenated classic bundle.

**Who has to fix it, and where.** The correct fix is upstream in the UIKit build: either down-level the ESM-authored source into a genuine classic (IIFE/UMD) bundle so no `export` survives, **or** commit fully to ESM and have every consumer load it `type="module"`. Until the build does one of those, consumers patch it downstream at sync time — the DTA `dga-dl` site's `scripts/sync-uikit.mjs` renames `civictheme.storybook.js` → `civictheme.base.js` and strips exports:

```js
const stripEsmExports = (code) => code.replace(/^export\s+/gm, '');
// FILES: ['civictheme.storybook.js', 'civictheme.base.js', stripEsmExports]
```

Treat that regex as a **band-aid, not the model**. When authoring or reviewing UIKit component JS, the invariant is: **no top-level `import`/`export` in any file that lands in the runtime bundle.** `.stories.js` are the sole exception — they live only in the Vite/Storybook world and are never concatenated into the classic runtime bundle (see `js-patterns.md` → "The runtime bundle must stay export-free").

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
