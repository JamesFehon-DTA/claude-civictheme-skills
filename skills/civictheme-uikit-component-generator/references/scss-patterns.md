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
