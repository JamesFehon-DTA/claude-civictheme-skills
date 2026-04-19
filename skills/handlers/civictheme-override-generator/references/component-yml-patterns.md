# .component.yml Patterns

Detailed schema patterns for CivicTheme SDC `.component.yml` files.

## Full Schema Structure

```yaml
$schema: https://git.drupalcode.org/project/drupal/-/raw/HEAD/core/assets/schemas/v1/metadata.schema.json
name: Human Readable Name
status: stable          # stable | experimental | deprecated
description: Purpose and usage of this component.
replaces: civictheme:name   # OVERRIDE ONLY — omit for new components

props:
  type: object
  required:
    - required_prop_name   # list any required props here
  properties:
    # ... prop definitions

slots:
  slot_name:
    title: Slot Label   # for components that accept rendered markup
```

## SDC and Drupal Loading Behaviour

- Drupal **automatically enqueues the compiled `.css` file** when a component template is rendered via `{% include %}`. No library entry is needed for CSS.
- **JS is never auto-loaded**. Always attach it explicitly via a library (`$variables['#attached']` or globally in `.info.yml`).
- Components without a `.component.yml` are not SDCs — both CSS and JS must be in a library.

## Common Prop Patterns

### Scalars

```yaml
title:
  type: string
  title: Title

count:
  type: integer

is_active:
  type: boolean

weight:
  type: number
```

### Enum with default

```yaml
theme:
  type: string
  enum: [light, dark]

vertical_spacing:
  type: string
  enum: [top, bottom, both, none]

size:
  type: string
  enum: [small, regular, large]
  default: regular
```

### Drupal Attribute object

```yaml
attributes:
  type: Drupal\Core\Template\Attribute
  title: HTML Attributes
```

### Object

```yaml
link:
  type: object
  properties:
    text:
      type: string
    url:
      type: string
    is_new_window:
      type: boolean
    is_external:
      type: boolean
```

### Array of scalars

```yaml
classes:
  type: array
  items:
    type: string
```

### Array of objects

```yaml
items:
  type: array
  items:
    type: object
    properties:
      title:
        type: string
      url:
        type: string
      description:
        type: string
```

### Array of objects with enum and required props

```yaml
columns:
  type: array
  items:
    type: object
    required:
      - label
      - filter_type
    properties:
      label:
        type: string
      filter_type:
        type: string
        enum: [text, select, none]
```

### Union type (object or array)

```yaml
control:
  type: [object, array]
  title: Form control configuration
```

## Slots vs Props

Use **props** for scalar values, objects, and arrays of structured data.

Use **slots** when the content is rendered markup (HTML) that should be injected into a named region of the component — typically in organisms and templates. Slots cannot be validated by JSON Schema since they contain arbitrary markup.

```yaml
slots:
  content:
    title: Main Content
  sidebar:
    title: Sidebar Content
  footer:
    title: Footer Region
```

In Twig, slots are output with `{{ slot_name }}`. Pass slot content from the parent template using the `embed` tag or via Drupal's block system.

## Status Values

- `stable` — production ready; breaking changes must follow semver
- `experimental` — API may change without notice; use with caution
- `deprecated` — scheduled for removal; include a migration note in the description

## Standard Shared Props

Every component should include these unless there is a specific reason not to:

```yaml
theme:
  type: string
  enum: [light, dark]
vertical_spacing:
  type: string
  enum: [top, bottom, both, none]
with_background:
  type: boolean
attributes:
  type: Drupal\Core\Template\Attribute
modifier_class:
  type: string
```

## Override-Specific Notes

When `replaces: civictheme:name` is present:

1. **Copy all base props verbatim first** — then add new ones below
2. **Match existing enum values exactly** — adding new enum values is safe; removing or renaming existing ones breaks data passed from base preprocess hooks
3. **The file path must match** — `components/[level]/[name]/[name].component.yml` — same relative path as the base component
4. **Maintenance obligation** — after each CivicTheme update, compare the base component's `.component.yml` against your override and merge any new or changed props
