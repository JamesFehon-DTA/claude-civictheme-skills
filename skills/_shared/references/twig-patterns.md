# Twig Template Patterns

CivicTheme Twig conventions for component and paragraph templates.

## File Header

Every `.twig` file starts with a documentation block listing all props:

```twig
{#
/**
 * @file
 * [Name] component.
 *
 * Props:
 * - theme: [string] 'light' or 'dark'. Default: 'light'.
 * - vertical_spacing: [string] 'top', 'bottom', 'both', or 'none'.
 * - with_background: [boolean] Whether to apply a background.
 * - title: [string] Optional heading text.
 * - items: [array] List of item objects.
 *   - title: [string] Item title.
 *   - url: [string] Item URL.
 * - modifier_class: [string] Additional CSS classes.
 * - attributes: [Drupal\Core\Template\Attribute] HTML attributes.
 */
#}
```

## Prop Validation

Validate enum props at the top — fall back to a safe default if an invalid value is passed. Drupal validates against the schema, but Twig validation defends against edge cases in Storybook and direct includes:

```twig
{% set theme = theme in ['light', 'dark'] ? theme : 'light' %}
{% set vertical_spacing = vertical_spacing in ['top', 'bottom', 'both', 'none'] ? vertical_spacing : null %}
{% set size = size in ['small', 'regular', 'large'] ? size : 'regular' %}
```

## Class Construction

Build the full BEM modifier class string before the root element:

```twig
{% set theme_class = 'ct-theme-%s'|format(theme) %}
{% set spacing_class = vertical_spacing ? 'ct-vertical-spacing-inset--%s'|format(vertical_spacing) : '' %}
{% set background_class = with_background ? 'ct-has-background' : '' %}
{% set modifier_class = '%s %s %s %s'|format(theme_class, spacing_class, background_class, modifier_class|default('')) %}

<div class="ct-[name] {{ modifier_class|trim }}"{{ attributes }}>
```

## The `only` Keyword — Why It Matters

**Always use `with { ... } only` when including child components.**

Without `only`, Drupal passes every variable in the current template scope into the child component — including internal render array variables (`content`, `elements`, `node`, etc.). This can overwrite the child's expected props with Drupal internals, causing silent rendering errors that are hard to trace.

```twig
{# Correct — scoped include #}
{% include 'civictheme:heading' with {
  content: title,
  level: 2,
  theme: theme,
} only %}

{# Wrong — Drupal internals leak into civictheme:heading's scope #}
{% include 'civictheme:heading' with {
  content: title,
} %}
```

## Common CivicTheme Component Includes

```twig
{# Heading #}
{% include 'civictheme:heading' with {
  content: title,
  level: 2,
  theme: theme,
} only %}

{# Button #}
{% include 'civictheme:button' with {
  text: link.text,
  url: link.url,
  type: 'primary',
  theme: theme,
  is_new_window: link.is_new_window,
  is_external: link.is_external,
} only %}

{# Icon #}
{% include 'civictheme:icon' with {
  symbol: icon_name,
  size: 'small',
} only %}

{# Tag #}
{% include 'civictheme:tag' with {
  content: tag.text,
  url: tag.url,
  theme: theme,
} only %}
```

## Conditional Rendering

```twig
{% if title %}
  {% include 'civictheme:heading' with { content: title, level: 2, theme: theme } only %}
{% endif %}

{% if items %}
  <ul class="ct-[name]__list">
    {% for item in items %}
      <li class="ct-[name]__item">{{ item.title }}</li>
    {% endfor %}
  </ul>
{% endif %}
```

## Extensibility Blocks

Wrap key regions in Twig blocks so child templates can override them:

```twig
{% block content_block %}
  <div class="ct-[name]__content">
    {{ content }}
  </div>
{% endblock %}
```

## Paragraph Template Pattern

Paragraph templates are thin connectors — all data transformation happens in the PHP preprocess hook, not in Twig:

```twig
{# templates/paragraph--[name].html.twig #}
{% include '[THEME_MACHINE_NAME]:[component-name]' with {
  theme: theme,
  title: title,
  vertical_spacing: vertical_spacing,
  with_background: with_background,
  attributes: attributes,
  my_prop: my_prop,
} only %}
```

## ARIA and Accessibility

```twig
{# aria-live region for dynamic content updates #}
<div aria-live="polite" aria-atomic="true" class="ct-visually-hidden" role="status">
  {{ results_count }}
</div>

{# Toggleable section #}
<button type="button"
  class="ct-[name]__toggle"
  aria-expanded="{{ is_open ? 'true' : 'false' }}"
  aria-controls="{{ target_id }}">
  {{ label }}
</button>

{# Landmark with labelled heading #}
<section aria-labelledby="[name]-heading-{{ loop.index }}">
  <h2 id="[name]-heading-{{ loop.index }}">{{ title }}</h2>
</section>
```

## `data-` Attribute Selectors for JS

JS selects elements via `data-` attributes — not classes or IDs. This decouples JS from HTML structure so markup can change without breaking behaviour:

```twig
<div class="ct-[name]"
  data-[name]
  data-[name]-option="{{ some_value }}">

  <button type="button" data-[name]-trigger>Toggle</button>
  <div data-[name]-target hidden>Content</div>
</div>
```

Corresponding JS:

```js
once('[theme]-[name]', '[data-[name]]', context).forEach(function (el) {
  var trigger = el.querySelector('[data-[name]-trigger]');
  var target  = el.querySelector('[data-[name]-target]');
});
```

## Namespace Quick Reference

| Context | Namespace |
|---|---|
| CivicTheme base components | `civictheme:component-name` |
| New sub-theme components | `[THEME_MACHINE_NAME]:component-name` |
| Sub-theme overrides | `civictheme:component-name` (Drupal routes to the override automatically) |
