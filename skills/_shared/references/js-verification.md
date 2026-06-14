# Verifying CivicTheme JS behaviour

Two traps make agents wrongly conclude "the JS doesn't initialise" when verifying behaviour in Storybook. Read the live DOM, and respect animation timing.

## Trap A – don't mistake the HTML-addon panel for source markup

The live DOM is reliable. After `collapsible` initialises, the live root genuinely carries `data-collapsible="true"` (`collapsible.js`) and the injected `.ct-collapsible__icon` node – either one, read off the live DOM, confirms init ran.

The trap is reading the **HTML-addon panel** and reasoning about it as if it were the component's source. The Storybook HTML addon (`@whitespace/storybook-addon-html`, wired in `packages/sdc/.storybook/main.js`; serialised by the `withHTML` decorator in `preview.js`) prints a *post-init serialisation* of `innerHTML`, so its panel shows `data-collapsible="true"` even though the source Twig markup is bare `data-collapsible` (value `""`) – see `accordion.twig`, `search-results.twig`. Comparing the panel against the bare source and inferring a problem is the mistake; the panel is a snapshot of the running DOM, not the template.

**Inspect the live DOM directly** (e.g. `preview_eval`), not the rendered HTML panel. Either signal works:

```js
el.getAttribute('data-collapsible') === 'true'                              // init marker on the live root
|| el.querySelector('[data-collapsible-trigger] .ct-collapsible__icon')     // injected icon, equally reliable
```

Other behaviours expose their own live-DOM init markers (`core-behaviours.md`): `tooltip` adds `aria-describedby` + `data-tooltip="true"`; `scrollspy`/`flyout` set `data-*="true"`. Read them from the live DOM, not the panel.

## Trap B – on an animated toggle, `aria-expanded` lands on `transitionend`

`collapsible` sets `aria-expanded` / `aria-hidden` in `setCollapsedState` / `setExpandedState`. These run **synchronously** for the initial state (at init) and on the non-animated path (`data-collapsible-duration="0"`). They are deferred to the panel's `transitionend` handler **only on an animated toggle** (duration > 0) – and a real user click animates, dispatching `ct.collapsible.*` with `animate: true`. The animation runs for `data-collapsible-duration` ms (default 500; `accordion.twig` uses 250), so an immediate read after an animated click shows the **stale** value.

So: the initial render and a `duration:0` toggle are safe to read immediately; an animated toggle is not. **Don't read `aria-expanded` on the same tick as an animated click, and don't rely on it as your only signal** – `transitionend` can fail to fire (no real height change, panel never visible), leaving the read hung or stale forever.

Listen for `transitionend` but cap it with a timeout fallback, then read state:

```js
trigger.click();
await new Promise((resolve) => {
  const done = () => { panel.removeEventListener('transitionend', done); clearTimeout(t); resolve(); };
  const t = setTimeout(done, durationMs + 100); // fallback if transitionend never fires
  panel.addEventListener('transitionend', done);
});
// now read aria-expanded / data-collapsible-collapsed
```
