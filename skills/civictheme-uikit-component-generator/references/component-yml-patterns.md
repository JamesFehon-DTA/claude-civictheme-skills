# component.yml Patterns

`.component.yml` files live in `packages/sdc/components/` only. They are the authoritative prop schema for the component and, by extension, for the whole UIKit repo — `components:update:sdc` rewrites the SDC twig docblock from this file, and `components:update:twig` propagates the result to `packages/twig/`.

**Do not generate `.component.yml` in `packages/twig/`.** The twig-package docblock is the schema in that package. A second YAML schema would diverge the moment either side is edited.

---

## Schema

```yaml
$schema: https://git.drupalcode.org/project/drupal/-/raw/HEAD/core/assets/schemas/v1/metadata.schema.json
name: Component Name
status: stable
description: One sentence describing what the component does.
props:
  type: object
  properties:
    theme:
      type: string
      enum: [light, dark]
    vertical_spacing:
      type: string
      enum: [top, bottom, both, none]
    with_background:
      type: boolean
    # component-specific props go here
    modifier_class:
      type: string
    attributes:
      type: "Drupal\\Core\\Template\\Attribute"
      title: HTML Attributes
```

Always include `$schema`. The Drupal SDC metadata schema is the same schema the UIKit's validator runs against — `npm run validate` uses it to check enum values and required props. Omitting `$schema` does not break validation but drops editor JSON-schema assistance.

---

## Standard props

Always include unless the component genuinely doesn't support them:

| Prop | Type | Notes |
|---|---|---|
| `theme` | `string` | enum: `[light, dark]` |
| `vertical_spacing` | `string` | enum: `[top, bottom, both, none]` — omit for atoms that never use spacing |
| `with_background` | `boolean` | omit for atoms |
| `modifier_class` | `string` | always include |
| `attributes` | `Drupal\Core\Template\Attribute` | always include |

---

## Enum values

These enum values are validated by `npm run validate`. Use exactly these values — no others.

| Prop | Valid values |
|---|---|
| `theme` | `light`, `dark` |
| `vertical_spacing` | `top`, `bottom`, `both`, `none` |

---

## Prop types

| Twig type | YAML type |
|---|---|
| string | `string` |
| boolean | `boolean` |
| array of objects | `array` with `items: type: object` |
| Drupal attributes | `Drupal\Core\Template\Attribute` |

For array props, list required child properties:

```yaml
items:
  type: array
  items:
    type: object
    required:
      - title
      - url
    properties:
      title:
        type: string
      url:
        type: string
      is_external:
        type: boolean
```

---

## Slots

Use `slots:` for rendered-markup regions — typically in organisms and templates. Slots cannot be validated by JSON Schema, so they live alongside `props:` at the top level of the file.

```yaml
slots:
  content_top:
    title: Content Above Main Body
  content:
    title: Main Content
```

In Twig, slots are output with `{{ slot_name }}` and usually wrapped in a `{% block %}` so consumers can override either the full block or just the inner slot.

---

## Keeping docblock and .component.yml in sync

The SDC `.component.yml` is the source of truth. The flow is:

1. You edit `packages/sdc/components/.../[name].component.yml`.
2. `npm run components:update:sdc` rewrites the SDC twig docblock to match.
3. `npm run components:update:twig` regenerates `packages/twig/components/.../[name].twig` with the same docblock and `@tier/` namespaces.

When the generator emits both packages in one pass, the SDC docblock and `.component.yml` must already match — otherwise the first `components:update:sdc` run will produce a confusing diff. The `twig-patterns.md` docblock format is the shared contract: generate the SDC twig docblock from the same prop list that went into the YAML.
