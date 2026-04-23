# SCSS Authoring Patterns

Canonical references:
- `packages/sdc/components/01-atoms/label/label.scss` — typography iteration, full theme pattern
- `packages/sdc/components/02-molecules/accordion/accordion.scss` — breakpoints, geometry tokens, nested theme

SCSS content is identical across `packages/sdc/` and `packages/twig/`. Emit the same file body to both packages; `components:update:twig` keeps them aligned thereafter.

---

## File structure

```scss
//
// CivicTheme [Component Name] component styles.
//

.ct-[component] {
  $root: &;

  // layout and typography
  @include ct-typography('[scale]');
  margin-bottom: ct-spacing();

  // sub-elements
  #{$root}__[element] {
    ...
  }

  // theme rules always last
  @include ct-component-theme($root) using($root, $theme) {
    @include ct-component-property($root, $theme, color);
  }
}
```

---

## `@use` imports

Only include when the generated SCSS actually calls the corresponding functions:

```scss
@use 'sass:map';    // only when using map.keys(), map.get(), etc.
@use 'sass:string'; // only when using string.index(), string.slice(), etc.
```

Most components need neither. The label component uses both only because it iterates `_ct-typography-all()` map keys to generate size modifiers — that is unusual. Do not include these imports by default.

---

## Typography

```scss
@include ct-typography('label-regular');
@include ct-typography('heading-6');
@include ct-typography('text-regular');
```

Scale names follow the pattern `[category]-[size]`. Common values: `label-regular`, `label-small`, `heading-1` through `heading-6`, `text-regular`, `text-small`.

---

## Spacing

```scss
margin-bottom: ct-spacing();      // 1 unit
padding: ct-spacing(3);           // 3 units
gap: ct-spacing(2);
```

---

## Pixel-precise values

For border widths and other sub-pixel values:

```scss
border: ct-particle(0.125) solid;  // 0.125 * base particle = 2px
```

---

## Breakpoints

```scss
@include ct-breakpoint(m) {
  flex-wrap: nowrap;
}
```

Common breakpoint identifiers: `xs`, `s`, `m`, `l`, `xl`.

---

## Theme rules

Use `ct-component-theme` for all theme-sensitive properties (color, background-color, border-color). This emits both light and dark variants correctly.

```scss
@include ct-component-theme($root) using($root, $theme) {
  @include ct-component-property($root, $theme, color);
  @include ct-component-property($root, $theme, background-color);
  @include ct-component-property($root, $theme, border-color);

  #{$root}__[sub-element] {
    @include ct-component-property($root, $theme, [sub-element], color);
  }
}
```

`ct-component-property` resolves the design token for the current theme. The optional third argument is a sub-element key: `ct-component-property($root, $theme, button, background-color)`.

---

## Component geometry tokens

For layout-level values that vary per component but are NOT theme-variant (border-radius, component-specific spacing), `var(--ct-[component]-*)` is acceptable:

```scss
border-radius: var(--ct-accordion-item-border-radius);
padding-left: var(--ct-accordion-space-horizontal);
```

These tokens are defined in the design system's variables layer, not inline in component files. Only reference tokens that already exist — do not invent new `--ct-` custom properties inside component SCSS.

---

## BEM child elements

Always use `$root` to reference the parent selector, not a hardcoded string.

```scss
.ct-[component] {
  $root: &;

  #{$root}__header { ... }
  #{$root}__content { ... }

  &#{$root}--with-background { ... }  // modifier on root
}
```

---

## Banned patterns

| Pattern | Reason |
|---|---|
| Hardcoded `rem`/`px` values | Use `ct-spacing()`, `ct-particle()`, or design tokens |
| `var(--ct-color-light-*)` / `var(--ct-color-dark-*)` inline | Use `ct-component-property()` inside `ct-component-theme()` |
| Flat `.ct-theme-light { }` / `.ct-theme-dark { }` blocks | Use `ct-component-theme($root) using(...)` |
| `var(--ct-typography-*)` inline | Use `ct-typography('[scale]')` mixin |
| CSS custom property declarations at file root | All declarations must be inside a selector |
| Compiled/minified CSS output | This is SCSS source — write mixins and tokens, not compiled output |

---

## Gotchas

### Contextual override scoping — which file owns which rule

When a parent component restyles a sub-component that appears inside its template, split the rules across three locations by kind:

| Kind of rule | Where it belongs |
|---|---|
| Selector-scoped restyling of a sub-component (structural adjustments that only apply in this parent's context) | The **parent's** `.scss` file, scoped under `.ct-[parent]` — e.g. `.ct-[parent] .ct-[child]__title { ... }` |
| Colour, background-color, border-color, any property resolved via `ct-component-property()` | Inside a `ct-component-theme($root) using($root, $theme)` block on the selector that owns the element |
| Border width/style, `border-radius`, padding, margin, flex, grid, width/height | A layout-focused block (near the top of the selector, outside `ct-component-theme`) |

The theme block is for properties whose value depends on light vs dark. Layout and geometry never depend on theme, so keeping them separate keeps the theme block small and auditable. Putting border-width inside `ct-component-theme` also hides the fact that the value is theme-invariant and makes later `ct-component-property` calls harder to read.

### `<fieldset>` needs explicit `min-width: 0`

`<fieldset>` has an implicit `min-width: min-content` in every browser. This overrides `flex-basis` and `width` — a fieldset inside a flex row refuses to shrink below its content's minimum width, breaking layouts that other elements handle fine.

```scss
.ct-[component]__fieldset {
  min-width: 0;  // always — even when no other width rule is set
}
```

Add this to any fieldset you emit, regardless of whether it is inside flex or grid. Browsers that would otherwise layout it correctly ignore the declaration; browsers that break without it finally behave.

### `flex: 1 1 0` over `flex: 1 1 auto` for growing siblings

When two flex children share space and one has a fixed or intrinsic width (an icon, a fixed-width label), use `flex: 1 1 0` on the growing sibling, not `flex: 1 1 auto`.

```scss
.ct-[component]__row {
  display: flex;
  gap: ct-spacing();
}

.ct-[component]__icon {
  flex: 0 0 auto;           // fixed intrinsic width
}

.ct-[component]__label {
  flex: 1 1 0;              // fills remaining space — NOT `1 1 auto`
  min-width: 0;             // allows text truncation / wrapping
}
```

`flex: 1 1 auto` uses each child's intrinsic content size as the flex basis, so two growing siblings with different text lengths end up with different widths. `flex: 1 1 0` gives both siblings the same starting basis and distributes remaining space evenly. Pair with `min-width: 0` so long content can truncate or wrap instead of pushing the container wider.
