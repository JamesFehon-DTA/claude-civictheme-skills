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

**CSS-only components need explicit asset imports in the SDC stories file.** The sdc-plugin auto-discovers per-component `.css` / `.js` via `Component from './x.twig'` includes; with no Twig template there is no include for it to walk. In the **SDC** `.stories.js`, import the atom's `.css` and `.js` explicitly at the top of the file so the sdc-plugin bundles them. The **twig-package** `.stories.js` must NOT have those imports — the twig Vite build would fail on them (the twig package uses a global `civictheme.storybook.css` bundle instead). Upstream CivicTheme has no sync-skip mechanism, so the next `components:update:twig` run copies the SDC stories.js over the twig copy and breaks the twig build until the imports are manually removed again. The same situation applies to any component that emits raw atom HTML (`<input class="ct-input">`) in place of `{% include 'civictheme:input' %}`. See "Sync exclusions" and "Asset discovery" in `civictheme-uikit-component-generator/references/toolchain.md`.

## Default export fields

- `title` — Storybook sidebar path (`Atoms/...`, `Molecules/...`, `Organisms/...`).
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

## SB10 compatibility — do not emit these SB8 patterns

| SB8 (broken in SB10) | SB10 (correct) |
|---|---|
| `parameters.backgrounds.values: [...]` | `parameters.backgrounds.options: { key: { name, value } }` |
| `parameters.backgrounds.default: 'Dark'` | `globals: { backgrounds: { value: 'dark' } }` at story level |
| `import { ... } from '@storybook/preview-api'` | `import { ... } from 'storybook/preview-api'` |

If you encounter upstream CivicTheme story files that use the SB8 column, rewrite them to the SB10 column before including them in a sub-theme.
