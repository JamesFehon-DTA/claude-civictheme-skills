# Accessibility Rules for CivicTheme Generators

Authoritative, repo-wide a11y rules for every skill that emits or mutates interactive markup, ARIA attributes, or link semantics. Cited from each generator's SKILL.md; do not duplicate the rule list elsewhere.

All rules here are **enforced at generation** — generators must emit the correct pattern in the first place rather than relying on downstream review.

This is the current curated set. Add new rules here as they are confirmed in practice — pick the next free letter (#D, #E, …) and match the shape of #A–#C. Generators cite by rule letter, so extending this file is cheaper than editing every SKILL.md.

---

## Rule A — never emit `disabled` on `<a>`

`<a>` has no `disabled` attribute. Browsers ignore it: the link remains focusable, follows on Enter/click, and exposes no disabled state to assistive tech. The `:disabled` CSS pseudo-class also does not match, so any visual "disabled" styling keyed on `:disabled` silently no-ops.

The correct disabled-link pattern is three edits in concert:

1. `aria-disabled="true"` — announces the disabled state to assistive tech.
2. `tabindex="-1"` — removes the link from sequential focus order.
3. Omit `href` (or drop it conditionally) — prevents activation.

```twig
{# a11y: disabled-link pattern — aria-disabled + tabindex="-1" + omit href.
   Do NOT emit a `disabled` attribute on <a>. See references/accessibility.md #A. #}
{% if is_disabled %}
  <a class="ct-[name]" aria-disabled="true" tabindex="-1">{{ label }}</a>
{% else %}
  <a class="ct-[name]" href="{{ url }}">{{ label }}</a>
{% endif %}
```

CSS should style the disabled state via `[aria-disabled="true"]`, not `:disabled`:

```scss
.ct-[name][aria-disabled="true"] { opacity: 0.5; pointer-events: none; }
```

This rule does not apply to `<button>` — `<button disabled>` is correct and should keep using the native attribute. The rule is specifically about link-shaped controls.

When toggling disabled-ness in JS, flip all three attributes together:

```js
// a11y: swap aria-disabled, tabindex, and href together. Never touch .disabled on <a>.
link.setAttribute('aria-disabled', 'true');
link.setAttribute('tabindex', '-1');
link.removeAttribute('href');
```

---

## Rule B — new-tab notices must append to the accessible name, not replace it

When a link opens in a new tab or window, sighted users see the link text plus (often) an external-link icon. Non-sighted users need the "opens in a new tab" notice too — but it must **append** to the link's accessible name, not replace it.

The common bug is `aria-label="Opens in a new tab"` on the anchor. `aria-label` overrides the link's accessible name wholesale, so the screen reader announces "Opens in a new tab, link" with no trace of the original label. The user hears the side-channel information and loses the primary information.

The correct pattern is a visually hidden suffix inside the link:

```twig
{# a11y: new-tab notice — append via visually-hidden span. Never use
   aria-label="Opens in a new tab" — it replaces the accessible name.
   See references/accessibility.md #B. #}
<a href="{{ url }}" target="_blank" rel="noopener noreferrer">
  {{ label }}<span class="ct-visually-hidden"> (opens in a new tab)</span>
</a>
```

`ct-visually-hidden` is CivicTheme's standard visually-hidden utility class — it removes the span from visual layout while leaving it in the accessibility tree. The appended text concatenates onto the accessible name, so AT announces "[label], (opens in a new tab), link".

If the caller passes an explicit accessible name override (rare, audited), use `aria-label` that includes both pieces: `aria-label="{{ label }} (opens in a new tab)"`. The banned pattern is the notice-only label that drops the original text.

---

## Rule C — decorative icon spans need `aria-hidden="true"`

Icons inside CivicTheme components fall into two categories:

- **Decorative** — paired with a visible text label; the icon adds no information a screen-reader user would miss. Example: a chevron next to "Learn more", a magnifier inside a button labelled "Search".
- **Meaningful** — the icon IS the label; there is no accompanying text. Example: a standalone icon-only close button.

Decorative icons must be hidden from assistive tech so they are not announced alongside the label. Without `aria-hidden="true"`, the rendered SVG's `<title>` and `<desc>` (or the icon's text content) get announced, producing duplicate or nonsense output like "chevron-right, Learn more".

```twig
{# a11y: decorative icons need aria-hidden="true" to avoid double-announcement.
   See references/accessibility.md #C. #}
<span class="ct-[name]__icon" aria-hidden="true">
  {% include 'civictheme:icon' with { symbol: icon_name, size: 'small' } only %}
</span>
```

Meaningful icons (icon-only controls) must NOT have `aria-hidden="true"`. Instead give the surrounding control an accessible name via visually-hidden text or `aria-label`:

```twig
<button type="button" class="ct-[name]__close">
  <span class="ct-visually-hidden">Close</span>
  {# icon stays announceable via its title, OR wrap in aria-hidden span if the
     visually-hidden text above is the intended accessible name. #}
  <span aria-hidden="true">{% include 'civictheme:icon' with { symbol: 'close' } only %}</span>
</button>
```

The heuristic: if a text label sits next to the icon in the same control, the icon is decorative — hide it. If the icon stands alone, add text via `ct-visually-hidden` or `aria-label` and hide the icon so the announcement is the text, not the icon's own metadata.

---

## How generators apply these rules

Each generator's SKILL.md cites this file from the **Reference files** section and carries inline comments in its sample skeletons. Inline comments are the primary channel — agents copying from code blocks pick up the pattern without needing to re-read this file. The prose section and citation are belt-and-suspenders.

Future a11y rules are added here, not re-stated per skill. Keep each rule self-contained and labelled (#A, #B, #C, #D…) so inline comments can reference them by anchor.
