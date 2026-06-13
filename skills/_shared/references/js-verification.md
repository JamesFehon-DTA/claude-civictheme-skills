# Verifying CivicTheme JS behaviour

Two traps make agents wrongly conclude "the JS doesn't initialise" when reading the DOM after a synthetic click in Storybook. Both come from reading an attribute and inferring state from it. Verify side-effects and respect animation timing instead.

## Trap A – the attribute string is not a reliable init signal

The Storybook HTML addon (`@whitespace/storybook-addon-html`, wired in `packages/sdc/.storybook/main.js`; serialised by the `withHTML` decorator in `preview.js`) serialises the live DOM's `innerHTML`. After `collapsible` initialises it sets `data-collapsible="true"` on the root (`collapsible.js`), so the addon's HTML panel shows `data-collapsible="true"`. But the source Twig markup is bare `data-collapsible` (value `""`) – see `accordion.twig` and `search-results.twig`. So the same attribute reads differently depending on what you inspect, and `=== 'true'`, truthy, and `hasAttribute()` checks diverge:

- `getAttribute('data-collapsible')` → `""` before init (bare markup), `"true"` after init.
- `hasAttribute('data-collapsible')` → `true` in both cases – it never tells you whether init ran.

**Do not infer init from the attribute.** Verify init via a DOM side-effect the addon cannot fabricate from source markup: the injected `.ct-collapsible__icon` node, which `collapsible.js` appends into the trigger only on successful init.

```js
// init ran iff the icon was injected
el.querySelector('[data-collapsible-trigger] .ct-collapsible__icon') !== null
```

For other behaviours, key off their init side-effects from `core-behaviours.md`: `tooltip` adds `aria-describedby` to its button; `scrollspy`/`flyout`/`tooltip` set their own `data-*="true"` *only when they actually ran*, so pair the attribute read with a structural side-effect rather than trusting the string alone.

## Trap B – `aria-expanded` updates on `transitionend`, not on click

`collapsible` updates `aria-expanded` / `aria-hidden` inside `setCollapsedState` / `setExpandedState`, which run from the `transitionend` handler after the panel height animation. The animation runs for `data-collapsible-duration` ms (default 500; `accordion.twig` uses 250). An immediate post-click read shows the **stale** value.

**Verify toggles with animation-aware timing.** After dispatching the click, wait longer than the component's duration before asserting:

```js
trigger.click();
await new Promise((r) => setTimeout(r, 600)); // > data-collapsible-duration
// now aria-expanded / data-collapsible-collapsed reflect the new state
```

Or assert on the transition directly by listening for `transitionend` on the panel rather than polling on a fixed delay. Either way, never read collapsible state on the same tick as the click.
