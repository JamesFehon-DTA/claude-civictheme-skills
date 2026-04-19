# CivicTheme Field Naming Rules

Field naming for paragraph types in CivicTheme and sub-themes.

## Allowed patterns

### CivicTheme paragraph fields

```
field_c_p_[a-z0-9_]+
```

Used for all fields defined in CivicTheme's `config/install` and referenced in CivicTheme's preprocess hooks. This is CivicTheme's canonical namespace.

### Sub-theme custom fields

```
field_[THEME_MACHINE_NAME]_[a-z0-9_]+
```

Examples:
```
field_agency_promo_summary_rich
field_agency_featured_icon
field_agency_related_links
```

This ensures zero collision risk, clear ownership, and no interference with CivicTheme's own fields.

## Disallowed patterns

| Pattern | Why disallowed |
|---|---|
| `field_c_p_[custom]` | Pollutes CivicTheme's namespace; risks collision on future updates |
| `field_p_[anything]` | Not used anywhere in CivicTheme — not in config, not in preprocess, not in examples |
| Any field not starting with `field_` | Drupal requires the `field_` prefix |

## Linting rules

### CivicTheme paragraph bundles (machine name starts with `civictheme_`)

All fields must match:
```
^field_c_p_[a-z0-9_]+$
```

### Sub-theme paragraph bundles (machine name starts with `[THEME_MACHINE_NAME]_`)

All fields must match:
```
^field_[THEME_MACHINE_NAME]_[a-z0-9_]+$
```

### Mixed bundles (sub-theme extending a CivicTheme paragraph type)

- CivicTheme fields (`field_c_p_*`) — allowed
- Sub-theme fields (`field_[THEME_MACHINE_NAME]_*`) — allowed
- Custom fields using `field_c_p_*` — not allowed

## In preprocess hooks

```php
// Shared CivicTheme field — use the shared helper:
_civictheme_preprocess_paragraph__paragraph_field__title($variables);

// Sub-theme custom field — map directly:
$variables['my_prop'] = civictheme_get_field_value($paragraph, 'field_[THEME_MACHINE_NAME]_my_field');
```

## Why `field_p_` is not valid

`field_p_` does not exist in CivicTheme's codebase — not in config/install, not in any preprocess include, not in any example. Using it produces fields with no recognised convention and no preprocessor support.
