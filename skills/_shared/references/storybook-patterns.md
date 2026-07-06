# Storybook Patterns

Storybook is optional infrastructure in a CivicTheme sub-theme. Only include a `.stories.js` file when the user confirms Storybook is present. When it is, the story documents the component's `.component.yml` prop contract.

This repo targets **Storybook 10**. Do not emit SB8 patterns — they silently break. See the compatibility table at the bottom.

## File placement

Co-locate the story with the component, using the same base name as the directory:

```
components/02-molecules/my-card/
├── my-card.component.yml
├── my-card.twig
├── my-card.scss
└── my-card.stories.js
```

## Two story patterns

### Pattern A — Controls theme toggle

Use for **atoms and molecules** that have a `theme` prop. The `theme` argType radio passes `'light'` or `'dark'` into the Twig template, which applies `ct-theme-light` / `ct-theme-dark` to the root element. Background doesn't change automatically — reviewers toggle it manually.

```js
import MyCardTwig from './my-card.twig';

export default {
  title: 'Molecules/My Card',
  component: MyCardTwig,
  argTypes: {
    theme: {
      control: { type: 'radio' },
      options: ['light', 'dark'],
    },
    vertical_spacing: {
      control: { type: 'select' },
      options: ['top', 'bottom', 'both', 'none'],
    },
    with_background: {
      control: { type: 'boolean' },
    },
    title: { control: { type: 'text' } },
  },
};

export const Default = {
  args: {
    theme: 'light',
    vertical_spacing: 'none',
    with_background: false,
    title: 'Example card title',
  },
};
```

### Pattern B — Separate dark variant story

Use when:

- The component is an **organism or template** (Banner, Header, Footer, List, Page…) — visual weight makes a pre-configured dark view valuable alongside the light default.
- The component has **no Twig template** — the theme class is applied directly in HTML; there is no `theme` argType available.

**Pattern B for Twig-import organisms/templates** — keep the `theme` argType, and also export a `Dark` story with the SB10 `globals` key to pre-select the dark background:

```js
import MyBannerTwig from './my-banner.twig';

export default {
  title: 'Organisms/My Banner',
  component: MyBannerTwig,
  argTypes: {
    theme: {
      control: { type: 'radio' },
      options: ['light', 'dark'],
    },
    // other argTypes...
  },
};

export const Default = {
  args: {
    theme: 'light',
    // other args...
  },
};

export const Dark = {
  args: {
    ...Default.args,
    theme: 'dark',
  },
  globals: {
    backgrounds: { value: 'dark' },
  },
};
```

**Pattern B for CSS-class-only components** — no Twig import, no `theme` argType; apply the class directly in the `render` function:

```js
export default {
  title: 'Molecules/My Component',
  render: (args) => {
    const el = document.createElement('div');
    el.className = 'ct-theme-light my-component';
    el.innerHTML = `<!-- component HTML -->`;
    return el;
  },
};

export const Default = {
  args: { /* component-specific args */ },
};

export const Dark = {
  args: { ...Default.args },
  globals: {
    backgrounds: { value: 'dark' },
  },
  render: (args) => {
    const el = document.createElement('div');
    el.className = 'ct-theme-dark my-component';
    el.innerHTML = `<!-- component HTML -->`;
    return el;
  },
};
```

## Which pattern to use

```
if no Twig template (CSS-class-only):
  → Pattern B only
elif organism or template tier:
  → Pattern A (theme argType) + Pattern B (separate Dark export)
else:  # atom or molecule with Twig template
  → Pattern A only
```

The primary driver is whether a Twig template exists, not the component tier. A CSS-class-only atom gets Pattern B; an organism gets both patterns (B is additive, not a replacement for the Controls toggle).

The only CSS-only components in the upstream CivicTheme base are **Table Sort** and **Summary List** (both atoms). For the full component list and tier assignments, see `references/component-taxonomy.md`.

**CSS-only components need explicit asset imports in the SDC stories file.** The sdc-plugin auto-discovers per-component `.css` / `.js` via `Component from './x.twig'` includes; with no Twig template there is no include for it to walk. In the **SDC** `.stories.js`, import the atom's `.css` and `.js` explicitly at the top of the file so the sdc-plugin bundles them. The **twig-package** `.stories.js` must NOT have those imports – the twig Vite build would fail on them (the twig package uses a global `civictheme.storybook.css` bundle instead). Upstream CivicTheme has no sync-skip mechanism, so the next `components:update:twig` run copies the SDC stories.js over the twig copy and breaks the twig build until the imports are manually removed again.

**DTA-fork escape hatch.** If the fork has patched `components:update:twig` to honour an `@sync-ignore` marker (the DTA `civictheme-uikit` fork does – the script reads the first 2 KB of the destination file), add the marker to the twig `.stories.js` docblock so the sync preserves the drift instead of re-breaking it on every run:

```
 * @sync-ignore
 * This file intentionally drifts from the SDC source: the SDC version imports
 * per-component .css for sdc-plugin discovery; the twig build resolves styles
 * globally and has no such files.
```

Upstream CivicTheme has no such guard – do not rely on the marker in a component targeted at upstream. The same situation applies to any component that emits raw atom HTML (`<input class="ct-input">`) in place of `{% include 'civictheme:input' %}`. See "Sync exclusions" and "Asset discovery" in `civictheme-uikit-component-generator/references/toolchain.md`.

## Default export fields

- `title` – Storybook sidebar path. Mirror an existing peer's prefix rather than assuming the atomic tier (see "Story titles" below).
- `component` — the imported `.twig` file; the CivicTheme Storybook preset renders it. Omit for CSS-class-only components — use `render` instead.
- `argTypes` — one entry per prop declared in `.component.yml`. Keys must match prop names exactly.

## Args map to `.component.yml` props

Every key in `argTypes` (and in a story's `args`) must match a prop in the component's `.component.yml`. If a prop is added or renamed in YAML, the story must be updated to match — otherwise the control renders with no effect.

## `argTypes` for enum props

Enums in YAML become `radio` or `select` controls with explicit `options`:

```yaml
# my-card.component.yml (excerpt)
props:
  type: object
  properties:
    theme:
      type: string
      enum: [light, dark]
    size:
      type: string
      enum: [small, medium, large]
```

The `props:` key is a JSON Schema object — prop definitions live under `properties:`, not directly under `props:`. See `references/component-yml-patterns.md` for the full schema.

```js
argTypes: {
  theme: {
    control: { type: 'radio' },
    options: ['light', 'dark'],
  },
  size: {
    control: { type: 'select' },
    options: ['small', 'medium', 'large'],
  },
},
```

Use `radio` for 2–3 options; `select` for 4+.

## Story titles – mirror a peer, not the tier

The `title`'s top segment must match a group in the repo's `.storybook/preview.js` storySort `order`, or the story sorts through the trailing `*` and lands away from its siblings. Do not blind-assume the atomic tier: the CivicTheme UIKit titles content-display components by purpose – `Content/Tables/Filterable table`, `Content/Tables/Table sort`, `Content/Charts/Chart`, `Content/Summary list` – while structural components keep `Atoms/` … `Templates/`. Before titling a new story, grep a sibling component's `.stories.js` and mirror its prefix.

## Docs pages and `tags`

Per-component Docs pages come from `tags: ['autodocs']` on the preview default export, set in `.storybook/preview.js` in **both** `packages/sdc/` and `packages/twig/` (the twig config is tracked independently, not synced from SDC). `@storybook/html-vite` has no automatic docgen, so the Docs args table is built entirely from the hand-written `argTypes` – a story with no `argTypes` renders an empty table. That is the real reason every prop needs an explicit `argTypes` entry, not just a populated Controls panel.

- Opt one component out of Docs with `tags: ['!autodocs']` in its `meta`.
- Tag DGA-specific stories `tags: ['digitalgovau']` for the sidebar badge (wired in `manager.js`).

Editorial "when to use / anti-pattern" content that autodocs cannot generate belongs in an attached MDX page beside the stories, not in the `.stories.js`.

## Interaction (`play`) functions – wiring only

Do not add `userEvent` / `expect` demo `play` functions to showcase stories. They auto-run on every render (the default state is never seen), a real `<form method="get">` submit navigates the iframe off-story, and `aria-expanded` assertions coupled to `collapsible.js`'s `transitionend` (~500 ms) flake or hang in headless CI. A search-results attempt was reverted for exactly these reasons.

`play` is legitimate for one thing – **wiring** component JS to run on each story switch, e.g. `play: ({ canvasElement }) => window.DgaFilterableTable.initAll(canvasElement)`. On Storybook 10 import test utilities from bare `storybook/test`, not `@storybook/test`. Read `js-verification.md` before asserting any behaviour from a story.

## Fonts and vendored assets in the SDC Storybook

A SCSS swap to a self-hosted font renders in the twig Storybook but 404s in the **SDC** Storybook: `civictheme.base.css` bakes the Drupal asset path and the build only path-swaps assets in the twig flow. The body still looks right because the font falls back to a metric-identical system face, masking the failure. Re-emit the `@font-face` (via `ct-font-include()`) in `packages/sdc/components/style.stories.scss` – it is compiled with the Storybook `/assets/` path and already imported by SDC `preview.js` – while keeping `#{$ct-assets-directory}` in `variables.base.scss` so each build context fills its own path. Do not add a staticDir.

## SB10 compatibility — do not emit these SB8 patterns

| SB8 (broken in SB10) | SB10 (correct) |
|---|---|
| `parameters.backgrounds.values: [...]` | `parameters.backgrounds.options: { key: { name, value } }` |
| `parameters.backgrounds.default: 'Dark'` | `globals: { backgrounds: { value: 'dark' } }` at story level |
| `import { ... } from '@storybook/preview-api'` | `import { ... } from 'storybook/preview-api'` |

If you encounter upstream CivicTheme story files that use the SB8 column, rewrite them to the SB10 column before including them in a sub-theme.
