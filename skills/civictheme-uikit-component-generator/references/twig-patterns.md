# Twig Authoring Patterns

Canonical reference: `packages/twig/components/01-atoms/label/label.twig`
Secondary reference: `packages/twig/components/02-molecules/accordion/accordion.twig`

---

## Docblock

Every file opens with a `{# ... #}` docblock. Never use HTML comments (`<!-- -->`).

```twig
{#
/**
 * @file
 * CivicTheme [Component Name] component.
 *
 * Props:
 * - theme: [string] Theme variation (light or dark).
 * - vertical_spacing: [string] Vertical spacing (top, bottom, both, none).
 * - with_background: [boolean] Whether to display with a background.
 * - modifier_class: [string] Additional CSS classes.
 * - attributes: [Drupal\Core\Template\Attribute] Additional HTML attributes.
 *
 * Slots:
 * - content_top: Content above the main body.
 *
 * Blocks:
 * - content_top_block
 * - content_block
 */
#}
```

- List every prop with `[type]` annotation
- Omit Slots / Blocks sections if the component has none
- Array props list their child properties indented under them (see accordion pattern)
- The docblock prop list and the `.component.yml` props must describe the same set

---

## Prop validation and defaults

Validate enumerated props before use. Assign the validated value back to the same variable name.

```twig
{# Enum validation #}
{% set theme = theme in ['light', 'dark'] ? theme : 'light' %}
{% set size = size in ['large', 'regular', 'small'] ? size : 'regular' %}
{% set vertical_spacing = vertical_spacing in ['top', 'bottom', 'both', 'none'] ? vertical_spacing : null %}

{# Boolean default #}
{% set with_background = with_background ?? false %}

{# String default #}
{% set required_text = required_text|default('(required)') %}
```

---

## Class composition

Build all classes before the markup. Use `|format()` throughout — never `~` concatenation.

```twig
{% set theme_class = 'ct-theme-%s'|format(theme) %}
{% set vertical_spacing_class = vertical_spacing ? 'ct-vertical-spacing-inset--%s'|format(vertical_spacing) : '' %}
{% set with_background_class = with_background ? 'ct-[component]--with-background' : '' %}
{% set size_class = 'ct-[component]--%s'|format(size) %}
{% set modifier_class = '%s %s %s %s'|format(theme_class, vertical_spacing_class, with_background_class, modifier_class|default('')) %}
```

- `theme_class` is always first in the modifier string
- `modifier_class|default('')` is always last — it lets callers append extra classes
- Use empty string `''` for conditional classes that are absent, not `null`

---

## Content guard

Wrap all output in a non-empty check on the component's primary prop.

```twig
{% if content is not empty %}
  <div class="ct-[component] {{ modifier_class -}}"
    {%- if attributes is defined and attributes is not null %} {{- attributes -}}{% endif %}>
    {{- content -}}
  </div>
{% endif %}
```

For list components, guard on the list prop:

```twig
{% if items is not empty %}
  ...
{% endif %}
```

---

## Attributes

Always include on the root element. Never omit.

```twig
{% if attributes is defined and attributes is not null %}{{- attributes -}}{% endif %}
```

---

## Including sub-components

Use path-based `@tier/` namespaces — not `civictheme:` namespaces (those are the SDC package convention).

```twig
{% include '@atoms/paragraph/paragraph.twig' with {
  theme: theme,
  content: panel.content,
  modifier_class: 'ct-[component]__inner',
} only %}
```

Tier namespace mapping:
- `01-atoms` → `@atoms/`
- `02-molecules` → `@molecules/`
- `03-organisms` → `@organisms/`
- `04-templates` → `@templates/`

Always pass `only` to prevent variable leakage.

---

## Slots and blocks (molecules/organisms)

Use `{% block %}` wrappers with a conditional inner slot variable. This lets consumers override the entire block or inject slot content.

```twig
{% block content_top_block %}
  {% if content_top is not empty %}
    <div class="ct-[component]__content-top">
      {{- content_top -}}
    </div>
  {% endif %}
{% endblock %}
```

---

## Grid structure (organisms)

Organisms that occupy full-width sections use the standard grid container:

```twig
<div class="container">
  <div class="row">
    <div class="col-xxs-12">
      ...
    </div>
  </div>
</div>
```

Atoms and molecules do not use this wrapper.

---

## Banned patterns

| Pattern | Replace with |
|---|---|
| `<!-- HTML comment -->` | `{# Twig comment #}` |
| `\|raw` filter | Render content directly — `\|raw` removed in UIKit 1.12.2+ |
| `{% extends %}` | Full replacement only — unsupported from 1.11.0 onward |
| `civictheme:label` namespace | `@atoms/label/label.twig` |
| `~` string concatenation | `'%s %s'\|format(a, b)` |
| Hardcoded placeholder text | Twig variables |
