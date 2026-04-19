# Storybook Patterns

Storybook is optional infrastructure in a CivicTheme sub-theme. Only include a `.stories.js` file when the user confirms Storybook is present. When it is, the story documents the component's `.component.yml` prop contract.

## File placement

Co-locate the story with the component, using the same base name as the directory:

```
components/02-molecules/my-card/
├── my-card.component.yml
├── my-card.twig
├── my-card.scss
└── my-card.stories.js
```

## Default export structure

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
```

- `title` — the Storybook sidebar path (`Atoms/...`, `Molecules/...`, `Organisms/...`).
- `component` — the imported `.twig` file; the Storybook CivicTheme preset renders it.
- `argTypes` — one entry per prop declared in `.component.yml`. Keys must match prop names exactly.

## Args map to `.component.yml` props

Every key in `argTypes` (and in a story's `args`) must correspond to a prop in the component's `.component.yml`. If a prop is added or renamed in YAML, update the story to match — otherwise the control renders with no effect.

## `argTypes` for enum props

Enums in YAML become `radio` or `select` controls with explicit `options`:

```yaml
# my-card.component.yml (excerpt)
props:
  theme:
    type: string
    enum: [light, dark]
  size:
    type: string
    enum: [small, medium, large]
```

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

## Named export for the default story

Every story file exports at least one named story alongside the default export:

```js
export const Default = {
  args: {
    theme: 'light',
    vertical_spacing: 'none',
    with_background: false,
    title: 'Example card title',
  },
};
```

The `args` object supplies initial values for the controls. Additional named exports (e.g. `Dark`, `WithBackground`) can override specific args to document visual variants.
