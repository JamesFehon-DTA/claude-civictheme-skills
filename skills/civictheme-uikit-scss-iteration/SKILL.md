---
name: civictheme-uikit-scss-iteration
description: Iterate on the SCSS of an existing component in a CivicTheme UIKit, design system, design library, or component library repo — NOT a Drupal sub-theme, and NOT for creating new components. Covers the scope decision between parent-scoped overrides and direct sub-component edits, the `dist:sdc` → `components:update` → `dist:twig` sync-build loop, and flex-layout diagnostics via `preview_eval`. Use when the user wants to tweak spacing, colour, typography, flex/grid layout, or selector-scoped overrides on an existing UIKit component. Triggers for "adjust spacing on the [component]", "fix the [component] layout", "change the [component] colours", "override the [component] styles in [parent]", "the flex row is wrapping", or any SCSS modification to an existing `packages/sdc/components/` file. For authoring a new UIKit component, use `civictheme-uikit-component-generator` instead.
---

# CivicTheme UIKit SCSS Iteration

Modify the SCSS of an existing component in a CivicTheme UIKit, design system, design library, or component library repo. This is the iteration skill — not the authoring skill. Use `civictheme-uikit-component-generator` to create new components.

This skill targets the **UIKit authoring source** only. For SCSS work inside a Drupal sub-theme, route through `civictheme-component-type-selector` instead.

## Authoring model — SDC-first, twig-package is a derivative

`packages/sdc/` is the source of truth. SCSS edits go there, and **only there**. The canonical flow is one-directional:

```
packages/sdc/ ──(components:update:twig)──▶ packages/twig/
```

There is no reverse path. `components:update:twig` copies `.scss` from SDC into the twig package, overwriting whatever sits there. **Any hand-edit to `packages/twig/components/[tier]/[name]/[name].scss` is wiped on the next sync.** If the diff you are iterating on touches the twig-package copy, you are editing the wrong file — stop, move the change to `packages/sdc/`, and re-run the sync loop.

The same rule applies to `packages/sdc/components/variables.components.scss`: edit the SDC copy; the twig-package copy is regenerated. Never write to `00-base/_variables.components.scss` (upstream base content).

## Required inputs

- `[COMPONENT_NAME]` — kebab-case name of the existing component, e.g. `summary-list`
- `[ATOMIC_TIER]` — one of `01-atoms`, `02-molecules`, `03-organisms`, `04-templates`
- `[CIVICTHEME_VERSION]` — UIKit version; default `1.12.2` if unknown
- The file under edit — confirm it is `packages/sdc/components/[tier]/[name]/[name].scss`, not the twig-package sibling

Before editing, confirm the target file exists at `packages/sdc/components/[ATOMIC_TIER]/[COMPONENT_NAME]/[COMPONENT_NAME].scss`. If it does not, the component needs to be scaffolded first — redirect to `civictheme-uikit-component-generator`.

## Reference files

Read before editing:

- `references/scss-patterns.md` — design-system mixins, `ct-component-theme` / `ct-component-property` shapes, geometry tokens, banned patterns, and the three gotchas most likely to bite during iteration (contextual override scoping, `<fieldset>` min-width, `flex: 1 1 0` over `1 1 auto`). This is the core of the skill — read first.
- `references/js-patterns.md` — read when the component uses the collapsible primitive. The `display: block !important` pitfall is SCSS-side and silently breaks JS-driven open/close state. Iteration often introduces this by accident while "forcing" a layout.
- `references/accessibility.md` — read before touching focus styles, `:hover`/`:focus-visible`, or `[aria-disabled]` / `[aria-expanded]` selectors. SCSS iteration is a common source of focus-style regressions; rule #A explicitly requires styling disabled-link state via `[aria-disabled="true"]`, not `:disabled`.
- `references/toolchain.md` — canonical sync loop and the SDC maintainer iteration loop (`dist:sdc` → `components:update` → `dist:twig`). Husky behaviour and the `components:check` contract. Symlinked from `civictheme-uikit-component-generator`, which owns the authoritative copy — iteration reads the same file the authoring skill does so the two skills cannot drift.

`twig-patterns.md` is deliberately **not** cited here. Pure SCSS iteration does not change the markup or include chain; if an edit needs to touch a `.twig` file, it is no longer iteration — re-scope to an override (Drupal sub-theme) or a full re-author (UIKit). The one exception is needing to trace which parent template includes a sub-component in order to decide scoping — use `grep` rather than pulling in the full twig reference.

## Scope decision — parent-scoped override vs sub-component edit

When an existing sub-component looks wrong only inside a specific parent (e.g. a `button` renders differently when embedded in a `summary-list__row`), there are two places the SCSS change can live. The criterion is whether the change **generalises**:

| Change generalises across every use of the sub-component | Put it in the sub-component's own SCSS |
|---|---|
| e.g. a spacing fix the sub-component should have had from day one | `packages/sdc/components/[tier]/[sub]/[sub].scss` |
| Change only applies inside this one parent context | Put it in the parent's SCSS, scoped under the parent selector |
| e.g. summary-list's row makes the button denser; no other button context wants that | `packages/sdc/components/[tier]/[parent]/[parent].scss` → `.ct-[parent] .ct-[sub] { ... }` |

The test is not "can this go in the parent?" — almost anything can be scoped under a parent selector. The test is "would every other call site of the sub-component also want this?" If yes, it is a sub-component edit. If no, it is a parent-scoped override. Getting this wrong in either direction produces different kinds of debt: globalising a context-specific rule makes the sub-component unpredictable; localising a genuinely-universal rule duplicates the fix every time a new parent embeds the sub-component.

Two secondary constraints:

- **Theme-sensitive properties** (colour, background-color, border-color, anything going through `ct-component-property`) must live inside a `ct-component-theme($root) using($root, $theme)` block on the selector that owns the element. A parent-scoped override of a sub-component's colour goes inside the **parent's** theme block, not as a bare `.ct-[parent] .ct-[sub] { color: ... }` rule. See `references/scss-patterns.md` → Theme rules.
- **Layout and geometry** (border-width, border-radius, padding, margin, flex, grid, width/height) stay outside `ct-component-theme`. Keeping the theme block to theme-variant properties keeps it small and auditable.

See `references/scss-patterns.md` → Contextual override scoping for the three-way split (selector-scoped restyling / theme properties / geometry) that follows once the above decision is made.

## Sync-build loop — `dist:sdc` → `components:update` → `dist:twig`

Every SCSS edit goes through this loop before the Storybook preview reflects it. Treat it as a first-class workflow step, not a post-hoc "oh, and then rebuild":

| # | Command | Why it runs here |
|---|---|---|
| 1 | `npm run dist:sdc` | Compile SCSS → CSS for the SDC workspace only. Fast; surfaces SCSS syntax errors and mixin-resolution failures immediately. |
| 2 | `npm run components:update` | Runs `components:update:sdc` (regenerates SDC twig docblocks) then `components:update:twig` (copies SDC → twig package, including the `.scss` you just edited). This is the step that propagates the change to the twig package. |
| 3 | `npm run dist:twig` | Compile SCSS → CSS for the twig workspace, producing the files Storybook serves. Storybook HMR does not reliably pick up cross-package SCSS changes, so this is what actually refreshes the preview. |

Skipping any step silently breaks iteration:

- Skip `dist:sdc` → syntax errors surface only after the full `components:update`, muddling the diagnostic.
- Skip `components:update` → SDC is correct, twig package is stale, Storybook serves the old CSS.
- Skip `dist:twig` → twig-package `.scss` is up to date but its compiled `.css` is not, so Storybook still renders the old styles.

The full `components:update:sdc` → `components:update:twig` → `validate` sequence from `references/toolchain.md` is the **pre-commit contract**; the three-step loop above is the **iteration loop** and is what you run after every SCSS edit. Do not skip directly to the pre-commit contract during iteration — `validate` is wasted work while a change is still in flux, and the full `components:update` without the surrounding `dist:*` steps does not refresh the compiled CSS Storybook serves.

Pre-commit, Husky runs `components:check` (asserts `packages/twig/` is a byte-accurate derivative of `packages/sdc/`) plus lint and tests. See `references/toolchain.md` → Pre-commit hooks.

## Flex-layout diagnostics via `preview_eval`

When a flex row wraps unexpectedly, overflows its container, or a child consumes more space than its siblings, the fastest diagnostic is reading the actual computed box metrics of each flex child from the live Storybook preview. `preview_eval` executes JavaScript in the running preview's document context and returns the result.

**Prerequisite: a running Storybook preview.** `preview_eval` is a no-op without one. Start the preview first:

```sh
npm run dev:twig   # starts the Storybook dev server for the twig package
```

Once the dev server is up, the preview-MCP flow is: `preview_start` (connect to the running server) → navigate to the story under investigation → `preview_eval`. The specific MCP invocation and URL structure are the preview tooling's concern, not this skill's — this skill only specifies what to evaluate and how to read the result. If the preview tooling is unfamiliar, defer to whatever `preview-start` documentation the host environment provides.

The three metrics that diagnose wrapping and space-consumption bugs:

- `offsetWidth` — the rendered pixel width of the child. Compare against the container's content-box width to see how much space each child actually takes.
- `offsetLeft` — the child's x-offset from its offset parent. A flex child whose `offsetLeft` exceeds the container's content-box width has wrapped to the next line.
- `offsetTop` — the child's y-offset from its offset parent. If two siblings in a single-row flex container have different `offsetTop` values, one has wrapped.

Example evaluation (run via `preview_eval` against the story URL):

```js
// Read per-child metrics for a flex row. Adjust the selector to the component under diagnosis.
Array.from(document.querySelectorAll('.ct-[component]__row > *')).map((el, i) => ({
  index: i,
  tag: el.tagName.toLowerCase(),
  classes: el.className,
  offsetWidth: el.offsetWidth,
  offsetLeft: el.offsetLeft,
  offsetTop: el.offsetTop,
  // Computed flex values — useful when the bug is "this child is wider than I expected"
  flex: getComputedStyle(el).flex,
}));
```

What to look for in the returned array:

| Symptom | What to read from the metrics |
|---|---|
| Flex row wraps on desktop but should stay on one line | Any child's `offsetTop` differs from its siblings' — that child has wrapped |
| One child "eats" too much space | Compare `offsetWidth` values against each child's `flex` computed value; a `flex: 1 1 auto` child will size to content, which may be wider than you expect — switch to `flex: 1 1 0` (see `references/scss-patterns.md`) |
| Layout breaks inside a `<fieldset>` | Inspect the fieldset's `offsetWidth` against its parent; `<fieldset>` has an implicit `min-width: min-content` that ignores flex-basis. Add `min-width: 0` (see `references/scss-patterns.md`) |
| Sibling-order drift at a breakpoint | Run the evaluation at the target viewport width — Storybook's "desktop" preset can resolve below the `l` breakpoint. Set the viewport explicitly; see `references/toolchain.md` → Storybook viewport presets |

Read the metrics **before** changing the SCSS. A diagnostic run narrows the suspect set; guessing at a fix and re-running the preview without metrics turns iteration into trial and error.

## Out of scope

- **New components.** Use `civictheme-uikit-component-generator`.
- **Drupal sub-theme SCSS.** Route through `civictheme-component-type-selector` — the Drupal-side skills handle `.info.yml`, libraries, and sub-theme variable overrides, which do not exist in a UIKit repo.
- **Portable / self-contained components** — own CSS token namespace (`--[prefix]-*`), hardcoded fallbacks, multi-site portability. These live in Drupal themes under their own SDC namespace, not `packages/sdc/`. Out of scope for every UIKit skill.
- **Twig markup changes.** If the iteration needs to rename a class, add a BEM child, or change an include chain, it is no longer pure SCSS iteration — re-scope the task.
- **Creating new `--ct-[component]-*` custom properties.** Iteration may reference existing geometry tokens but must not invent new ones inline (see `references/scss-patterns.md` → Component geometry tokens). A new token belongs in the variables layer and is authoring work, not iteration.

## Output contract

```yaml
component_path_sdc: packages/sdc/components/[tier]/[name]/
edit_target: packages/sdc/components/[tier]/[name]/[name].scss
change_kind: <sub_component_edit | parent_scoped_override | variables_only>
scope_rationale: <one sentence explaining why this change generalises or is context-specific>
files:
  - path: packages/sdc/components/[tier]/[name]/[name].scss
    purpose: SCSS edit to the sub-component's own file (sub_component_edit) OR parent file with scoped override block (parent_scoped_override)
    # Do NOT also write packages/twig/components/[tier]/[name]/[name].scss — the twig package is a generated derivative of SDC, and components:update:twig will overwrite any hand-written copy.
    diff: |
      <unified diff or full replacement contents>
  - path: packages/sdc/components/variables.components.scss  # only when change_kind == variables_only or when adding a variable alongside an SCSS edit
    purpose: variable block for any new ct-component-property calls introduced by this edit
    # Do NOT also write packages/twig/components/variables.components.scss — regenerated by components:update:twig.
    diff: |
      <appended block or unified diff>
post_iteration_notes:
  - Run npm run dist:sdc to compile SDC SCSS and surface syntax errors.
  - Run npm run components:update to regenerate SDC docblocks and copy SDC → twig package.
  - Run npm run dist:twig to compile twig-package SCSS into the CSS Storybook serves.
  - If a flex-layout diagnostic is needed, start Storybook with npm run dev:twig, then use preview_eval to read offsetWidth/offsetLeft/offsetTop on the flex children before changing the SCSS further.
  - Before committing, run the full pre-commit contract: npm run components:update && npm run validate && npm run lint. Husky will fail the commit if packages/twig/ does not match what components:update:twig would produce from current SDC source.
```
