# Preprocess Helpers

How to read fields and related data inside a paragraph preprocess hook. Prefer CivicTheme's field helper API; fall back to `\Drupal::` only for things the helpers don't cover.

## CivicTheme field helper API (preferred)

### `civictheme_get_field_value($entity, $field_name, $multiple = FALSE, $default = NULL)`

The standard accessor for all CivicTheme entity fields. Handles empty checks and basic entity reference resolution, so callers avoid repetitive null-guarding.

```php
function mytheme_preprocess_paragraph__my_paragraph(array &$variables): void {
  $paragraph = $variables['paragraph'];

  $variables['title'] = civictheme_get_field_value($paragraph, 'field_c_p_title');
  $variables['items'] = civictheme_get_field_value($paragraph, 'field_c_p_items', TRUE, []);

  $variables['content'] = NULL;
}
```

- `$multiple = TRUE` returns an array of values for multi-value fields.
- `$default` is returned when the field is empty or missing.

### Shared paragraph-field preprocess helpers

CivicTheme ships preprocess helpers for the standard paragraph fields. Call them from a paragraph preprocess hook to get consistent prop mapping:

- `_civictheme_preprocess_paragraph__paragraph_field__title($variables)` — maps the standard title field to `$variables['title']`.
- `_civictheme_preprocess_paragraph__paragraph_field__content($variables)` — maps the standard body/content field to `$variables['content_items']` (or the equivalent, depending on component).

```php
function mytheme_preprocess_paragraph__my_paragraph(array &$variables): void {
  _civictheme_preprocess_paragraph__paragraph_field__title($variables);
  _civictheme_preprocess_paragraph__paragraph_field__content($variables);

  $variables['content'] = NULL;
}
```

### Rule

Always use CivicTheme helpers for fields on the paragraph entity being preprocessed. Do not use `->get('field_name')->value` directly — it bypasses the abstraction and duplicates null-guards the helpers already provide.

## When `\Drupal::` is appropriate (secondary)

Use `\Drupal::` only when the CivicTheme helpers don't cover the need. All of the following are permitted by the GovCMS SaaS PHPStan config.

- Loading a related entity not already on `$variables`:

  ```php
  $node = \Drupal::entityTypeManager()
    ->getStorage('node')
    ->load($referenced_id);
  ```

- Access-conditional output:

  ```php
  if (\Drupal::currentUser()->hasRole('editor')) {
    $variables['edit_link'] = /* ... */;
  }
  ```

- Token resolution outside Metatag context:

  ```php
  $variables['summary'] = \Drupal::token()
    ->replace('[node:title] — [node:field_summary]', ['node' => $node]);
  ```

## What not to use

- **Direct field access** (`$paragraph->get('field_name')->value`) — bypasses the CivicTheme abstraction. Use `civictheme_get_field_value()` instead.
- **`\Drupal::database()`** — banned by the platform PHPStan config.
- **`\Drupal::service('some.service')` for field access** — unnecessary when the helper API covers the case. Reserve service container access for genuinely custom needs not already wrapped by CivicTheme.
