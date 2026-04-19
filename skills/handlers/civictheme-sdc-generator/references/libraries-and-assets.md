# Libraries and Asset Loading

How Drupal loads CSS and JS in a CivicTheme sub-theme — including SDC auto-loading, library declarations, and asset compilation. For replacing CivicTheme base-theme assets (`libraries-override`), see the override-generator skill.

## The Three Asset Loading Methods

### 1. SDC Auto-Loading (CSS only)

When a component template is rendered via `{% include 'ns:component' %}`, Drupal's SDC system automatically enqueues the compiled `.css` file from the component directory. **No library entry is needed.**

This applies to any component that has a `.component.yml` file (i.e., is a registered SDC).

```
components/03-organisms/filterable-table/
├── filterable-table.component.yml  ← SDC registered
├── filterable-table.twig
├── filterable-table.scss
└── filterable-table.css            ← auto-loaded when template renders
```

**JS is never auto-loaded by SDC.** Even for SDC components, JS must be attached via a library.

### 2. Conditional Library Attachment (preprocess hook)

Attach a library only on pages where a specific paragraph or component renders. This avoids loading JS globally when it's only needed in certain contexts.

```php
// In a paragraph preprocess hook:
$variables['#attached']['library'][] = '[THEME_MACHINE_NAME]/filterable-table';
```

The library is only queued when that preprocess hook runs, meaning the JS loads only on pages containing that paragraph type.

### 3. Global Library (`.info.yml`)

Attach a library on every page, regardless of what content is on the page.

```yaml
# [THEME_MACHINE_NAME].info.yml
libraries:
  - [THEME_MACHINE_NAME]/table-sort
```

Use this for JS/CSS enhancements that target markup that could appear anywhere (e.g., a class applied via CKEditor Block Styles).

---

## CSS File Path Rule: `components/` vs `components_combined/`

The sub-theme's `.info.yml` registers Drupal SDC namespaces pointing to `components/` only — `components_combined/` is never a Drupal SDC source directory. This produces a clear rule for library CSS paths:

| Component origin | Drupal SDC loads CSS from | Library path to reference |
|---|---|---|
| Sub-theme's own (new SDC, Type 4 enhancement) | `[THEME_DIR]/components/[level]/[name]/` | `components/[level]/[name]/[name].css` |
| CivicTheme base component, loaded explicitly | `civictheme/components/[level]/[name]/` | `components_combined/[level]/[name]/[name].css` |

**Why `components_combined/` for base theme components?**

`components_combined/` is the build system's merged output. The sub-theme build copies base theme CSS into it, then overwrites with sub-theme compiled CSS if an override exists. Referencing `components_combined/` means you always get the "active" version — base theme CSS by default, sub-theme override automatically if one is created later. Referencing `../../contrib/civictheme/` would silently bypass any future override.

---

## Declaring Libraries (`[THEME_MACHINE_NAME].libraries.yml`)

### JS-only library (SDC component with JS behaviour)

```yaml
filterable-table:
  js:
    components/03-organisms/filterable-table/filterable-table.js: {}
  dependencies:
    - core/drupal
    - core/once
    - [THEME_MACHINE_NAME]/global
```

CSS is omitted — SDC auto-loads it.

### Loading a CivicTheme base component's CSS explicitly

SDC auto-loading only fires when the component *template* is rendered via `{% include %}`. If you apply a CivicTheme class (e.g. `ct-select`, `ct-input`) to a native HTML element directly, the CSS is never attached — it does not exist in the global bundle.

To fix this, add the component CSS file to the library that loads for your component:

```yaml
filterable-table:
  css:
    component:
      # ct-select and ct-input are not in the global bundle — load them explicitly
      # so they are available when native elements carry those classes.
      components_combined/01-atoms/select/select.css: {}
      components_combined/01-atoms/input/input.css: {}
  js:
    components/03-organisms/filterable-table/filterable-table.js: {}
  dependencies:
    - core/drupal
    - core/once
    - [THEME_MACHINE_NAME]/global
```

**Always reference `components_combined/` — not `../../contrib/civictheme/`.**

`components_combined/` is the canonical merged output of the build system. It reflects the "active" version of every component — either the base theme's compiled CSS, or the sub-theme override if one exists. The contrib path bypasses any sub-theme override and hardcodes the base theme location.

> The `components_combined/` directory is a build artifact inside the sub-theme root. Drupal resolves library paths relative to the declaring theme, so `components_combined/01-atoms/select/select.css` resolves correctly to the sub-theme's `components_combined` directory.

### CSS + JS library (non-SDC enhancement)

Required when there is no `.component.yml` and the SDC system won't auto-load anything:

```yaml
table-sort:
  css:
    theme:
      components/01-atoms/table-sort/table-sort.css: {}
  js:
    components/01-atoms/table-sort/table-sort.js: {}
  dependencies:
    - core/drupal
    - core/once
```

### CSS weight and preprocessing

```yaml
css-variables:
  css:
    theme:
      dist/styles.variables.css: { preprocess: false, weight: 10 }
```

- `preprocess: false` — skips Drupal's CSS aggregation for this file (useful for CSS custom properties that must remain un-minified)
- `weight` — controls load order; default is 0; higher values load later

### Dependency on `[THEME_MACHINE_NAME]/global`

The `global` library is the sub-theme's main JS bundle (`dist/scripts.drupal.base.js`). Components that use shared utilities from the base bundle should declare it as a dependency:

```yaml
my-component:
  js:
    components/03-organisms/my-component/my-component.js: {}
  dependencies:
    - core/drupal
    - core/once
    - [THEME_MACHINE_NAME]/global
```

---

## The `global` Library

The `global` library is the sub-theme's foundational library, declared in `[THEME_MACHINE_NAME].libraries.yml`:

```yaml
global:
  css:
    theme:
      dist/styles.base.css: {}
      dist/styles.theme.css: {}
      dist/styles.variables.css: {}
  js:
    dist/scripts.drupal.base.js: {}
  dependencies:
    - core/drupal
    - core/once
    - core/drupalSettings
```

This loads on every page.

> `libraries-override` guidance — for replacing CivicTheme base-theme assets with sub-theme equivalents — is documented in the override-generator skill. It does not apply when declaring libraries for new components or extensions, which simply load alongside CivicTheme's.

---

## Asset Compilation

Whether assets need a build step depends on their origin.

**SDC components** — the build compiles each component's `.scss` → `.css` (written next to the source file) and bundles global assets into `dist/`. Run the build after adding or changing SCSS:

```bash
npm run dist      # compile SCSS → CSS, bundle JS → dist/
```

The build produces:
- Each component's `.scss` → `.css` (written next to the source file)
- All component SCSS bundled into `dist/styles.base.css` and `dist/styles.theme.css`
- All component JS bundled into `dist/scripts.drupal.base.js`

**Plain CSS/JS extensions** — files under `components/[level]/[name]/` with no `.component.yml` ship as-is. Write `.css` directly (not `.scss`), and `.js` directly. No build step is required — Drupal reads the files straight from the sub-theme.

**If a referenced CSS file is missing, Drupal will silently skip it** (no error in most environments) — resulting in unstyled components. For SDC components, always run `npm run dist` after SCSS changes.

---

## Decision Guide

| Situation | Method |
|---|---|
| New SDC component — CSS only | SDC auto-load (no library needed) |
| New SDC component — has JS | Conditional via preprocess `#attached`, or global if needed everywhere |
| JS/CSS enhancement (no `.component.yml`) | Explicit library — both CSS and JS entries required |
| Apply a CivicTheme class to a native HTML element | Add `components_combined/[level]/[name]/[name].css` to the enclosing component's library |
| Enhancement active on every page | Global: `libraries:` in `.info.yml` |
| Enhancement only on specific paragraph pages | Conditional: `$variables['#attached']` in preprocess hook |
