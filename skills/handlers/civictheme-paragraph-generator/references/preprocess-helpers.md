# Preprocess Helpers

How to read fields and related data inside a paragraph preprocess hook. Use CivicTheme's field helper API as the default; use the shared preprocess helpers only when their hardcoded inputs and output keys match what your component needs; fall back to `\Drupal::` for things the helpers don't cover.

All line citations in this document refer to `web/themes/contrib/civictheme/includes/paragraphs.inc` at commit `29fa0fd3271d1e8ef48179f3043385304c699716` of the [CivicTheme monorepo](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/includes/paragraphs.inc). Field getter signatures below are from `includes/utilities.inc` on the same commit. Verify against your installed CivicTheme version before relying on specific line numbers.

## CivicTheme field helper API (preferred)

### `civictheme_get_field_value($entity, $field_name, $only_first = FALSE, $default = NULL, array &$build = [])`

The standard accessor for all CivicTheme entity fields. Handles empty checks and basic entity reference resolution, so callers avoid repetitive null-guarding.

```php
function mytheme_preprocess_paragraph__my_paragraph(array &$variables): void {
  $paragraph = $variables['paragraph'];

  $variables['title'] = civictheme_get_field_value($paragraph, 'field_c_p_title', TRUE);
  $variables['items'] = civictheme_get_field_value($paragraph, 'field_c_p_items', FALSE, [], $variables);

  $variables['content'] = NULL;
}
```

- `$only_first = TRUE` returns the first value only (scalar); `FALSE` (default) returns an array.
- `$default` is returned when the field is empty or missing.
- `$build` — pass `$variables` as a reference to bubble cacheable metadata into the paragraph render array. See "Cacheable metadata" below.

### `civictheme_get_field_referenced_entities($entity, $field_name, array &$build = [])`

Returns referenced entities with access checks applied. Used for paragraph fields that reference other entities (e.g. `field_c_p_list_items`, `field_c_p_reference`). Upstream usage: `manual_list.inc:42`.

```php
$items = civictheme_get_field_referenced_entities($paragraph, 'field_c_p_list_items', $variables);
```

### `civictheme_get_referenced_entity_labels($entity, $field_name, array &$build = [])`

Returns labels for entities referenced from a field (typically taxonomy terms on `field_c_p_topics` or `field_c_n_topics`). Resolves the reference and extracts the human-readable label. Use this for tags/topics props rather than loading the taxonomy terms manually.

### `_civictheme_process__html_content($html, $options = [], $format = NULL)`

Processes formatted-text HTML for component consumption: converts bare URLs to links, applies external-link behaviour from theme settings, and substitutes the contextual theme class (`ct-theme-light` → `ct-theme-dark`, etc.) when `$options['theme']` is provided. Run formatted-text field values through this before handing them to components; raw values from `civictheme_get_field_value()` on a `text_long` field are unprocessed and will not have link behaviour applied.

## Cacheable metadata

CivicTheme manages cacheable metadata at the field-getter level. Per the [1.12.0 manual update instructions](https://docs.civictheme.io/getting-started/civictheme-1.12.0-manual-update-instructions.md): "CivicTheme was not correctly managing cacheable metadata within its preprocess functions. We have updated the CivicTheme API to manage this at the field getter level."

Pass `$variables` (or any render array with a `#cache` key) as the `$build` parameter to any getter that loads referenced entities or applies access checks. Internally the getter uses `CacheableMetadata::createFromRenderArray($build)->applyTo($build)` to bubble referenced-entity cache tags + access-check cacheability into the render array.

- `civictheme_get_field_referenced_entities` and `civictheme_get_referenced_entity_labels` emit a deprecation notice when called without `$build`. Upstream states the parameter will be required in `civictheme:1.13.0` — see [drupal.org/node/3552745](https://www.drupal.org/node/3552745). The failure mode in 1.13.0 is not specified; pass `$variables` now to avoid the deprecation warning and future-proof the call.
- `civictheme_get_field_value` accepts `$build` as the 5th positional argument. Pass `$variables` when the field is an entity reference (the getter resolves references internally).

In addition, attach the paragraph's own cache tags explicitly. Upstream pattern from `manual_list.inc:39`:

```php
$variables['#cache']['tags'] = $paragraph->getCacheTags();
```

For per-row or per-list patterns that merge multiple entities' tags, CivicTheme uses `Cache::mergeTags()` — e.g. `block.inc:157` merges block + node tags.

### What belongs in a paragraph preprocess `#cache`

| Need | Pattern |
|---|---|
| Paragraph's own cacheability | `$variables['#cache']['tags'] = $paragraph->getCacheTags();` |
| Access-checked referenced entities | Pass `$variables` as `$build` to the getter; it handles the rest |
| Output varies by URL path / query | Append `url.path` / `url.query_args:key` to `$variables['#cache']['contexts']` — matches `page.inc:62`, `views.inc:122` |
| Output varies by role | Append `user.roles` (not bare `user` — bare `user` defeats Akamai edge caching) |
| Per-user state (bookmarks, cart count) | Use `#lazy_builder` placeholder instead — keeps the rest of the page cacheable |

### What to avoid

- `$variables['#cache']['max-age'] = 0` in a paragraph preprocess — makes the entire host node page uncacheable at Akamai/Purge. CivicTheme uses `max-age = 0` only in narrow cases (e.g. `banner.inc:94`, scoped to a block rendered without node context).
- Loading entities via `\Drupal::entityTypeManager()` without merging their cache metadata — use `civictheme_get_field_referenced_entities` with `$build` where possible, or manually merge via `CacheableMetadata::createFromObject($entity)->applyTo($variables)`.
- Bare `user` context — use `user.roles` or `user.permissions` unless output is genuinely unique per user.

## Shared paragraph-field preprocess helpers

CivicTheme ships two families of helpers in `paragraphs.inc`, differing by where they read from:

- `paragraph_field__*` — reads a field on the **current paragraph entity**.
- `node_field__*` — reads a field on a **node referenced** from the current paragraph (typically via `field_c_p_reference`). Used by card-shaped paragraphs that display a referenced content item.

**All helpers read from hardcoded field names.** If your sub-theme stores the value in a differently-named field, the helper will not find it — use `civictheme_get_field_value()` directly instead. See "Upstream evolution" at the end of this document.

### `paragraph_field__*` helpers (read from the paragraph)

| Helper suffix     | Reads                          | Writes to `$variables[...]`                            |
| ----------------- | ------------------------------ | ------------------------------------------------------ |
| `background`       | `field_c_p_background`          | `with_background`                                      |
| `column_count`     | `field_c_p_list_column_count`   | `column_count`                                         |
| `content`          | `field_c_p_content`             | `content` — **see warning below**                      |
| `date`             | `field_c_p_date`                | `date`, `date_iso`                                     |
| `date_range`       | `field_c_p_date_range`          | `date`, `date_iso`, `date_end`, `date_end_iso`         |
| `fill_width`       | `field_c_p_list_fill_width`     | `fill_width`                                           |
| `image`            | `field_c_p_image`               | `image` (accepts optional `$image_style` arg)          |
| `image_position`   | `field_c_p_image_position`      | `image_position`                                       |
| `link`             | `field_c_p_link`                | `link`                                                 |
| `link_above`       | `field_c_p_list_link_above`     | `link_above`                                           |
| `link_below`       | `field_c_p_list_link_below`     | `link_below`                                           |
| `links`            | `field_c_p_links`               | `links` (multi-value)                                  |
| `summary`          | `field_c_p_summary`             | `summary` (truncated per theme config)                 |
| `theme`            | `field_c_p_theme`               | `theme`                                                |
| `title`            | `field_c_p_title`               | `title`                                                |
| `topics`           | `field_c_p_topics`              | `tags`                                                 |
| `vertical_spacing` | `field_c_p_vertical_spacing`    | `vertical_spacing`                                     |

### `node_field__*` helpers (read from a referenced node)

Each of these resolves the referenced node from `$variables['node']` if already present, otherwise from `field_c_p_reference` on the paragraph. Fields are read from the **node** using the `field_c_n_*` prefix.

| Helper suffix | Reads on node                                       | Writes to `$variables[...]`                    |
| ------------- | --------------------------------------------------- | ---------------------------------------------- |
| `date`         | (node changed time)                                  | `date`, `date_iso`                             |
| `date_range`   | `field_c_n_date_range`                               | `date`, `date_iso`, `date_end`, `date_end_iso` |
| `image`        | `field_c_n_thumbnail`                                | `image` (accepts optional `$image_style` arg)  |
| `link`         | (node title + URL)                                   | `link`                                         |
| `location`     | `field_c_n_location` → `field_c_p_address`           | `location`                                     |
| `summary`      | `field_c_n_summary` (configurable via `$field_name`) | `summary` (truncated)                          |
| `title`        | (node title)                                         | `title`                                        |
| `topics`       | `field_c_n_topics`                                   | `tags`                                         |

### Warning: do not call `paragraph_field__content`

`_civictheme_preprocess_paragraph__paragraph_field__content()` writes to `$variables['content']`. SKILL.md mandates setting `$variables['content'] = NULL` in every paragraph preprocess hook to suppress Drupal's default field render. These two rules collide — the helper's output is always overwritten, making the call a no-op at best and misleading at worst.

**Use `civictheme_get_field_value()` directly** for body/content fields, mapping the result to whatever prop name your component actually expects:

```php
function mytheme_preprocess_paragraph__my_paragraph(array &$variables): void {
  $paragraph = $variables['paragraph'];

  $variables['title'] = civictheme_get_field_value($paragraph, 'field_c_p_title');
  $variables['body'] = civictheme_get_field_value($paragraph, 'field_c_p_content');

  $variables['content'] = NULL;
}
```

If the field is formatted text (WYSIWYG / `text_long` / `text_with_summary`), wrap the read in `_civictheme_process__html_content()` so URLs are linkified and the contextual theme class is substituted:

```php
$raw = civictheme_get_field_value($paragraph, 'field_c_p_content');
$variables['body'] = $raw ? _civictheme_process__html_content($raw, ['theme' => 'light']) : NULL;
```

### Using the other helpers

When a helper's hardcoded input field and output key both match your needs, calling it is cleaner than rolling your own:

```php
function mytheme_preprocess_paragraph__my_paragraph(array &$variables): void {
  _civictheme_preprocess_paragraph__paragraph_field__title($variables);
  _civictheme_preprocess_paragraph__paragraph_field__summary($variables);

  $variables['content'] = NULL;
}
```

If your component's prop name differs from the helper's output key, either (a) call the helper and remap (`$variables['heading'] = $variables['title']`), or (b) skip the helper and use `civictheme_get_field_value()` directly. Prefer (b) — it keeps the field-to-prop mapping in one place.

## When `\Drupal::` is appropriate (last resort)

Use `\Drupal::` only when the helpers above don't cover the need. All of the following are permitted by the GovCMS SaaS PHPStan config.

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
- **`\Drupal::service('some.service')` for field access** — unnecessary when the helper API covers the case. Reserve service container access for genuinely custom needs.

## Upstream evolution

The hardcoded-input-field limitation is a known upstream constraint. A feature request was raised on 17 February 2026 to add a hook system so sub-themes can override which fields the helpers read from. If that lands, some of the "use `civictheme_get_field_value()` directly" guidance in this document will relax for sub-themes that register their custom fields via the new hook. Until then, the rule stands: the shared helpers only work for sub-themes that use CivicTheme's canonical field names.
