# Core CivicTheme behaviours – reuse before authoring

CivicTheme ships a set of `00-base` and atom/molecule JavaScript behaviours that already implement the common interactions. **Before authoring or fixing any component JS, check this table.** If a core behaviour already provides the interaction, reuse it by emitting its data-attribute markup and delete the bespoke JS – do not hand-roll a button + panel + custom show/hide script.

All paths are under `packages/sdc/components/`. Each behaviour self-initialises (see "Init" column) and marks itself initialised, so you add markup, not script.

## Interaction → primitive

Pattern-match the interaction the user describes to a primitive:

| Interaction | Primitive |
|---|---|
| Show/hide a panel, expand/collapse, accordion, "more/less" toggle | **collapsible** |
| Reveal/dismiss an overlay, off-canvas menu, mobile drawer, "close all" | **flyout** |
| Gate a behaviour by breakpoint (mobile-only toggle, desktop-only layout) | **responsive** (drives collapsible/flyout) |
| Sticky header, reveal-on-scroll, a "scrolled" state class | **scrollspy** |
| Tabbed panels | **tabs** |
| Hover/focus popover | **tooltip** |
| Skip link / jump focus to a target | **skip-to-target** |

A **mobile filter toggle** (button reveals a filter panel below a breakpoint) is `collapsible` (the panel) gated by `responsive` (the breakpoint) – not a candidate for bespoke JS. See the anti-pattern below.

## Data-attribute contracts

| Primitive | File | Init selector | Key attributes | Init side-effect |
|---|---|---|---|---|
| collapsible | `00-base/collapsible/collapsible.js` | `[data-collapsible]` | `data-collapsible-trigger`, `data-collapsible-panel`, `data-collapsible-collapsed` (start collapsed), `data-collapsible-duration` (ms, default 500), `data-collapsible-group` (mutually-exclusive group), `data-collapsible-group-enabled-breakpoint` (needs `data-responsive`) | injects `.ct-collapsible__icon` SVG into the trigger; sets `data-collapsible="true"`; flips `aria-expanded`/`aria-hidden` on `transitionend` |
| flyout | `00-base/flyout/flyout.js` | `[data-flyout]` | `data-flyout-open-trigger` (+ `data-flyout-target` selector), `data-flyout-close-trigger`, `data-flyout-close-all-trigger`, `data-flyout-panel`, `data-flyout-expanded`, `data-flyout-duration`, `data-flyout-focus` | sets `data-flyout="true"`; focus-traps Tab within open panels |
| responsive | `00-base/responsive/responsive.js` | `[data-responsive]` (singleton) | `data-responsive="<op><bp>"` e.g. `>=m`, `<s`; operators `< > = >= <= <>`; breakpoints `xxs xs s m l xl xxl` | dispatches a `ct-responsive` window event other behaviours subscribe to |
| scrollspy | `00-base/scrollspy/scrollspy.js` | `[data-scrollspy]` | `data-scrollspy-offset` (px) | adds `.ct-scrollspy-scrolled` past the offset; sets `data-scrollspy="true"` |
| tabs | `02-molecules/tabs/tabs.js` | `.ct-tabs` | `data-tabs-tab` (links), `data-tabs-panel` (panels); selected state via `.ct-tabs__tab--selected` / `.ct-tabs__panel--selected` | flips `aria-selected` / `aria-hidden` |
| tooltip | `02-molecules/tooltip/tooltip.js` | `.ct-tooltip` | `data-tooltip-button`, `data-tooltip-content`, `data-tooltip-arrow`, `data-tooltip-close`, `data-tooltip-position` | sets `data-tooltip="true"`; generates a content id + `aria-describedby`; positions via Popper |
| skip-to-target | `00-base/skip-to-target/skip-to-target.js` | `[data-skip-to-target]` | `href="#id"` pointing at the target | moves focus + scrolls to the target on click |

`collapsible`, `flyout`, `responsive`, `scrollspy` and `skip-to-target` are bundled into `civictheme.base` (imported by `packages/sdc/.storybook/preview.js`) and initialise once at the document level. See `js-patterns.md` for the constructor + `querySelectorAll` shape and for why a *per-component* file does not get the same free initialisation.

## Worked example – the canonical anti-pattern

`04-templates/search-results/search-results.js` hand-rolls a `[data-search-results-filter-toggle]` button that flips `aria-expanded` and a `data-search-results-filter-groups-visible` attribute to show/hide the mobile filter panel. That is exactly what `collapsible` does – and the *same template* already uses `data-collapsible data-collapsible-collapsed data-collapsible-trigger-wide` for its inner filter groups (`search-results.twig`), and `02-molecules/accordion/accordion.twig` uses the same markup verbatim.

The correct fix is to delete the bespoke `search-results.js` and re-author the toggle as a `collapsible` (gated by `responsive` for the breakpoint), not to fortify the bespoke script with a `MutationObserver` or a `Drupal.behaviors` wrapper.

**The gate, every time:** *Does a core CivicTheme behaviour already provide this interaction?* If yes, reuse it and delete the bespoke code. Only when the table genuinely has no match do you author new JS – and then follow `js-patterns.md`.
