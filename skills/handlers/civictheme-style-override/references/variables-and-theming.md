# Variables and Theming

How to override CivicTheme's design tokens and component styles in a sub-theme — without modifying the base theme.

## The Two Variable Files

CivicTheme splits variables into two files to allow targeted overrides:

| File | What it controls | When to edit it |
|---|---|---|
| `components/variables.base.scss` | Brand colours, typography scale, spacing particle, breakpoints, grid | When a change should cascade across all components automatically |
| `components/variables.components.scss` | Per-component appearance (colour, border, spacing per component) | When changing a specific component without affecting others |

Both files live in the **sub-theme's** `components/` directory. The build system imports them before CivicTheme's own files, so sub-theme values take precedence.

---

## The Override Mechanism: Removing `!default`

CivicTheme declares every variable with the `!default` flag:

```scss
// In CivicTheme source:
$ct-button-light-primary-background-color: #002664 !default;
```

`!default` means "only assign this value if the variable is not already defined". The sub-theme imports its variable files **before** CivicTheme's files, so declaring the same variable **without `!default`** wins:

```scss
// In your sub-theme's variables.components.scss:
$ct-button-light-primary-background-color: #005ea5;  // no !default — this wins
```

**Never include `!default` in sub-theme overrides.** If you do, CivicTheme's value will take precedence.

---

## Three Levels of Colour Override

Override at the level that matches the scope of change needed:

### Level 1 — Brand Foundation (`variables.base.scss`)

Changes here cascade to everything. Derived component colours recalculate automatically.

```scss
// Shifts the primary brand colour everywhere it's used
$ct-colors-brands: (
  'primary': #005ea5,
  'secondary': #e6e9eb,
  'accent': #f0a500,
);
```

### Level 2 — Semantic Palette (`variables.base.scss`)

Set specific semantic colour roles without changing the brand definition:

```scss
// Override the heading colour directly
$ct-colors: map.merge($ct-colors, (
  'heading': #1a1a1a,
  'body': #333333,
  'link': #005ea5,
));
```

### Level 3 — Individual Component (`variables.components.scss`)

The most targeted option — change a single state of a single component:

```scss
$ct-button-light-primary-background-color: #005ea5;
$ct-button-light-primary-hover-background-color: #003d72;
$ct-button-light-primary-color: #ffffff;
```

---

## Variable Naming Pattern

`$ct-[component]-[theme]-[subcomponent]-[state]-[property]`

| Segment | Examples |
|---|---|
| `[component]` | `button`, `card`, `header`, `tag` |
| `[theme]` | `light`, `dark` |
| `[subcomponent]` | `primary`, `secondary`, `title`, `icon` (optional) |
| `[state]` | `hover`, `focus`, `active`, `disabled` (optional) |
| `[property]` | `color`, `background-color`, `border-color`, `font-size` |

Full examples:
- `$ct-button-light-primary-background-color`
- `$ct-button-light-primary-hover-background-color`
- `$ct-button-dark-secondary-border-color`
- `$ct-card-light-title-color`
- `$ct-tag-dark-background-color`

---

## SASS Map Extension

For variables that are SASS maps (colour palettes, breakpoints, icon sets), use `map.merge()` to **add to** the map rather than replacing it entirely. Replacing breaks things when CivicTheme adds new keys to the map in a future update.

```scss
@use 'sass:map';

// Extend the colour map — don't replace it
$ct-colors: map.merge($ct-colors, (
  'agency-highlight': #ff6b35,
  'agency-background': #f5f5f5,
));

// Extend breakpoints — don't replace them
$ct-breakpoints: map.merge($ct-breakpoints, (
  'xxxl': 1920px,
));
```

---

## Where to Find Available Variables

Reference the base theme's source files to see all available variables:

```
[BASE_THEME_DIR]/components/variables.base.scss       ← base design tokens
[BASE_THEME_DIR]/components/variables.components.scss ← per-component vars
```

Copy the variable you want to override into your sub-theme's matching file, change the value, and remove `!default`.

---

## SCSS Component Theme Mixin

For light/dark theme support within SCSS, use the CivicTheme theme mixin:

```scss
.ct-[name] {
  $root: &;

  // Light theme styles (default)
  @include ct-component-theme($root) using($root, $theme) {
    // Apply a colour from the component's theme variable map
    @include ct-component-property($root, $theme, background-color);

    #{$root}__title {
      @include ct-component-property($root, $theme, title, color);
    }
  }
}
```

This mixin iterates over light and dark theme contexts, applying the correct CSS custom properties for each. The `ct-component-property` mixin references the `$ct-[component]-[theme]-[property]` variable automatically.

---

## Design Token Functions

Use these functions instead of hardcoded pixel values:

```scss
// Spacing — multiples of the 8px particle unit
padding: ct-spacing(2);        // 16px
margin-bottom: ct-spacing(3);  // 24px

// Raw particle unit
border-width: ct-particle(0.125);  // 1px

// Typography preset
@include ct-typography('heading-4');

// Responsive breakpoint (mobile-first, min-width only)
@include ct-breakpoint(m) {
  // styles for medium viewport and up
}
```

Breakpoint names: `xxs`, `xs`, `s`, `m`, `l`, `xl`, `xxl`

---

## Build After Variable Changes

After editing any SCSS variable file:

```bash
npm run dist
```

Variable changes affect compiled CSS — without rebuilding, changes won't appear in Drupal or Storybook.
