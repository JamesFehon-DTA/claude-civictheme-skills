# JS Authoring Patterns

CivicTheme component JS conventions. Use these patterns when emitting `.js` files for SDC components, UIKit components, or overrides.

## First: can a core behaviour do this?

**Before authoring or fixing any component JS, run the reuse gate.** Most interactions (show/hide, accordion, dismiss, sticky, reveal-on-scroll, tabs, popover, skip-link) are already implemented by a `00-base`/atom/molecule behaviour. Pattern-match the interaction in `core-behaviours.md`; if a primitive matches, emit its data-attribute markup and **delete the bespoke JS** instead of writing or fortifying it. Author new JS only when the table has no match.

---

## Constructor + root-level `querySelectorAll` init

CivicTheme's existing component JS (`navigation.js`, `accordion.js`, `tabs.js`) follows a consistent shape: a constructor function that takes the root element, plus an init function that queries for every matching root in the document and instantiates one constructor per root.

```js
function CTCollapsible(el) {
  this.el = el;
  this.trigger = el.querySelector('[data-collapsible-trigger]');
  this.panel = el.querySelector('[data-collapsible-panel]');
  this.init();
}

CTCollapsible.prototype.init = function () {
  this.trigger.addEventListener('click', this.toggle.bind(this));
};

CTCollapsible.prototype.toggle = function () {
  var collapsed = this.el.getAttribute('data-collapsible-collapsed') === 'true';
  this.el.setAttribute('data-collapsible-collapsed', collapsed ? 'false' : 'true');
};

document.querySelectorAll('[data-collapsible]').forEach(function (el) {
  new CTCollapsible(el);
});
```

When the enhancement ships via a Drupal library and must run on AJAX-inserted markup, wrap the `querySelectorAll` loop in `Drupal.behaviors` with `once()`:

```js
Drupal.behaviors.ctCollapsible = {
  attach: function (context) {
    once('ct-collapsible', '[data-collapsible]', context).forEach(function (el) {
      new CTCollapsible(el);
    });
  },
};
```

Use `data-` attribute selectors — not classes — for JS targeting so markup changes do not break behaviour. One constructor instance per root; keep all per-instance state on `this`.

---

## When the one-time top-level init actually runs

The top-level `document.querySelectorAll(...).forEach(new X())` works for **`00-base` behaviours** because they are bundled into `civictheme.base` and imported eagerly by `packages/sdc/.storybook/preview.js` (`import '../dist/civictheme.base'`). That bundle evaluates once, before any story, so its `querySelectorAll` sweep finds every matching root already in the document.

A **per-component `.js`** does NOT get the same free initialisation. The Storybook SDC plugin (`packages/sdc/.storybook/sdc-plugin.js`) auto-discovers a component's `.js` via its `.twig` import, but the module's top-level `querySelectorAll().forEach()` runs at **module-evaluation time, which is before the story mounts its markup into the DOM**. The sweep finds nothing, and the component looks uninitialised even though the file loaded.

When a per-component file legitimately needs JS (i.e. `core-behaviours.md` has no matching primitive – check that first), initialise so it survives both first mount and later DOM insertion:

```js
function initAll(context) {
  (context || document).querySelectorAll('[data-x]').forEach((el) => new CTX(el));
}

// Drupal: re-attach on AJAX-inserted markup.
Drupal.behaviors.ctX = { attach: (context) => initAll(context) };

// Storybook (no Drupal): re-run when the story injects markup after module eval.
new MutationObserver(() => initAll(document)).observe(document.body, { childList: true, subtree: true });
initAll(document);
```

This dual-init pattern (`initAll(context)` + `Drupal.behaviors` + `MutationObserver`) is the shape the digital.gov.au components use. Treat it as a **last resort, only after the reuse check fails** – the `MutationObserver` + global `Drupal.behaviors` is overhead you should not add to fortify bespoke JS that a primitive could replace. It is not the default for "any interactive component"; most interactive components are markup over a `00-base` behaviour and need no per-component init at all.

---

## `data-collapsible-collapsed` controls state — not `aria-expanded`

CivicTheme's collapsible primitive is driven by `data-collapsible-collapsed="true" | "false"` on the root element. CSS rules key off that attribute to hide and show the panel, and the JS flips the attribute on toggle.

```html
<div class="ct-[name]" data-collapsible data-collapsible-collapsed="true">
  <button type="button" data-collapsible-trigger aria-expanded="false" aria-controls="panel-1">
    Toggle
  </button>
  <div id="panel-1" data-collapsible-panel>…</div>
</div>
```

`aria-expanded` still goes on the trigger button for screen readers — update it in step with `data-collapsible-collapsed` — but **CSS and JS must not branch on `aria-expanded`**. The state selector is the data attribute. Mixing the two causes desync: toggling `aria-expanded` alone leaves the panel visually open, toggling only `data-collapsible-collapsed` leaves AT unaware.

```js
// Always flip both together
this.el.setAttribute('data-collapsible-collapsed', collapsed ? 'false' : 'true');
this.trigger.setAttribute('aria-expanded', collapsed ? 'true' : 'false');
```

---

## `display: block !important` on a collapsible panel breaks the JS

The collapsible panel's visibility is controlled by CSS rules keyed on `[data-collapsible-collapsed="true"]` on the root. Those rules typically set `display: none` (or `height: 0` + `overflow: hidden`) on the panel when collapsed.

An override like:

```scss
// Don't
.ct-[name]__panel {
  display: block !important;
}
```

forces the panel visible regardless of the collapsed attribute — the visual state no longer reflects the JS state. Clicks still toggle the attribute, but nothing shows or hides. The bug looks like "the JS is broken" but the JS is fine; the `!important` is overriding the state-dependent CSS.

If the panel needs a different block-level layout, scope the override under the expanded state:

```scss
// Right — only applies when the root is expanded
.ct-[name][data-collapsible-collapsed="false"] .ct-[name]__panel {
  display: flex;  // or block, grid — whatever the layout needs
}
```

Same rule applies to `visibility: visible !important`, `height: auto !important`, and `overflow: visible !important` on collapsible panels — any `!important` that defeats the collapsed-state CSS breaks the component.

---

## Verifying the behaviour

When checking whether JS initialised or a toggle worked, do not read an attribute string and infer state – the Storybook HTML addon serialises post-init attribute values, and `collapsible` updates `aria-expanded` only on `transitionend` (~500ms). See `js-verification.md` for the two traps and the side-effect / animation-aware checks that avoid them.
