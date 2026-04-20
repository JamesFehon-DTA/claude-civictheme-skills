# CivicTheme field storage reference

Authoritative storage metadata for every canonical CivicTheme field (`field_c_p_*` paragraph fields and `field_c_n_*` node fields): storage type, cardinality, max length, HTML support, and bundle attachments.

Skills consult this file to warn authors when the backing storage contradicts a component prop's expectation (e.g. a card summary prop accepts HTML, but the field storing the summary is `string_long` — plain text only).

## Pinned commit

All citations below point at commit [`29fa0fd3271d1e8ef48179f3043385304c699716`](https://github.com/civictheme/monorepo-drupal/tree/29fa0fd3271d1e8ef48179f3043385304c699716) of the [CivicTheme monorepo](https://github.com/civictheme/monorepo-drupal), under `web/themes/contrib/civictheme/config/install/`. The same commit pins the other references in this skills package (e.g. [`civictheme-paragraph-generator/references/preprocess-helpers.md`](../../civictheme-paragraph-generator/references/preprocess-helpers.md)). Verify against your installed CivicTheme version before relying on specific line numbers.

## How to refresh for a new CivicTheme release

When CivicTheme is bumped in the consuming project:

1. Pick the new target commit (tag or SHA) on `civictheme/monorepo-drupal`.
2. Update the pinned commit in the "Pinned commit" section above and in the per-row GitHub URLs. The rows are generated from:
   - every `field.storage.<entity>.<field_name>.yml` in [`web/themes/contrib/civictheme/config/install/`](https://github.com/civictheme/monorepo-drupal/tree/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install) where `field_name` starts with `field_c_p_` or `field_c_n_` — supplies machine name, storage type, cardinality, and storage-level settings.
   - every `field.field.<entity>.<bundle>.<field_name>.yml` for the same fields — supplies `bundle`, `required`, `label`, `allowed_formats`, and `handler_settings.target_bundles`.
3. A quick way to regenerate the tables is to walk those YAML files with any YAML parser and reproduce the shape below. If you script it, pin the `type:` and `required:` line numbers for each file so the deep links stay useful — offsets shift when `dependencies:` lists grow or shrink.
4. Diff the rebuilt tables against this file and commit the changes together with any skills that need to cite new or renamed fields.

## Reading this reference

- **Storage type** is whatever the field-storage YAML declares at `type:` — matches Drupal's field type plugin ID (`string`, `string_long`, `text_long`, `entity_reference`, `entity_reference_revisions`, `link`, `datetime`, `daterange`, `boolean`, `integer`, `list_string`, `list_integer`, `webform`).
- **Cardinality**: `1` = single-value, `-1` = unlimited, `n` = exactly n.
- **Max length** only applies to `string` (bounded VARCHAR, `max_length` setting) and `string_long`/`text_long` (unbounded TEXT column). Other storages are not character-limited at this layer.
- **HTML support** is the property authors get wrong most often:
  - `text_long` / `text_with_summary` — formatted text backed by a text format filter chain. The rendered output may contain HTML depending on the chosen format. Use CivicTheme's `_civictheme_process__html_content()` helper before passing to a component that expects HTML.
  - `string` / `string_long` — plain text. **No text format, no filters.** Any HTML typed into the field is stored and emitted verbatim; Twig's default auto-escaping then renders it as visible markup characters (`&lt;strong&gt;` not `<strong>`). Do **not** pass these through `|raw` to "enable HTML" — the storage layer does no sanitisation, so raw-rendering opens XSS. If a component prop needs HTML, the field must be `text_long`.
  - `link` — the value is a `uri` + `title` pair; the formatter (not the storage) decides how it renders. Passing the raw `uri` into an HTML prop never produces the link markup on its own.
  - Everything else — scalar values (booleans, lists, dates) or resolved references (entity_reference, image, webform). They render via their own formatter and HTML is not part of the data contract.
- **`allowed_formats: {}`** on a bundle's `field.field.*.yml` means "no restriction" — the editor sees every text format their role has permission to use. A non-empty list restricts the dropdown. CivicTheme's install config uses the empty form everywhere today.

## Storage-vs-prop mismatches to watch for

Common traps skills should surface when generating or overriding:

- **Summary fields are not rich text.** `field_c_p_summary` and `field_c_n_summary` are both `string_long`. Card components whose `summary` prop accepts HTML (e.g. `civictheme_promo_card`, `civictheme_publication_card`, `civictheme_snippet`) will render escaped tag characters if an author pastes HTML into the summary. Either keep the prop plain, or author the summary in `text_long` via a custom sub-theme field.
- **`field_c_p_url` is `string_long`, not `link`.** Any helper that calls link-formatting APIs on it will fail or coerce incorrectly. The field stores a raw URI string; preprocess code must build its own URL object before handing it to a component prop that expects a link.
- **Single vs multi matters.** `field_c_p_links`, `field_c_p_attachments`, `field_c_p_document`, `field_c_p_topics`, `field_c_p_list_filters_exp`, `field_c_p_list_items`, `field_c_p_list_site_sections`, `field_c_p_list_topics`, `field_c_p_panels`, `field_c_p_slides`, `field_c_n_attachments`, `field_c_n_banner_components`, `field_c_n_banner_components_bott`, `field_c_n_components`, `field_c_n_location`, and `field_c_n_topics` have cardinality `-1`. `civictheme_get_field_value()` must be called with `$multiple = TRUE` for these or only the first value is returned.
- **Title fields cap at 255 characters.** `field_c_p_title`, `field_c_p_subtitle`, `field_c_p_link_text`, `field_c_p_address`, `field_c_p_height`, `field_c_p_width`, `field_c_p_location`, and `field_c_n_banner_title` are all `string` with `max_length: 255`. A prop like `title` that truncates or wraps needs to account for the storage limit — component validation won't catch an over-long server-side string, because nothing over-long can exist.
- **Banner title shares storage with page titles only conceptually.** `field_c_n_banner_title` is a distinct field; the node's main title comes from the node entity's built-in `title` base field and is not listed here.
- **`field_c_p_reference` is a `node` reference, not a paragraph reference.** It drives the `*_ref` card variants (`civictheme_event_card_ref`, `civictheme_navigation_card_ref`, etc.) which re-render a referenced content item as a card. `field_c_p_cards`, `field_c_p_panels`, `field_c_p_slides`, and `field_c_p_list_items` are `entity_reference_revisions` to paragraphs.

## Fields

The quick-reference tables give one row per field (storage type, cardinality, max length, HTML support). The per-field details sections add bundle attachments — which paragraph types or content types the field is attached to, whether it is required there, and any target-bundle / format restrictions recorded on the `field.field.*.yml`.

### Paragraph fields — quick reference (`field_c_p_*`)

| Field | Storage type | Cardinality | Max length | HTML | Storage source |
|---|---|---|---|---|---|
| `field_c_p_address` | `string` | `1` | 255 | No (plain text, HTML escaped) | [`field.storage.paragraph.field_c_p_address.yml:9`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_address.yml#L9) |
| `field_c_p_attachments` | `entity_reference` | `-1` | — | n/a (resolved render array) | [`field.storage.paragraph.field_c_p_attachments.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_attachments.yml#L10) |
| `field_c_p_background` | `boolean` | `1` | — | n/a | [`field.storage.paragraph.field_c_p_background.yml:9`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_background.yml#L9) |
| `field_c_p_cards` | `entity_reference_revisions` | `-1` | — | n/a (resolved render array) | [`field.storage.paragraph.field_c_p_cards.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_cards.yml#L10) |
| `field_c_p_content` | `text_long` | `1` | unlimited (TEXT column) | Yes (via text format) | [`field.storage.paragraph.field_c_p_content.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_content.yml#L10) |
| `field_c_p_date` | `datetime` | `1` | — | n/a | [`field.storage.paragraph.field_c_p_date.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_date.yml#L10) |
| `field_c_p_date_range` | `daterange` | `1` | — | n/a | [`field.storage.paragraph.field_c_p_date_range.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_date_range.yml#L10) |
| `field_c_p_default_panel` | `list_integer` | `1` | — | n/a | [`field.storage.paragraph.field_c_p_default_panel.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_default_panel.yml#L10) |
| `field_c_p_document` | `entity_reference` | `-1` | — | n/a (resolved render array) | [`field.storage.paragraph.field_c_p_document.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_document.yml#L10) |
| `field_c_p_embed_url` | `link` | `1` | unlimited (uri) | No (URI + title, HTML escaped) | [`field.storage.paragraph.field_c_p_embed_url.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_embed_url.yml#L10) |
| `field_c_p_expand` | `boolean` | `1` | — | n/a | [`field.storage.paragraph.field_c_p_expand.yml:9`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_expand.yml#L9) |
| `field_c_p_footer_link` | `link` | `1` | unlimited (uri) | No (URI + title, HTML escaped) | [`field.storage.paragraph.field_c_p_footer_link.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_footer_link.yml#L10) |
| `field_c_p_header_link` | `link` | `1` | unlimited (uri) | No (URI + title, HTML escaped) | [`field.storage.paragraph.field_c_p_header_link.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_header_link.yml#L10) |
| `field_c_p_height` | `string` | `1` | 255 | No (plain text, HTML escaped) | [`field.storage.paragraph.field_c_p_height.yml:9`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_height.yml#L9) |
| `field_c_p_icon` | `entity_reference` | `1` | — | n/a (resolved render array) | [`field.storage.paragraph.field_c_p_icon.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_icon.yml#L10) |
| `field_c_p_image` | `entity_reference` | `1` | — | n/a (resolved render array) | [`field.storage.paragraph.field_c_p_image.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_image.yml#L10) |
| `field_c_p_image_position` | `list_string` | `1` | — | n/a | [`field.storage.paragraph.field_c_p_image_position.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_image_position.yml#L10) |
| `field_c_p_link` | `link` | `1` | unlimited (uri) | No (URI + title, HTML escaped) | [`field.storage.paragraph.field_c_p_link.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_link.yml#L10) |
| `field_c_p_link_text` | `string` | `1` | 255 | No (plain text, HTML escaped) | [`field.storage.paragraph.field_c_p_link_text.yml:9`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_link_text.yml#L9) |
| `field_c_p_links` | `link` | `-1` | unlimited (uri) | No (URI + title, HTML escaped) | [`field.storage.paragraph.field_c_p_links.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_links.yml#L10) |
| `field_c_p_list_column_count` | `list_integer` | `1` | — | n/a | [`field.storage.paragraph.field_c_p_list_column_count.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_column_count.yml#L10) |
| `field_c_p_list_content_type` | `list_string` | `1` | — | n/a | [`field.storage.paragraph.field_c_p_list_content_type.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_content_type.yml#L10) |
| `field_c_p_list_fill_width` | `boolean` | `1` | — | n/a | [`field.storage.paragraph.field_c_p_list_fill_width.yml:9`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_fill_width.yml#L9) |
| `field_c_p_list_filters_exp` | `list_string` | `-1` | — | n/a | [`field.storage.paragraph.field_c_p_list_filters_exp.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_filters_exp.yml#L10) |
| `field_c_p_list_item_theme` | `list_string` | `1` | — | n/a | [`field.storage.paragraph.field_c_p_list_item_theme.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_item_theme.yml#L10) |
| `field_c_p_list_item_view_as` | `list_string` | `1` | — | n/a | [`field.storage.paragraph.field_c_p_list_item_view_as.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_item_view_as.yml#L10) |
| `field_c_p_list_items` | `entity_reference_revisions` | `-1` | — | n/a (resolved render array) | [`field.storage.paragraph.field_c_p_list_items.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_items.yml#L10) |
| `field_c_p_list_limit` | `integer` | `1` | — | n/a | [`field.storage.paragraph.field_c_p_list_limit.yml:9`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_limit.yml#L9) |
| `field_c_p_list_limit_type` | `list_string` | `1` | — | n/a | [`field.storage.paragraph.field_c_p_list_limit_type.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_limit_type.yml#L10) |
| `field_c_p_list_link_above` | `link` | `1` | unlimited (uri) | No (URI + title, HTML escaped) | [`field.storage.paragraph.field_c_p_list_link_above.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_link_above.yml#L10) |
| `field_c_p_list_link_below` | `link` | `1` | unlimited (uri) | No (URI + title, HTML escaped) | [`field.storage.paragraph.field_c_p_list_link_below.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_link_below.yml#L10) |
| `field_c_p_list_site_sections` | `entity_reference` | `-1` | — | n/a (resolved render array) | [`field.storage.paragraph.field_c_p_list_site_sections.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_site_sections.yml#L10) |
| `field_c_p_list_topics` | `entity_reference` | `-1` | — | n/a (resolved render array) | [`field.storage.paragraph.field_c_p_list_topics.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_topics.yml#L10) |
| `field_c_p_list_type` | `list_string` | `1` | — | n/a | [`field.storage.paragraph.field_c_p_list_type.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_type.yml#L10) |
| `field_c_p_location` | `string` | `1` | 255 | No (plain text, HTML escaped) | [`field.storage.paragraph.field_c_p_location.yml:9`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_location.yml#L9) |
| `field_c_p_message_type` | `list_string` | `1` | — | n/a | [`field.storage.paragraph.field_c_p_message_type.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_message_type.yml#L10) |
| `field_c_p_panels` | `entity_reference_revisions` | `-1` | — | n/a (resolved render array) | [`field.storage.paragraph.field_c_p_panels.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_panels.yml#L10) |
| `field_c_p_reference` | `entity_reference` | `1` | — | n/a (resolved render array) | [`field.storage.paragraph.field_c_p_reference.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_reference.yml#L10) |
| `field_c_p_show_image_as_icon` | `boolean` | `1` | — | n/a | [`field.storage.paragraph.field_c_p_show_image_as_icon.yml:9`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_show_image_as_icon.yml#L9) |
| `field_c_p_slides` | `entity_reference_revisions` | `-1` | — | n/a (resolved render array) | [`field.storage.paragraph.field_c_p_slides.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_slides.yml#L10) |
| `field_c_p_subtitle` | `string` | `1` | 255 | No (plain text, HTML escaped) | [`field.storage.paragraph.field_c_p_subtitle.yml:9`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_subtitle.yml#L9) |
| `field_c_p_summary` | `string_long` | `1` | unlimited (TEXT column) | No (plain text, HTML escaped) | [`field.storage.paragraph.field_c_p_summary.yml:9`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_summary.yml#L9) |
| `field_c_p_theme` | `list_string` | `1` | — | n/a | [`field.storage.paragraph.field_c_p_theme.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_theme.yml#L10) |
| `field_c_p_title` | `string` | `1` | 255 | No (plain text, HTML escaped) | [`field.storage.paragraph.field_c_p_title.yml:9`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_title.yml#L9) |
| `field_c_p_topics` | `entity_reference` | `-1` | — | n/a (resolved render array) | [`field.storage.paragraph.field_c_p_topics.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_topics.yml#L10) |
| `field_c_p_url` | `string_long` | `1` | unlimited (TEXT column) | No (plain text, HTML escaped) | [`field.storage.paragraph.field_c_p_url.yml:9`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_url.yml#L9) |
| `field_c_p_vertical_spacing` | `list_string` | `1` | — | n/a | [`field.storage.paragraph.field_c_p_vertical_spacing.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_vertical_spacing.yml#L10) |
| `field_c_p_view_link` | `link` | `1` | unlimited (uri) | No (URI + title, HTML escaped) | [`field.storage.paragraph.field_c_p_view_link.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_view_link.yml#L10) |
| `field_c_p_webform` | `webform` | `1` | — | n/a (resolved render array) | [`field.storage.paragraph.field_c_p_webform.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_webform.yml#L10) |
| `field_c_p_width` | `string` | `1` | 255 | No (plain text, HTML escaped) | [`field.storage.paragraph.field_c_p_width.yml:9`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_width.yml#L9) |

### Node fields — quick reference (`field_c_n_*`)

| Field | Storage type | Cardinality | Max length | HTML | Storage source |
|---|---|---|---|---|---|
| `field_c_n_alert_page_visibility` | `string_long` | `1` | unlimited (TEXT column) | No (plain text, HTML escaped) | [`field.storage.node.field_c_n_alert_page_visibility.yml:9`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_alert_page_visibility.yml#L9) |
| `field_c_n_alert_type` | `list_string` | `1` | — | n/a | [`field.storage.node.field_c_n_alert_type.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_alert_type.yml#L10) |
| `field_c_n_attachments` | `entity_reference_revisions` | `-1` | — | n/a (resolved render array) | [`field.storage.node.field_c_n_attachments.yml:11`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_attachments.yml#L11) |
| `field_c_n_banner_background` | `entity_reference` | `1` | — | n/a (resolved render array) | [`field.storage.node.field_c_n_banner_background.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_banner_background.yml#L10) |
| `field_c_n_banner_blend_mode` | `list_string` | `1` | — | n/a | [`field.storage.node.field_c_n_banner_blend_mode.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_banner_blend_mode.yml#L10) |
| `field_c_n_banner_components` | `entity_reference_revisions` | `-1` | — | n/a (resolved render array) | [`field.storage.node.field_c_n_banner_components.yml:11`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_banner_components.yml#L11) |
| `field_c_n_banner_components_bott` | `entity_reference_revisions` | `-1` | — | n/a (resolved render array) | [`field.storage.node.field_c_n_banner_components_bott.yml:11`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_banner_components_bott.yml#L11) |
| `field_c_n_banner_featured_image` | `entity_reference` | `1` | — | n/a (resolved render array) | [`field.storage.node.field_c_n_banner_featured_image.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_banner_featured_image.yml#L10) |
| `field_c_n_banner_hide_breadcrumb` | `boolean` | `1` | — | n/a | [`field.storage.node.field_c_n_banner_hide_breadcrumb.yml:9`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_banner_hide_breadcrumb.yml#L9) |
| `field_c_n_banner_theme` | `list_string` | `1` | — | n/a | [`field.storage.node.field_c_n_banner_theme.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_banner_theme.yml#L10) |
| `field_c_n_banner_title` | `string` | `1` | 255 | No (plain text, HTML escaped) | [`field.storage.node.field_c_n_banner_title.yml:9`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_banner_title.yml#L9) |
| `field_c_n_banner_type` | `list_string` | `1` | — | n/a | [`field.storage.node.field_c_n_banner_type.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_banner_type.yml#L10) |
| `field_c_n_body` | `text_long` | `1` | unlimited (TEXT column) | Yes (via text format) | [`field.storage.node.field_c_n_body.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_body.yml#L10) |
| `field_c_n_components` | `entity_reference_revisions` | `-1` | — | n/a (resolved render array) | [`field.storage.node.field_c_n_components.yml:11`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_components.yml#L11) |
| `field_c_n_custom_last_updated` | `datetime` | `1` | — | n/a | [`field.storage.node.field_c_n_custom_last_updated.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_custom_last_updated.yml#L10) |
| `field_c_n_date_range` | `daterange` | `1` | — | n/a | [`field.storage.node.field_c_n_date_range.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_date_range.yml#L10) |
| `field_c_n_hide_sidebar` | `boolean` | `1` | — | n/a | [`field.storage.node.field_c_n_hide_sidebar.yml:9`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_hide_sidebar.yml#L9) |
| `field_c_n_hide_tags` | `boolean` | `1` | — | n/a | [`field.storage.node.field_c_n_hide_tags.yml:9`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_hide_tags.yml#L9) |
| `field_c_n_location` | `entity_reference_revisions` | `-1` | — | n/a (resolved render array) | [`field.storage.node.field_c_n_location.yml:11`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_location.yml#L11) |
| `field_c_n_show_last_updated` | `boolean` | `1` | — | n/a | [`field.storage.node.field_c_n_show_last_updated.yml:9`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_show_last_updated.yml#L9) |
| `field_c_n_show_toc` | `boolean` | `1` | — | n/a | [`field.storage.node.field_c_n_show_toc.yml:9`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_show_toc.yml#L9) |
| `field_c_n_site_section` | `entity_reference` | `1` | — | n/a (resolved render array) | [`field.storage.node.field_c_n_site_section.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_site_section.yml#L10) |
| `field_c_n_summary` | `string_long` | `1` | unlimited (TEXT column) | No (plain text, HTML escaped) | [`field.storage.node.field_c_n_summary.yml:9`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_summary.yml#L9) |
| `field_c_n_thumbnail` | `entity_reference` | `1` | — | n/a (resolved render array) | [`field.storage.node.field_c_n_thumbnail.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_thumbnail.yml#L10) |
| `field_c_n_topics` | `entity_reference` | `-1` | — | n/a (resolved render array) | [`field.storage.node.field_c_n_topics.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_topics.yml#L10) |
| `field_c_n_vertical_spacing` | `list_string` | `1` | — | n/a | [`field.storage.node.field_c_n_vertical_spacing.yml:10`](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_vertical_spacing.yml#L10) |

### Paragraph field details

#### `field_c_p_address`

- **Storage** — type `string`, cardinality `1`, max_length `255` — [field.storage.paragraph.field_c_p_address.yml#L9](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_address.yml#L9)
- **Bundle attachments:**
  - `civictheme_map` — label `Address` — required — [field.field.paragraph.civictheme_map.field_c_p_address.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_map.field_c_p_address.yml#L13)

#### `field_c_p_attachments`

- **Storage** — type `entity_reference`, cardinality `-1`, `target_type: media` — [field.storage.paragraph.field_c_p_attachments.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_attachments.yml#L10)
- **Bundle attachments:**
  - `civictheme_attachment` — label `Attachments` — required — targets: `civictheme_document` — [field.field.paragraph.civictheme_attachment.field_c_p_attachments.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_attachment.field_c_p_attachments.yml#L14)

#### `field_c_p_background`

- **Storage** — type `boolean`, cardinality `1` — [field.storage.paragraph.field_c_p_background.yml#L9](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_background.yml#L9)
- **Bundle attachments:**
  - `civictheme_accordion` — label `Background` — optional — [field.field.paragraph.civictheme_accordion.field_c_p_background.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_accordion.field_c_p_background.yml#L13)
  - `civictheme_attachment` — label `Background` — optional — [field.field.paragraph.civictheme_attachment.field_c_p_background.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_attachment.field_c_p_background.yml#L13)
  - `civictheme_automated_list` — label `Background` — optional — [field.field.paragraph.civictheme_automated_list.field_c_p_background.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_automated_list.field_c_p_background.yml#L13)
  - `civictheme_content` — label `Background` — optional — [field.field.paragraph.civictheme_content.field_c_p_background.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_content.field_c_p_background.yml#L13)
  - `civictheme_iframe` — label `Background` — optional — [field.field.paragraph.civictheme_iframe.field_c_p_background.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_iframe.field_c_p_background.yml#L13)
  - `civictheme_manual_list` — label `Background` — optional — [field.field.paragraph.civictheme_manual_list.field_c_p_background.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_manual_list.field_c_p_background.yml#L13)
  - `civictheme_map` — label `Background` — optional — [field.field.paragraph.civictheme_map.field_c_p_background.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_map.field_c_p_background.yml#L13)
  - `civictheme_message` — label `Background` — optional — [field.field.paragraph.civictheme_message.field_c_p_background.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_message.field_c_p_background.yml#L13)
  - `civictheme_promo` — label `Background` — optional — [field.field.paragraph.civictheme_promo.field_c_p_background.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_promo.field_c_p_background.yml#L13)
  - `civictheme_slider` — label `Background` — optional — [field.field.paragraph.civictheme_slider.field_c_p_background.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_slider.field_c_p_background.yml#L13)
  - `civictheme_webform` — label `Background` — optional — [field.field.paragraph.civictheme_webform.field_c_p_background.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_webform.field_c_p_background.yml#L13)

#### `field_c_p_cards`

- **Storage** — type `entity_reference_revisions`, cardinality `-1`, `target_type: paragraph` — [field.storage.paragraph.field_c_p_cards.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_cards.yml#L10)
- **Bundle attachments** — none in base CivicTheme install config. (Storage declared, no `field.field.*.yml` attaches it to a bundle — this field is either unused or attached by other configuration outside `config/install`.)

#### `field_c_p_content`

- **Storage** — type `text_long`, cardinality `1` — [field.storage.paragraph.field_c_p_content.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_content.yml#L10)
- **Bundle attachments:**
  - `civictheme_accordion_panel` — label `Content` — required — `allowed_formats: {}` — any enabled format — [field.field.paragraph.civictheme_accordion_panel.field_c_p_content.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_accordion_panel.field_c_p_content.yml#L15)
  - `civictheme_attachment` — label `Content` — optional — `allowed_formats: {}` — any enabled format — [field.field.paragraph.civictheme_attachment.field_c_p_content.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_attachment.field_c_p_content.yml#L15)
  - `civictheme_automated_list` — label `Content` — optional — `allowed_formats: {}` — any enabled format — [field.field.paragraph.civictheme_automated_list.field_c_p_content.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_automated_list.field_c_p_content.yml#L15)
  - `civictheme_callout` — label `Content` — required — `allowed_formats: {}` — any enabled format — [field.field.paragraph.civictheme_callout.field_c_p_content.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_callout.field_c_p_content.yml#L15)
  - `civictheme_campaign` — label `Content` — optional — `allowed_formats: {}` — any enabled format — [field.field.paragraph.civictheme_campaign.field_c_p_content.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_campaign.field_c_p_content.yml#L15)
  - `civictheme_content` — label `Content` — optional — `allowed_formats: {}` — any enabled format — [field.field.paragraph.civictheme_content.field_c_p_content.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_content.field_c_p_content.yml#L15)
  - `civictheme_manual_list` — label `Content` — optional — `allowed_formats: {}` — any enabled format — [field.field.paragraph.civictheme_manual_list.field_c_p_content.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_manual_list.field_c_p_content.yml#L15)
  - `civictheme_message` — label `Content` — optional — `allowed_formats: {}` — any enabled format — [field.field.paragraph.civictheme_message.field_c_p_content.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_message.field_c_p_content.yml#L15)
  - `civictheme_next_step` — label `Content` — optional — `allowed_formats: {}` — any enabled format — [field.field.paragraph.civictheme_next_step.field_c_p_content.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_next_step.field_c_p_content.yml#L15)
  - `civictheme_promo` — label `Content` — optional — `allowed_formats: {}` — any enabled format — [field.field.paragraph.civictheme_promo.field_c_p_content.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_promo.field_c_p_content.yml#L15)
  - `civictheme_slider_slide` — label `Content` — optional — `allowed_formats: {}` — any enabled format — [field.field.paragraph.civictheme_slider_slide.field_c_p_content.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_slider_slide.field_c_p_content.yml#L15)

#### `field_c_p_date`

- **Storage** — type `datetime`, cardinality `1`, `datetime_type: date` — [field.storage.paragraph.field_c_p_date.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_date.yml#L10)
- **Bundle attachments:**
  - `civictheme_campaign` — label `Date` — optional — [field.field.paragraph.civictheme_campaign.field_c_p_date.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_campaign.field_c_p_date.yml#L15)
  - `civictheme_slider_slide` — label `Date` — optional — [field.field.paragraph.civictheme_slider_slide.field_c_p_date.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_slider_slide.field_c_p_date.yml#L15)

#### `field_c_p_date_range`

- **Storage** — type `daterange`, cardinality `1`, `datetime_type: datetime` — [field.storage.paragraph.field_c_p_date_range.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_date_range.yml#L10)
- **Bundle attachments:**
  - `civictheme_event_card` — label `Date` — optional — [field.field.paragraph.civictheme_event_card.field_c_p_date_range.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_event_card.field_c_p_date_range.yml#L15)

#### `field_c_p_default_panel`

- **Storage** — type `list_integer`, cardinality `1`, allowed values: `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10` — [field.storage.paragraph.field_c_p_default_panel.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_default_panel.yml#L10)
- **Bundle attachments** — none in base CivicTheme install config. (Storage declared, no `field.field.*.yml` attaches it to a bundle — this field is either unused or attached by other configuration outside `config/install`.)

#### `field_c_p_document`

- **Storage** — type `entity_reference`, cardinality `-1`, `target_type: media` — [field.storage.paragraph.field_c_p_document.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_document.yml#L10)
- **Bundle attachments:**
  - `civictheme_publication_card` — label `Document` — required — targets: `civictheme_document` — [field.field.paragraph.civictheme_publication_card.field_c_p_document.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_publication_card.field_c_p_document.yml#L14)

#### `field_c_p_embed_url`

- **Storage** — type `link`, cardinality `1` — [field.storage.paragraph.field_c_p_embed_url.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_embed_url.yml#L10)
- **Bundle attachments:**
  - `civictheme_map` — label `Embed URL` — required — [field.field.paragraph.civictheme_map.field_c_p_embed_url.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_map.field_c_p_embed_url.yml#L15)

#### `field_c_p_expand`

- **Storage** — type `boolean`, cardinality `1` — [field.storage.paragraph.field_c_p_expand.yml#L9](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_expand.yml#L9)
- **Bundle attachments:**
  - `civictheme_accordion` — label `Expand all` — optional — [field.field.paragraph.civictheme_accordion.field_c_p_expand.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_accordion.field_c_p_expand.yml#L13)
  - `civictheme_accordion_panel` — label `Expanded` — optional — [field.field.paragraph.civictheme_accordion_panel.field_c_p_expand.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_accordion_panel.field_c_p_expand.yml#L13)

#### `field_c_p_footer_link`

- **Storage** — type `link`, cardinality `1` — [field.storage.paragraph.field_c_p_footer_link.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_footer_link.yml#L10)
- **Bundle attachments** — none in base CivicTheme install config. (Storage declared, no `field.field.*.yml` attaches it to a bundle — this field is either unused or attached by other configuration outside `config/install`.)

#### `field_c_p_header_link`

- **Storage** — type `link`, cardinality `1` — [field.storage.paragraph.field_c_p_header_link.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_header_link.yml#L10)
- **Bundle attachments** — none in base CivicTheme install config. (Storage declared, no `field.field.*.yml` attaches it to a bundle — this field is either unused or attached by other configuration outside `config/install`.)

#### `field_c_p_height`

- **Storage** — type `string`, cardinality `1`, max_length `255` — [field.storage.paragraph.field_c_p_height.yml#L9](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_height.yml#L9)
- **Bundle attachments:**
  - `civictheme_iframe` — label `Height` — optional — [field.field.paragraph.civictheme_iframe.field_c_p_height.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_iframe.field_c_p_height.yml#L13)

#### `field_c_p_icon`

- **Storage** — type `entity_reference`, cardinality `1`, `target_type: media` — [field.storage.paragraph.field_c_p_icon.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_icon.yml#L10)
- **Bundle attachments:**
  - `civictheme_social_icon` — label `Icon` — required — targets: `civictheme_icon` — [field.field.paragraph.civictheme_social_icon.field_c_p_icon.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_social_icon.field_c_p_icon.yml#L14)

#### `field_c_p_image`

- **Storage** — type `entity_reference`, cardinality `1`, `target_type: media` — [field.storage.paragraph.field_c_p_image.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_image.yml#L10)
- **Bundle attachments:**
  - `civictheme_campaign` — label `Image` — required — targets: `civictheme_image` — [field.field.paragraph.civictheme_campaign.field_c_p_image.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_campaign.field_c_p_image.yml#L14)
  - `civictheme_event_card` — label `Image` — optional — targets: `civictheme_image` — [field.field.paragraph.civictheme_event_card.field_c_p_image.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_event_card.field_c_p_image.yml#L14)
  - `civictheme_navigation_card` — label `Image` — optional — targets: `civictheme_icon`, `civictheme_image` — [field.field.paragraph.civictheme_navigation_card.field_c_p_image.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_navigation_card.field_c_p_image.yml#L15)
  - `civictheme_promo_card` — label `Image` — optional — targets: `civictheme_image` — [field.field.paragraph.civictheme_promo_card.field_c_p_image.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_promo_card.field_c_p_image.yml#L14)
  - `civictheme_publication_card` — label `Image` — optional — targets: `civictheme_image` — [field.field.paragraph.civictheme_publication_card.field_c_p_image.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_publication_card.field_c_p_image.yml#L14)
  - `civictheme_slider_slide` — label `Image` — optional — targets: `civictheme_image` — [field.field.paragraph.civictheme_slider_slide.field_c_p_image.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_slider_slide.field_c_p_image.yml#L14)
  - `civictheme_subject_card` — label `Image` — optional — targets: `civictheme_image` — [field.field.paragraph.civictheme_subject_card.field_c_p_image.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_subject_card.field_c_p_image.yml#L14)

#### `field_c_p_image_position`

- **Storage** — type `list_string`, cardinality `1`, allowed values: `left`, `right` — [field.storage.paragraph.field_c_p_image_position.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_image_position.yml#L10)
- **Bundle attachments:**
  - `civictheme_campaign` — label `Image position` — required — [field.field.paragraph.civictheme_campaign.field_c_p_image_position.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_campaign.field_c_p_image_position.yml#L15)
  - `civictheme_slider_slide` — label `Image position` — required — [field.field.paragraph.civictheme_slider_slide.field_c_p_image_position.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_slider_slide.field_c_p_image_position.yml#L15)
  - `civictheme_slider_slide_ref` — label `Image position` — required — [field.field.paragraph.civictheme_slider_slide_ref.field_c_p_image_position.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_slider_slide_ref.field_c_p_image_position.yml#L15)

#### `field_c_p_link`

- **Storage** — type `link`, cardinality `1` — [field.storage.paragraph.field_c_p_link.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_link.yml#L10)
- **Bundle attachments:**
  - `civictheme_event_card` — label `Link` — optional — [field.field.paragraph.civictheme_event_card.field_c_p_link.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_event_card.field_c_p_link.yml#L15)
  - `civictheme_navigation_card` — label `Link` — optional — [field.field.paragraph.civictheme_navigation_card.field_c_p_link.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_navigation_card.field_c_p_link.yml#L15)
  - `civictheme_next_step` — label `Link` — optional — [field.field.paragraph.civictheme_next_step.field_c_p_link.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_next_step.field_c_p_link.yml#L15)
  - `civictheme_promo` — label `Link` — required — [field.field.paragraph.civictheme_promo.field_c_p_link.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_promo.field_c_p_link.yml#L15)
  - `civictheme_promo_card` — label `Link` — optional — [field.field.paragraph.civictheme_promo_card.field_c_p_link.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_promo_card.field_c_p_link.yml#L15)
  - `civictheme_snippet` — label `Link` — optional — [field.field.paragraph.civictheme_snippet.field_c_p_link.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_snippet.field_c_p_link.yml#L15)
  - `civictheme_social_icon` — label `Link` — required — [field.field.paragraph.civictheme_social_icon.field_c_p_link.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_social_icon.field_c_p_link.yml#L15)
  - `civictheme_subject_card` — label `Link` — required — [field.field.paragraph.civictheme_subject_card.field_c_p_link.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_subject_card.field_c_p_link.yml#L15)

#### `field_c_p_link_text`

- **Storage** — type `string`, cardinality `1`, max_length `255` — [field.storage.paragraph.field_c_p_link_text.yml#L9](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_link_text.yml#L9)
- **Bundle attachments:**
  - `civictheme_slider_slide_ref` — label `Link text` — optional — [field.field.paragraph.civictheme_slider_slide_ref.field_c_p_link_text.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_slider_slide_ref.field_c_p_link_text.yml#L13)

#### `field_c_p_links`

- **Storage** — type `link`, cardinality `-1` — [field.storage.paragraph.field_c_p_links.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_links.yml#L10)
- **Bundle attachments:**
  - `civictheme_callout` — label `Links` — required — [field.field.paragraph.civictheme_callout.field_c_p_links.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_callout.field_c_p_links.yml#L15)
  - `civictheme_campaign` — label `Links` — optional — [field.field.paragraph.civictheme_campaign.field_c_p_links.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_campaign.field_c_p_links.yml#L15)
  - `civictheme_service_card` — label `Links` — required — [field.field.paragraph.civictheme_service_card.field_c_p_links.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_service_card.field_c_p_links.yml#L15)
  - `civictheme_slider_slide` — label `Links` — optional — [field.field.paragraph.civictheme_slider_slide.field_c_p_links.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_slider_slide.field_c_p_links.yml#L15)

#### `field_c_p_list_column_count`

- **Storage** — type `list_integer`, cardinality `1`, allowed values: `1`, `2`, `3`, `4` — [field.storage.paragraph.field_c_p_list_column_count.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_column_count.yml#L10)
- **Bundle attachments:**
  - `civictheme_automated_list` — label `Column count` — required — [field.field.paragraph.civictheme_automated_list.field_c_p_list_column_count.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_automated_list.field_c_p_list_column_count.yml#L15)
  - `civictheme_manual_list` — label `Column count` — required — [field.field.paragraph.civictheme_manual_list.field_c_p_list_column_count.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_manual_list.field_c_p_list_column_count.yml#L15)

#### `field_c_p_list_content_type`

- **Storage** — type `list_string`, cardinality `1`, allowed values: `all`, `civictheme_page`, `civictheme_event` — [field.storage.paragraph.field_c_p_list_content_type.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_content_type.yml#L10)
- **Bundle attachments:**
  - `civictheme_automated_list` — label `Content type` — required — [field.field.paragraph.civictheme_automated_list.field_c_p_list_content_type.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_automated_list.field_c_p_list_content_type.yml#L15)

#### `field_c_p_list_fill_width`

- **Storage** — type `boolean`, cardinality `1` — [field.storage.paragraph.field_c_p_list_fill_width.yml#L9](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_fill_width.yml#L9)
- **Bundle attachments:**
  - `civictheme_automated_list` — label `Fill width in the last row` — optional — [field.field.paragraph.civictheme_automated_list.field_c_p_list_fill_width.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_automated_list.field_c_p_list_fill_width.yml#L13)
  - `civictheme_manual_list` — label `Fill width in the last row` — optional — [field.field.paragraph.civictheme_manual_list.field_c_p_list_fill_width.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_manual_list.field_c_p_list_fill_width.yml#L13)

#### `field_c_p_list_filters_exp`

- **Storage** — type `list_string`, cardinality `-1`, allowed values: `type`, `topic`, `title` — [field.storage.paragraph.field_c_p_list_filters_exp.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_filters_exp.yml#L10)
- **Bundle attachments:**
  - `civictheme_automated_list` — label `Exposed filters` — optional — [field.field.paragraph.civictheme_automated_list.field_c_p_list_filters_exp.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_automated_list.field_c_p_list_filters_exp.yml#L15)

#### `field_c_p_list_item_theme`

- **Storage** — type `list_string`, cardinality `1`, allowed values: `light`, `dark` — [field.storage.paragraph.field_c_p_list_item_theme.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_item_theme.yml#L10)
- **Bundle attachments:**
  - `civictheme_automated_list` — label `Item theme` — required — [field.field.paragraph.civictheme_automated_list.field_c_p_list_item_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_automated_list.field_c_p_list_item_theme.yml#L15)

#### `field_c_p_list_item_view_as`

- **Storage** — type `list_string`, cardinality `1`, allowed values: `civictheme_promo_card`, `civictheme_navigation_card`, `civictheme_snippet` — [field.storage.paragraph.field_c_p_list_item_view_as.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_item_view_as.yml#L10)
- **Bundle attachments:**
  - `civictheme_automated_list` — label `Display items as` — required — [field.field.paragraph.civictheme_automated_list.field_c_p_list_item_view_as.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_automated_list.field_c_p_list_item_view_as.yml#L15)

#### `field_c_p_list_items`

- **Storage** — type `entity_reference_revisions`, cardinality `-1`, `target_type: paragraph` — [field.storage.paragraph.field_c_p_list_items.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_items.yml#L10)
- **Bundle attachments:**
  - `civictheme_manual_list` — label `List items` — required — targets: `civictheme_event_card`, `civictheme_event_card_ref`, `civictheme_navigation_card`, `civictheme_navigation_card_ref`, `civictheme_promo_card`, `civictheme_promo_card_ref`, `civictheme_publication_card`, `civictheme_service_card`, `civictheme_snippet`, `civictheme_snippet_ref`, `civictheme_subject_card`, `civictheme_subject_card_ref` — [field.field.paragraph.civictheme_manual_list.field_c_p_list_items.yml#L27](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_manual_list.field_c_p_list_items.yml#L27)

#### `field_c_p_list_limit`

- **Storage** — type `integer`, cardinality `1` — [field.storage.paragraph.field_c_p_list_limit.yml#L9](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_limit.yml#L9)
- **Bundle attachments:**
  - `civictheme_automated_list` — label `Limit` — required — [field.field.paragraph.civictheme_automated_list.field_c_p_list_limit.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_automated_list.field_c_p_list_limit.yml#L13)

#### `field_c_p_list_limit_type`

- **Storage** — type `list_string`, cardinality `1`, allowed values: `limited`, `unlimited` — [field.storage.paragraph.field_c_p_list_limit_type.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_limit_type.yml#L10)
- **Bundle attachments:**
  - `civictheme_automated_list` — label `Limit type` — required — [field.field.paragraph.civictheme_automated_list.field_c_p_list_limit_type.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_automated_list.field_c_p_list_limit_type.yml#L15)

#### `field_c_p_list_link_above`

- **Storage** — type `link`, cardinality `1` — [field.storage.paragraph.field_c_p_list_link_above.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_link_above.yml#L10)
- **Bundle attachments:**
  - `civictheme_automated_list` — label `Link above` — optional — [field.field.paragraph.civictheme_automated_list.field_c_p_list_link_above.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_automated_list.field_c_p_list_link_above.yml#L15)
  - `civictheme_manual_list` — label `Link above` — optional — [field.field.paragraph.civictheme_manual_list.field_c_p_list_link_above.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_manual_list.field_c_p_list_link_above.yml#L15)

#### `field_c_p_list_link_below`

- **Storage** — type `link`, cardinality `1` — [field.storage.paragraph.field_c_p_list_link_below.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_link_below.yml#L10)
- **Bundle attachments:**
  - `civictheme_automated_list` — label `Link below` — optional — [field.field.paragraph.civictheme_automated_list.field_c_p_list_link_below.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_automated_list.field_c_p_list_link_below.yml#L15)
  - `civictheme_manual_list` — label `Link below` — optional — [field.field.paragraph.civictheme_manual_list.field_c_p_list_link_below.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_manual_list.field_c_p_list_link_below.yml#L15)

#### `field_c_p_list_site_sections`

- **Storage** — type `entity_reference`, cardinality `-1`, `target_type: taxonomy_term` — [field.storage.paragraph.field_c_p_list_site_sections.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_site_sections.yml#L10)
- **Bundle attachments:**
  - `civictheme_automated_list` — label `Site sections` — optional — targets: `civictheme_site_sections` — [field.field.paragraph.civictheme_automated_list.field_c_p_list_site_sections.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_automated_list.field_c_p_list_site_sections.yml#L14)

#### `field_c_p_list_topics`

- **Storage** — type `entity_reference`, cardinality `-1`, `target_type: taxonomy_term` — [field.storage.paragraph.field_c_p_list_topics.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_topics.yml#L10)
- **Bundle attachments:**
  - `civictheme_automated_list` — label `Topics` — optional — targets: `civictheme_topics` — [field.field.paragraph.civictheme_automated_list.field_c_p_list_topics.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_automated_list.field_c_p_list_topics.yml#L14)

#### `field_c_p_list_type`

- **Storage** — type `list_string`, cardinality `1`, allowed values: `civictheme_automated_list__block1` — [field.storage.paragraph.field_c_p_list_type.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_list_type.yml#L10)
- **Bundle attachments:**
  - `civictheme_automated_list` — label `List type` — required — [field.field.paragraph.civictheme_automated_list.field_c_p_list_type.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_automated_list.field_c_p_list_type.yml#L15)

#### `field_c_p_location`

- **Storage** — type `string`, cardinality `1`, max_length `255` — [field.storage.paragraph.field_c_p_location.yml#L9](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_location.yml#L9)
- **Bundle attachments:**
  - `civictheme_event_card` — label `Location` — optional — [field.field.paragraph.civictheme_event_card.field_c_p_location.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_event_card.field_c_p_location.yml#L13)

#### `field_c_p_message_type`

- **Storage** — type `list_string`, cardinality `1`, allowed values: `information`, `warning`, `error`, `success` — [field.storage.paragraph.field_c_p_message_type.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_message_type.yml#L10)
- **Bundle attachments:**
  - `civictheme_message` — label `Type` — required — [field.field.paragraph.civictheme_message.field_c_p_message_type.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_message.field_c_p_message_type.yml#L15)

#### `field_c_p_panels`

- **Storage** — type `entity_reference_revisions`, cardinality `-1`, `target_type: paragraph` — [field.storage.paragraph.field_c_p_panels.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_panels.yml#L10)
- **Bundle attachments:**
  - `civictheme_accordion` — label `Panels` — required — targets: `civictheme_accordion_panel` — [field.field.paragraph.civictheme_accordion.field_c_p_panels.yml#L16](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_accordion.field_c_p_panels.yml#L16)

#### `field_c_p_reference`

- **Storage** — type `entity_reference`, cardinality `1`, `target_type: node` — [field.storage.paragraph.field_c_p_reference.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_reference.yml#L10)
- **Bundle attachments:**
  - `civictheme_event_card_ref` — label `Reference` — required — targets: `civictheme_event` — [field.field.paragraph.civictheme_event_card_ref.field_c_p_reference.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_event_card_ref.field_c_p_reference.yml#L14)
  - `civictheme_navigation_card_ref` — label `Reference` — required — targets: `civictheme_event`, `civictheme_page` — [field.field.paragraph.civictheme_navigation_card_ref.field_c_p_reference.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_navigation_card_ref.field_c_p_reference.yml#L15)
  - `civictheme_promo_card_ref` — label `Reference` — required — targets: `civictheme_event`, `civictheme_page` — [field.field.paragraph.civictheme_promo_card_ref.field_c_p_reference.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_promo_card_ref.field_c_p_reference.yml#L15)
  - `civictheme_slider_slide_ref` — label `Reference` — required — targets: `civictheme_event`, `civictheme_page` — [field.field.paragraph.civictheme_slider_slide_ref.field_c_p_reference.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_slider_slide_ref.field_c_p_reference.yml#L15)
  - `civictheme_snippet_ref` — label `Reference` — required — targets: `civictheme_event`, `civictheme_page` — [field.field.paragraph.civictheme_snippet_ref.field_c_p_reference.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_snippet_ref.field_c_p_reference.yml#L15)
  - `civictheme_subject_card_ref` — label `Reference` — required — targets: `civictheme_event`, `civictheme_page` — [field.field.paragraph.civictheme_subject_card_ref.field_c_p_reference.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_subject_card_ref.field_c_p_reference.yml#L15)

#### `field_c_p_show_image_as_icon`

- **Storage** — type `boolean`, cardinality `1` — [field.storage.paragraph.field_c_p_show_image_as_icon.yml#L9](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_show_image_as_icon.yml#L9)
- **Bundle attachments:**
  - `civictheme_navigation_card` — label `Show image as icon` — optional — [field.field.paragraph.civictheme_navigation_card.field_c_p_show_image_as_icon.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_navigation_card.field_c_p_show_image_as_icon.yml#L13)

#### `field_c_p_slides`

- **Storage** — type `entity_reference_revisions`, cardinality `-1`, `target_type: paragraph` — [field.storage.paragraph.field_c_p_slides.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_slides.yml#L10)
- **Bundle attachments:**
  - `civictheme_slider` — label `Slides` — required — targets: `civictheme_slider_slide`, `civictheme_slider_slide_ref` — [field.field.paragraph.civictheme_slider.field_c_p_slides.yml#L17](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_slider.field_c_p_slides.yml#L17)

#### `field_c_p_subtitle`

- **Storage** — type `string`, cardinality `1`, max_length `255` — [field.storage.paragraph.field_c_p_subtitle.yml#L9](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_subtitle.yml#L9)
- **Bundle attachments:**
  - `civictheme_promo_card` — label `Subtitle` — optional — [field.field.paragraph.civictheme_promo_card.field_c_p_subtitle.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_promo_card.field_c_p_subtitle.yml#L13)

#### `field_c_p_summary`

- **Storage** — type `string_long`, cardinality `1` — [field.storage.paragraph.field_c_p_summary.yml#L9](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_summary.yml#L9)
- **Bundle attachments:**
  - `civictheme_event_card` — label `Summary` — optional — [field.field.paragraph.civictheme_event_card.field_c_p_summary.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_event_card.field_c_p_summary.yml#L13)
  - `civictheme_navigation_card` — label `Summary` — optional — [field.field.paragraph.civictheme_navigation_card.field_c_p_summary.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_navigation_card.field_c_p_summary.yml#L13)
  - `civictheme_promo_card` — label `Summary` — optional — [field.field.paragraph.civictheme_promo_card.field_c_p_summary.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_promo_card.field_c_p_summary.yml#L13)
  - `civictheme_publication_card` — label `Summary` — optional — [field.field.paragraph.civictheme_publication_card.field_c_p_summary.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_publication_card.field_c_p_summary.yml#L13)
  - `civictheme_snippet` — label `Summary` — optional — [field.field.paragraph.civictheme_snippet.field_c_p_summary.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_snippet.field_c_p_summary.yml#L13)

#### `field_c_p_theme`

- **Storage** — type `list_string`, cardinality `1`, allowed values: `light`, `dark` — [field.storage.paragraph.field_c_p_theme.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_theme.yml#L10)
- **Bundle attachments:**
  - `civictheme_accordion` — label `Theme` — required — [field.field.paragraph.civictheme_accordion.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_accordion.field_c_p_theme.yml#L15)
  - `civictheme_attachment` — label `Theme` — required — [field.field.paragraph.civictheme_attachment.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_attachment.field_c_p_theme.yml#L15)
  - `civictheme_automated_list` — label `Theme` — required — [field.field.paragraph.civictheme_automated_list.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_automated_list.field_c_p_theme.yml#L15)
  - `civictheme_callout` — label `Theme` — required — [field.field.paragraph.civictheme_callout.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_callout.field_c_p_theme.yml#L15)
  - `civictheme_campaign` — label `Theme` — required — [field.field.paragraph.civictheme_campaign.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_campaign.field_c_p_theme.yml#L15)
  - `civictheme_content` — label `Theme` — required — [field.field.paragraph.civictheme_content.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_content.field_c_p_theme.yml#L15)
  - `civictheme_event_card` — label `Theme` — required — [field.field.paragraph.civictheme_event_card.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_event_card.field_c_p_theme.yml#L15)
  - `civictheme_event_card_ref` — label `Theme` — required — [field.field.paragraph.civictheme_event_card_ref.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_event_card_ref.field_c_p_theme.yml#L15)
  - `civictheme_iframe` — label `Theme` — required — [field.field.paragraph.civictheme_iframe.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_iframe.field_c_p_theme.yml#L15)
  - `civictheme_manual_list` — label `Theme` — required — [field.field.paragraph.civictheme_manual_list.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_manual_list.field_c_p_theme.yml#L15)
  - `civictheme_map` — label `Theme` — required — [field.field.paragraph.civictheme_map.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_map.field_c_p_theme.yml#L15)
  - `civictheme_message` — label `Theme` — required — [field.field.paragraph.civictheme_message.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_message.field_c_p_theme.yml#L15)
  - `civictheme_navigation_card` — label `Theme` — required — [field.field.paragraph.civictheme_navigation_card.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_navigation_card.field_c_p_theme.yml#L15)
  - `civictheme_navigation_card_ref` — label `Theme` — required — [field.field.paragraph.civictheme_navigation_card_ref.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_navigation_card_ref.field_c_p_theme.yml#L15)
  - `civictheme_next_step` — label `Theme` — required — [field.field.paragraph.civictheme_next_step.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_next_step.field_c_p_theme.yml#L15)
  - `civictheme_promo` — label `Theme` — required — [field.field.paragraph.civictheme_promo.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_promo.field_c_p_theme.yml#L15)
  - `civictheme_promo_card` — label `Theme` — required — [field.field.paragraph.civictheme_promo_card.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_promo_card.field_c_p_theme.yml#L15)
  - `civictheme_promo_card_ref` — label `Theme` — required — [field.field.paragraph.civictheme_promo_card_ref.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_promo_card_ref.field_c_p_theme.yml#L15)
  - `civictheme_publication_card` — label `Theme` — required — [field.field.paragraph.civictheme_publication_card.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_publication_card.field_c_p_theme.yml#L15)
  - `civictheme_service_card` — label `Theme` — required — [field.field.paragraph.civictheme_service_card.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_service_card.field_c_p_theme.yml#L15)
  - `civictheme_slider` — label `Theme` — required — [field.field.paragraph.civictheme_slider.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_slider.field_c_p_theme.yml#L15)
  - `civictheme_slider_slide` — label `Theme` — required — [field.field.paragraph.civictheme_slider_slide.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_slider_slide.field_c_p_theme.yml#L15)
  - `civictheme_slider_slide_ref` — label `Theme` — required — [field.field.paragraph.civictheme_slider_slide_ref.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_slider_slide_ref.field_c_p_theme.yml#L15)
  - `civictheme_snippet` — label `Theme` — required — [field.field.paragraph.civictheme_snippet.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_snippet.field_c_p_theme.yml#L15)
  - `civictheme_snippet_ref` — label `Theme` — required — [field.field.paragraph.civictheme_snippet_ref.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_snippet_ref.field_c_p_theme.yml#L15)
  - `civictheme_subject_card` — label `Theme` — required — [field.field.paragraph.civictheme_subject_card.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_subject_card.field_c_p_theme.yml#L15)
  - `civictheme_subject_card_ref` — label `Theme` — required — [field.field.paragraph.civictheme_subject_card_ref.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_subject_card_ref.field_c_p_theme.yml#L15)
  - `civictheme_webform` — label `Theme` — required — [field.field.paragraph.civictheme_webform.field_c_p_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_webform.field_c_p_theme.yml#L15)

#### `field_c_p_title`

- **Storage** — type `string`, cardinality `1`, max_length `255` — [field.storage.paragraph.field_c_p_title.yml#L9](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_title.yml#L9)
- **Bundle attachments:**
  - `civictheme_accordion_panel` — label `Title` — required — [field.field.paragraph.civictheme_accordion_panel.field_c_p_title.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_accordion_panel.field_c_p_title.yml#L13)
  - `civictheme_attachment` — label `Title` — required — [field.field.paragraph.civictheme_attachment.field_c_p_title.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_attachment.field_c_p_title.yml#L13)
  - `civictheme_automated_list` — label `Title` — optional — [field.field.paragraph.civictheme_automated_list.field_c_p_title.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_automated_list.field_c_p_title.yml#L13)
  - `civictheme_callout` — label `Title` — required — [field.field.paragraph.civictheme_callout.field_c_p_title.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_callout.field_c_p_title.yml#L13)
  - `civictheme_campaign` — label `Title` — required — [field.field.paragraph.civictheme_campaign.field_c_p_title.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_campaign.field_c_p_title.yml#L13)
  - `civictheme_event_card` — label `Title` — required — [field.field.paragraph.civictheme_event_card.field_c_p_title.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_event_card.field_c_p_title.yml#L13)
  - `civictheme_manual_list` — label `Title` — optional — [field.field.paragraph.civictheme_manual_list.field_c_p_title.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_manual_list.field_c_p_title.yml#L13)
  - `civictheme_message` — label `Title` — optional — [field.field.paragraph.civictheme_message.field_c_p_title.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_message.field_c_p_title.yml#L13)
  - `civictheme_navigation_card` — label `Title` — required — [field.field.paragraph.civictheme_navigation_card.field_c_p_title.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_navigation_card.field_c_p_title.yml#L13)
  - `civictheme_next_step` — label `Title` — required — [field.field.paragraph.civictheme_next_step.field_c_p_title.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_next_step.field_c_p_title.yml#L13)
  - `civictheme_promo` — label `Title` — required — [field.field.paragraph.civictheme_promo.field_c_p_title.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_promo.field_c_p_title.yml#L13)
  - `civictheme_promo_card` — label `Title` — required — [field.field.paragraph.civictheme_promo_card.field_c_p_title.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_promo_card.field_c_p_title.yml#L13)
  - `civictheme_publication_card` — label `Title` — required — [field.field.paragraph.civictheme_publication_card.field_c_p_title.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_publication_card.field_c_p_title.yml#L13)
  - `civictheme_service_card` — label `Title` — required — [field.field.paragraph.civictheme_service_card.field_c_p_title.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_service_card.field_c_p_title.yml#L13)
  - `civictheme_slider` — label `Title` — optional — [field.field.paragraph.civictheme_slider.field_c_p_title.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_slider.field_c_p_title.yml#L13)
  - `civictheme_slider_slide` — label `Title` — required — [field.field.paragraph.civictheme_slider_slide.field_c_p_title.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_slider_slide.field_c_p_title.yml#L13)
  - `civictheme_snippet` — label `Title` — required — [field.field.paragraph.civictheme_snippet.field_c_p_title.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_snippet.field_c_p_title.yml#L13)
  - `civictheme_subject_card` — label `Title` — required — [field.field.paragraph.civictheme_subject_card.field_c_p_title.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_subject_card.field_c_p_title.yml#L13)

#### `field_c_p_topics`

- **Storage** — type `entity_reference`, cardinality `-1`, `target_type: taxonomy_term` — [field.storage.paragraph.field_c_p_topics.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_topics.yml#L10)
- **Bundle attachments:**
  - `civictheme_campaign` — label `Topics` — optional — targets: `civictheme_topics` — [field.field.paragraph.civictheme_campaign.field_c_p_topics.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_campaign.field_c_p_topics.yml#L14)
  - `civictheme_event_card` — label `Topics` — optional — targets: `civictheme_topics` — [field.field.paragraph.civictheme_event_card.field_c_p_topics.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_event_card.field_c_p_topics.yml#L14)
  - `civictheme_promo_card` — label `Topics` — optional — targets: `civictheme_topics` — [field.field.paragraph.civictheme_promo_card.field_c_p_topics.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_promo_card.field_c_p_topics.yml#L14)
  - `civictheme_slider_slide` — label `Topics` — optional — targets: `civictheme_topics` — [field.field.paragraph.civictheme_slider_slide.field_c_p_topics.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_slider_slide.field_c_p_topics.yml#L14)
  - `civictheme_snippet` — label `Topics` — optional — targets: `civictheme_topics` — [field.field.paragraph.civictheme_snippet.field_c_p_topics.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_snippet.field_c_p_topics.yml#L14)

#### `field_c_p_url`

- **Storage** — type `string_long`, cardinality `1` — [field.storage.paragraph.field_c_p_url.yml#L9](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_url.yml#L9)
- **Bundle attachments:**
  - `civictheme_iframe` — label `URL` — required — [field.field.paragraph.civictheme_iframe.field_c_p_url.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_iframe.field_c_p_url.yml#L13)

#### `field_c_p_vertical_spacing`

- **Storage** — type `list_string`, cardinality `1`, allowed values: `none`, `top`, `bottom`, `both` — [field.storage.paragraph.field_c_p_vertical_spacing.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_vertical_spacing.yml#L10)
- **Bundle attachments:**
  - `civictheme_accordion` — label `Vertical spacing` — required — [field.field.paragraph.civictheme_accordion.field_c_p_vertical_spacing.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_accordion.field_c_p_vertical_spacing.yml#L15)
  - `civictheme_attachment` — label `Vertical spacing` — required — [field.field.paragraph.civictheme_attachment.field_c_p_vertical_spacing.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_attachment.field_c_p_vertical_spacing.yml#L15)
  - `civictheme_automated_list` — label `Vertical spacing` — required — [field.field.paragraph.civictheme_automated_list.field_c_p_vertical_spacing.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_automated_list.field_c_p_vertical_spacing.yml#L15)
  - `civictheme_callout` — label `Vertical spacing` — required — [field.field.paragraph.civictheme_callout.field_c_p_vertical_spacing.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_callout.field_c_p_vertical_spacing.yml#L15)
  - `civictheme_campaign` — label `Vertical spacing` — required — [field.field.paragraph.civictheme_campaign.field_c_p_vertical_spacing.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_campaign.field_c_p_vertical_spacing.yml#L15)
  - `civictheme_content` — label `Vertical spacing` — required — [field.field.paragraph.civictheme_content.field_c_p_vertical_spacing.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_content.field_c_p_vertical_spacing.yml#L15)
  - `civictheme_iframe` — label `Vertical spacing` — required — [field.field.paragraph.civictheme_iframe.field_c_p_vertical_spacing.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_iframe.field_c_p_vertical_spacing.yml#L15)
  - `civictheme_manual_list` — label `Vertical spacing` — required — [field.field.paragraph.civictheme_manual_list.field_c_p_vertical_spacing.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_manual_list.field_c_p_vertical_spacing.yml#L15)
  - `civictheme_map` — label `Vertical spacing` — required — [field.field.paragraph.civictheme_map.field_c_p_vertical_spacing.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_map.field_c_p_vertical_spacing.yml#L15)
  - `civictheme_message` — label `Vertical spacing` — required — [field.field.paragraph.civictheme_message.field_c_p_vertical_spacing.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_message.field_c_p_vertical_spacing.yml#L15)
  - `civictheme_next_step` — label `Vertical spacing` — required — [field.field.paragraph.civictheme_next_step.field_c_p_vertical_spacing.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_next_step.field_c_p_vertical_spacing.yml#L15)
  - `civictheme_promo` — label `Vertical spacing` — required — [field.field.paragraph.civictheme_promo.field_c_p_vertical_spacing.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_promo.field_c_p_vertical_spacing.yml#L15)
  - `civictheme_slider` — label `Vertical spacing` — required — [field.field.paragraph.civictheme_slider.field_c_p_vertical_spacing.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_slider.field_c_p_vertical_spacing.yml#L15)
  - `civictheme_webform` — label `Vertical spacing` — required — [field.field.paragraph.civictheme_webform.field_c_p_vertical_spacing.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_webform.field_c_p_vertical_spacing.yml#L15)

#### `field_c_p_view_link`

- **Storage** — type `link`, cardinality `1` — [field.storage.paragraph.field_c_p_view_link.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_view_link.yml#L10)
- **Bundle attachments:**
  - `civictheme_map` — label `View link` — optional — [field.field.paragraph.civictheme_map.field_c_p_view_link.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_map.field_c_p_view_link.yml#L15)

#### `field_c_p_webform`

- **Storage** — type `webform`, cardinality `1`, `target_type: webform` — [field.storage.paragraph.field_c_p_webform.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_webform.yml#L10)
- **Bundle attachments:**
  - `civictheme_webform` — label `Webform` — required — [field.field.paragraph.civictheme_webform.field_c_p_webform.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_webform.field_c_p_webform.yml#L15)

#### `field_c_p_width`

- **Storage** — type `string`, cardinality `1`, max_length `255` — [field.storage.paragraph.field_c_p_width.yml#L9](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.paragraph.field_c_p_width.yml#L9)
- **Bundle attachments:**
  - `civictheme_iframe` — label `Width` — optional — [field.field.paragraph.civictheme_iframe.field_c_p_width.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.paragraph.civictheme_iframe.field_c_p_width.yml#L13)


### Node field details

#### `field_c_n_alert_page_visibility`

- **Storage** — type `string_long`, cardinality `1` — [field.storage.node.field_c_n_alert_page_visibility.yml#L9](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_alert_page_visibility.yml#L9)
- **Bundle attachments:**
  - `civictheme_alert` — label `Page visibility` — optional — [field.field.node.civictheme_alert.field_c_n_alert_page_visibility.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_alert.field_c_n_alert_page_visibility.yml#L13)

#### `field_c_n_alert_type`

- **Storage** — type `list_string`, cardinality `1`, allowed values: `information`, `success`, `warning`, `error` — [field.storage.node.field_c_n_alert_type.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_alert_type.yml#L10)
- **Bundle attachments:**
  - `civictheme_alert` — label `Type` — required — [field.field.node.civictheme_alert.field_c_n_alert_type.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_alert.field_c_n_alert_type.yml#L15)

#### `field_c_n_attachments`

- **Storage** — type `entity_reference_revisions`, cardinality `-1`, `target_type: paragraph` — [field.storage.node.field_c_n_attachments.yml#L11](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_attachments.yml#L11)
- **Bundle attachments:**
  - `civictheme_event` — label `Attachments` — optional — targets: `civictheme_attachment` — [field.field.node.civictheme_event.field_c_n_attachments.yml#L16](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_event.field_c_n_attachments.yml#L16)

#### `field_c_n_banner_background`

- **Storage** — type `entity_reference`, cardinality `1`, `target_type: media` — [field.storage.node.field_c_n_banner_background.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_banner_background.yml#L10)
- **Bundle attachments:**
  - `civictheme_page` — label `Banner background` — optional — targets: `civictheme_image` — [field.field.node.civictheme_page.field_c_n_banner_background.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_page.field_c_n_banner_background.yml#L14)

#### `field_c_n_banner_blend_mode`

- **Storage** — type `list_string`, cardinality `1`, allowed values: `color`, `color-burn`, `color-dodge`, `darken`, `difference`, `exclusion`, `hard-light`, `hue`, `lighten`, `luminosity`, `multiply`, `normal`, `overlay`, `saturation`, `screen`, `soft-light` — [field.storage.node.field_c_n_banner_blend_mode.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_banner_blend_mode.yml#L10)
- **Bundle attachments:**
  - `civictheme_page` — label `Banner background blend  mode` — required — [field.field.node.civictheme_page.field_c_n_banner_blend_mode.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_page.field_c_n_banner_blend_mode.yml#L15)

#### `field_c_n_banner_components`

- **Storage** — type `entity_reference_revisions`, cardinality `-1`, `target_type: paragraph` — [field.storage.node.field_c_n_banner_components.yml#L11](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_banner_components.yml#L11)
- **Bundle attachments:**
  - `civictheme_page` — label `Banner components` — optional — targets: `civictheme_content`, `civictheme_manual_list`, `civictheme_iframe`, `civictheme_map`, `civictheme_slider` — [field.field.node.civictheme_page.field_c_n_banner_components.yml#L20](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_page.field_c_n_banner_components.yml#L20)

#### `field_c_n_banner_components_bott`

- **Storage** — type `entity_reference_revisions`, cardinality `-1`, `target_type: paragraph` — [field.storage.node.field_c_n_banner_components_bott.yml#L11](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_banner_components_bott.yml#L11)
- **Bundle attachments:**
  - `civictheme_page` — label `Banner bottom components` — optional — targets: `civictheme_content`, `civictheme_accordion`, `civictheme_automated_list`, `civictheme_callout`, `civictheme_campaign`, `civictheme_iframe`, `civictheme_manual_list`, `civictheme_map`, `civictheme_promo`, `civictheme_slider`, `civictheme_webform` — [field.field.node.civictheme_page.field_c_n_banner_components_bott.yml#L26](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_page.field_c_n_banner_components_bott.yml#L26)

#### `field_c_n_banner_featured_image`

- **Storage** — type `entity_reference`, cardinality `1`, `target_type: media` — [field.storage.node.field_c_n_banner_featured_image.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_banner_featured_image.yml#L10)
- **Bundle attachments:**
  - `civictheme_page` — label `Banner featured image` — optional — targets: `civictheme_image` — [field.field.node.civictheme_page.field_c_n_banner_featured_image.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_page.field_c_n_banner_featured_image.yml#L14)

#### `field_c_n_banner_hide_breadcrumb`

- **Storage** — type `boolean`, cardinality `1` — [field.storage.node.field_c_n_banner_hide_breadcrumb.yml#L9](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_banner_hide_breadcrumb.yml#L9)
- **Bundle attachments:**
  - `civictheme_page` — label `Hide breadcrumb` — optional — [field.field.node.civictheme_page.field_c_n_banner_hide_breadcrumb.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_page.field_c_n_banner_hide_breadcrumb.yml#L13)

#### `field_c_n_banner_theme`

- **Storage** — type `list_string`, cardinality `1`, allowed values: `inherit`, `light`, `dark` — [field.storage.node.field_c_n_banner_theme.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_banner_theme.yml#L10)
- **Bundle attachments:**
  - `civictheme_page` — label `Banner theme` — required — [field.field.node.civictheme_page.field_c_n_banner_theme.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_page.field_c_n_banner_theme.yml#L15)

#### `field_c_n_banner_title`

- **Storage** — type `string`, cardinality `1`, max_length `255` — [field.storage.node.field_c_n_banner_title.yml#L9](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_banner_title.yml#L9)
- **Bundle attachments:**
  - `civictheme_page` — label `Banner title` — optional — [field.field.node.civictheme_page.field_c_n_banner_title.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_page.field_c_n_banner_title.yml#L13)

#### `field_c_n_banner_type`

- **Storage** — type `list_string`, cardinality `1`, allowed values: `inherit`, `default`, `large` — [field.storage.node.field_c_n_banner_type.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_banner_type.yml#L10)
- **Bundle attachments:**
  - `civictheme_page` — label `Banner type` — required — [field.field.node.civictheme_page.field_c_n_banner_type.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_page.field_c_n_banner_type.yml#L15)

#### `field_c_n_body`

- **Storage** — type `text_long`, cardinality `1` — [field.storage.node.field_c_n_body.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_body.yml#L10)
- **Bundle attachments:**
  - `civictheme_alert` — label `Message` — required — `allowed_formats: {}` — any enabled format — [field.field.node.civictheme_alert.field_c_n_body.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_alert.field_c_n_body.yml#L15)
  - `civictheme_event` — label `Body` — required — `allowed_formats: {}` — any enabled format — [field.field.node.civictheme_event.field_c_n_body.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_event.field_c_n_body.yml#L15)

#### `field_c_n_components`

- **Storage** — type `entity_reference_revisions`, cardinality `-1`, `target_type: paragraph` — [field.storage.node.field_c_n_components.yml#L11](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_components.yml#L11)
- **Bundle attachments:**
  - `civictheme_page` — label `Components` — optional — targets: `civictheme_content`, `civictheme_accordion`, `civictheme_attachment`, `civictheme_automated_list`, `civictheme_callout`, `civictheme_campaign`, `civictheme_message`, `civictheme_iframe`, `civictheme_manual_list`, `civictheme_map`, `civictheme_next_step`, `civictheme_promo`, `civictheme_slider`, `civictheme_webform` — [field.field.node.civictheme_page.field_c_n_components.yml#L29](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_page.field_c_n_components.yml#L29)

#### `field_c_n_custom_last_updated`

- **Storage** — type `datetime`, cardinality `1`, `datetime_type: date` — [field.storage.node.field_c_n_custom_last_updated.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_custom_last_updated.yml#L10)
- **Bundle attachments:**
  - `civictheme_event` — label `Custom Last updated date` — optional — [field.field.node.civictheme_event.field_c_n_custom_last_updated.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_event.field_c_n_custom_last_updated.yml#L15)
  - `civictheme_page` — label `Custom Last updated date` — optional — [field.field.node.civictheme_page.field_c_n_custom_last_updated.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_page.field_c_n_custom_last_updated.yml#L15)

#### `field_c_n_date_range`

- **Storage** — type `daterange`, cardinality `1`, `datetime_type: datetime` — [field.storage.node.field_c_n_date_range.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_date_range.yml#L10)
- **Bundle attachments:**
  - `civictheme_alert` — label `Date range` — required — [field.field.node.civictheme_alert.field_c_n_date_range.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_alert.field_c_n_date_range.yml#L15)
  - `civictheme_event` — label `Date` — optional — [field.field.node.civictheme_event.field_c_n_date_range.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_event.field_c_n_date_range.yml#L15)

#### `field_c_n_hide_sidebar`

- **Storage** — type `boolean`, cardinality `1` — [field.storage.node.field_c_n_hide_sidebar.yml#L9](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_hide_sidebar.yml#L9)
- **Bundle attachments:**
  - `civictheme_page` — label `Hide sidebar` — optional — [field.field.node.civictheme_page.field_c_n_hide_sidebar.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_page.field_c_n_hide_sidebar.yml#L13)

#### `field_c_n_hide_tags`

- **Storage** — type `boolean`, cardinality `1` — [field.storage.node.field_c_n_hide_tags.yml#L9](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_hide_tags.yml#L9)
- **Bundle attachments:**
  - `civictheme_page` — label `Hide tags` — optional — [field.field.node.civictheme_page.field_c_n_hide_tags.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_page.field_c_n_hide_tags.yml#L13)

#### `field_c_n_location`

- **Storage** — type `entity_reference_revisions`, cardinality `-1`, `target_type: paragraph` — [field.storage.node.field_c_n_location.yml#L11](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_location.yml#L11)
- **Bundle attachments:**
  - `civictheme_event` — label `Locations` — required — targets: `civictheme_map`, `civictheme_content`, `civictheme_iframe` — [field.field.node.civictheme_event.field_c_n_location.yml#L18](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_event.field_c_n_location.yml#L18)

#### `field_c_n_show_last_updated`

- **Storage** — type `boolean`, cardinality `1` — [field.storage.node.field_c_n_show_last_updated.yml#L9](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_show_last_updated.yml#L9)
- **Bundle attachments:**
  - `civictheme_event` — label `Show Last updated date` — optional — [field.field.node.civictheme_event.field_c_n_show_last_updated.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_event.field_c_n_show_last_updated.yml#L13)
  - `civictheme_page` — label `Show Last updated date` — optional — [field.field.node.civictheme_page.field_c_n_show_last_updated.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_page.field_c_n_show_last_updated.yml#L13)

#### `field_c_n_show_toc`

- **Storage** — type `boolean`, cardinality `1` — [field.storage.node.field_c_n_show_toc.yml#L9](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_show_toc.yml#L9)
- **Bundle attachments:**
  - `civictheme_event` — label `Show Table of Contents` — optional — [field.field.node.civictheme_event.field_c_n_show_toc.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_event.field_c_n_show_toc.yml#L13)
  - `civictheme_page` — label `Show Table of Contents` — optional — [field.field.node.civictheme_page.field_c_n_show_toc.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_page.field_c_n_show_toc.yml#L13)

#### `field_c_n_site_section`

- **Storage** — type `entity_reference`, cardinality `1`, `target_type: taxonomy_term` — [field.storage.node.field_c_n_site_section.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_site_section.yml#L10)
- **Bundle attachments:**
  - `civictheme_event` — label `Site section` — optional — targets: `civictheme_site_sections` — [field.field.node.civictheme_event.field_c_n_site_section.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_event.field_c_n_site_section.yml#L14)
  - `civictheme_page` — label `Site section` — optional — targets: `civictheme_site_sections` — [field.field.node.civictheme_page.field_c_n_site_section.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_page.field_c_n_site_section.yml#L14)

#### `field_c_n_summary`

- **Storage** — type `string_long`, cardinality `1` — [field.storage.node.field_c_n_summary.yml#L9](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_summary.yml#L9)
- **Bundle attachments:**
  - `civictheme_event` — label `Summary` — optional — [field.field.node.civictheme_event.field_c_n_summary.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_event.field_c_n_summary.yml#L13)
  - `civictheme_page` — label `Summary` — optional — [field.field.node.civictheme_page.field_c_n_summary.yml#L13](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_page.field_c_n_summary.yml#L13)

#### `field_c_n_thumbnail`

- **Storage** — type `entity_reference`, cardinality `1`, `target_type: media` — [field.storage.node.field_c_n_thumbnail.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_thumbnail.yml#L10)
- **Bundle attachments:**
  - `civictheme_event` — label `Thumbnail` — optional — targets: `civictheme_image` — [field.field.node.civictheme_event.field_c_n_thumbnail.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_event.field_c_n_thumbnail.yml#L14)
  - `civictheme_page` — label `Thumbnail` — optional — targets: `civictheme_image` — [field.field.node.civictheme_page.field_c_n_thumbnail.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_page.field_c_n_thumbnail.yml#L14)

#### `field_c_n_topics`

- **Storage** — type `entity_reference`, cardinality `-1`, `target_type: taxonomy_term` — [field.storage.node.field_c_n_topics.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_topics.yml#L10)
- **Bundle attachments:**
  - `civictheme_event` — label `Topics` — optional — targets: `civictheme_topics` — [field.field.node.civictheme_event.field_c_n_topics.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_event.field_c_n_topics.yml#L14)
  - `civictheme_page` — label `Topics` — optional — targets: `civictheme_topics` — [field.field.node.civictheme_page.field_c_n_topics.yml#L14](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_page.field_c_n_topics.yml#L14)

#### `field_c_n_vertical_spacing`

- **Storage** — type `list_string`, cardinality `1`, allowed values: `none`, `top`, `bottom`, `both` — [field.storage.node.field_c_n_vertical_spacing.yml#L10](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.storage.node.field_c_n_vertical_spacing.yml#L10)
- **Bundle attachments:**
  - `civictheme_event` — label `Vertical spacing` — required — [field.field.node.civictheme_event.field_c_n_vertical_spacing.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_event.field_c_n_vertical_spacing.yml#L15)
  - `civictheme_page` — label `Vertical spacing` — required — [field.field.node.civictheme_page.field_c_n_vertical_spacing.yml#L15](https://github.com/civictheme/monorepo-drupal/blob/29fa0fd3271d1e8ef48179f3043385304c699716/web/themes/contrib/civictheme/config/install/field.field.node.civictheme_page.field_c_n_vertical_spacing.yml#L15)

