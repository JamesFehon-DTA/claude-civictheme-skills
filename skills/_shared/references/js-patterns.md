# JS Authoring Patterns

CivicTheme component JS conventions. Use these patterns when emitting `.js` files for SDC components, UIKit components, or overrides.

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
