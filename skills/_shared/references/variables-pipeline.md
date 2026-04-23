# Variables Pipeline — from `ct-component-property()` to compiled CSS custom properties

How CivicTheme turns a theme-sensitive SCSS declaration into a CSS custom property the browser can resolve — and how the generators must scaffold the variable block so the pipeline does not dead-end.

Apply to both new SDC components (sub-theme) and new UIKit components (upstream authoring). The file location differs by context (see **Where to write** below), but the four-stage flow is identical.

---

## The four stages

```
  (1) Component SCSS
      @include ct-component-property($root, $theme, [path…,] property)
                 │
                 ▼
  (2) CSS custom property reference
      #{property}: var(--ct-[component]-[theme]-[path-…-]property);
                 │
                 ▼
  (3) variables.components.scss — value source
      $ct-[component]-[theme]-[path-…-]property: ct-color-light('token');
      $ct-[component]-[theme]-[path-…-]property: ct-color-dark('token');
                 │
                 ▼
  (4) style.css_variables.scss — export
      Emits every $ct-* SCSS variable as a --ct-* CSS custom property
      declaration in the compiled stylesheet.
```

Each stage has a fixed name and a fixed role. Skipping any stage (most often stage 3) produces a component that renders `unset` for themed properties because the custom property the template asks for has no declaration anywhere in the cascade.

---

## Stage 1 — the mixin call

`ct-component-property($root, $theme, …args)` accepts:

- `$root` — the BEM root selector captured as `$root: &;`
- `$theme` — injected by the enclosing `ct-component-theme($root) using($root, $theme)` block; do not pass manually
- remaining positional args — zero or more **sub-element path segments** followed by one **CSS property name**

Examples, paired with the variable name each produces for `.ct-card`:

| Call | Variable base (light + dark pair) |
|---|---|
| `ct-component-property($root, $theme, color)` | `$ct-card-[theme]-color` |
| `ct-component-property($root, $theme, background-color)` | `$ct-card-[theme]-background-color` |
| `ct-component-property($root, $theme, title, color)` | `$ct-card-[theme]-title-color` |
| `ct-component-property($root, $theme, button, background-color)` | `$ct-card-[theme]-button-background-color` |
| `ct-component-property($root, $theme, button, hover, background-color)` | `$ct-card-[theme]-button-hover-background-color` |

The last positional argument is always the CSS property. Everything between `$theme` and that property joins with hyphens as the sub-element / state path.

The component name is derived from `$root` by stripping the leading `.ct-`. `$root: &` on `.ct-card` yields a component segment of `card`.

---

## Stage 2 — the custom property reference

`ct-component-property` expands (conceptually) to:

```scss
#{$property}: var(--ct-#{$component}-#{$theme}-#{$path-}#{$property});
```

The variable name mirrors the SCSS variable exactly, minus the leading `$`. This is the contract between the component stylesheet and the variable file — if they do not agree on the name, the pipeline breaks silently.

---

## Stage 3 — the variables.components.scss block

Every `ct-component-property` call in the component SCSS needs **two matching declarations** (one for `light`, one for `dark`) in `variables.components.scss`:

```scss
//
// [Component Name] variables.
//

// light theme
$ct-[component]-light-[path-]-[property]: ct-color-light('[token-name]');

// dark theme
$ct-[component]-dark-[path-]-[property]: ct-color-dark('[token-name]');
```

`ct-color-light('token')` and `ct-color-dark('token')` resolve a named colour from the active palette for the given theme. Common token names include `typography`, `background-light`, `background-dark`, `interactive`, `focus`, `border-light`, `border-dark` — the full set is defined by the design palette the theme consumes. Pick a sensible default and let the author refine.

Do **not** include `!default` when these declarations are emitted into the sub-theme's custom file — the sub-theme imports before the base, so a bare assignment wins. In an upstream UIKit component the base declarations do use `!default` so sub-themes can override them; match the surrounding convention of the file you are writing into.

### Non-colour properties

`ct-component-property` is not limited to colour. For properties like `border-width`, `border-radius`, `padding`, or `font-family` use an appropriate CivicTheme token function or a raw value instead of `ct-color-*`:

```scss
$ct-card-light-border-radius: ct-particle(0.5);
$ct-card-light-title-font-size: ct-typography-size('heading-4');
```

One common footgun: geometry tokens (`border-radius`, spacing between sub-elements) are usually **not theme-variant** — they take one value across light and dark. For those, a single declaration without the `-light` / `-dark` split is fine, and the component SCSS references them via `var(--ct-[component]-*)` directly (see `references/scss-patterns.md` "Component geometry tokens"), not through `ct-component-property`.

---

## Stage 4 — the export

`style.css_variables.scss` (upstream) imports every `variables.*.scss` file and walks the resulting `$ct-*` SCSS variables, emitting each one as a CSS custom property declaration scoped to `:root` or a theme selector. Generators never edit this file — it is upstream plumbing that runs automatically once the variable declarations in stage 3 exist.

If a component's `var(--ct-…)` reference resolves to nothing at runtime, the fault is almost always a missing stage 3 declaration, not a broken stage 4 export.

---

## Where to write

| Context | File | Notes |
|---|---|---|
| Sub-theme (new SDC component, `civictheme-sdc-generator`) | `components/variables.components.scss` | Sub-theme-level custom file. Append a block per component. Create the file if it does not exist. Omit `!default`. |
| UIKit authoring (new upstream component, `civictheme-uikit-component-generator`) | `packages/sdc/components/variables.components.scss` | Custom authoring file in the SDC source of truth. Same append-per-component pattern; `components:update:twig` carries the file into `packages/twig/`. |

**Never write to `00-base/_variables.components.scss`.** That path is upstream CivicTheme base content regardless of whether you are in a sub-theme or the UIKit repo; editing it couples your component to a file you do not own and the change will be lost at the next upstream pull.

---

## Generator responsibility

At generation time, after emitting the component SCSS:

1. Enumerate every `ct-component-property($root, $theme, …args)` call the generator just produced.
2. For each call, derive the variable base name as `[component]-[theme]-[joined-path-segments]-[property]`.
3. Emit a block in the target `variables.components.scss` with matched light + dark pairs, using `ct-color-light('token')` / `ct-color-dark('token')` as default values for colour properties, or the appropriate token function / raw value for non-colour properties.
4. Append to the existing file if present; create it if not. Never modify `00-base/_variables.components.scss`.
5. List the generated / updated variables file in the output contract.

A component that declares theme-sensitive properties but ships no matching stage-3 block is incomplete — treat it as a generator failure, not a post-generation todo for the user.
