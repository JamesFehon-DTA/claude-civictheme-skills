---
name: civictheme-paragraph-generator
description: Generate the Drupal integration layer for a CivicTheme-styled paragraph or content element, including paragraph template, preprocess hook, theme registration, and JS library attachment. Use when the type-selector returns paragraph_or_content_element_using_civictheme_component, or when the user asks to create a paragraph type, content element, or Drupal authoring pattern wrapping a CivicTheme SDC component.
---

# CivicTheme Paragraph Generator

Generate the Drupal integration layer for a CivicTheme-styled paragraph type.

## Required inputs

- `[THEME_MACHINE_NAME]` — sub-theme machine name
- Paragraph machine name (snake_case)
- Target SDC component namespace (`[THEME_MACHINE_NAME]:[name]` or `civictheme:[name]`)
- Fields needed (machine names or descriptions to infer machine names from)
- Whether the component has JS behaviour requiring library attachment

## Core rules

- Paragraph template includes the SDC component using `only` — mandatory; prevents Drupal internals from polluting component prop scope.
- `$variables['content'] = NULL` is required in every paragraph preprocess hook — suppresses Drupal's default field render.
- CSS auto-loads via SDC when the component template renders. Only attach JS in the library.
- **Field naming:**
  - Shared CivicTheme paragraph fields → `field_c_p_` prefix
  - Custom sub-theme fields → `field_[THEME_MACHINE_NAME]_` prefix
  - `field_p_` is **not a real CivicTheme convention** — never use it
  - See `references/field-naming.md` for full rules and linting logic

## Cacheability

CivicTheme manages cacheable metadata at the field-getter level (introduced as a security fix in 1.12.0). Generated preprocess hooks must follow this convention.

- Pass `$variables` as the `$build` argument to `civictheme_get_field_referenced_entities()` and `civictheme_get_referenced_entity_labels()`. Omitting it triggers a deprecation warning in 1.12.x; upstream states the parameter will be required in 1.13.0.
- Attach the paragraph's own cache tags: `$variables['#cache']['tags'] = $paragraph->getCacheTags();` — mirrors `manual_list.inc:39` in CivicTheme source.
- For context-varying output (URL, query, role) use narrow contexts: `url.path`, `url.query_args:key`, `user.roles`. Avoid bare `user` — it defeats Akamai edge caching on GovCMS SaaS.
- Never set `$variables['#cache']['max-age'] = 0` in a paragraph preprocess — makes the host node page uncacheable at the edge. Per-user state belongs in a `#lazy_builder` placeholder so the surrounding page stays cacheable.

See `references/preprocess-helpers.md` §Cacheable metadata for worked examples, upstream source references, and the deprecation link.

## Decision logic

- The underlying SDC component doesn't exist yet → note that `civictheme-sdc-generator` must run first (or in parallel); do not block generation
- User wants visual changes only to an existing paragraph → stop; recommend `civictheme-style-override`
- JS needed → attach JS-only library in preprocess hook (`$variables['#attached']['library'][]`); omit CSS from the library
- No JS → omit the library entry entirely; SDC auto-loads CSS

## Reference files

Read before generating:

- `references/field-naming.md` — allowed/disallowed field prefixes, linting rules, sub-theme vs CivicTheme namespaces
- `references/twig-patterns.md` — paragraph template pattern, `only` keyword rationale
- `references/libraries-and-assets.md` — conditional library attachment, SDC CSS auto-loading
- `references/preprocess-helpers.md` — CivicTheme field helper API, shared preprocess helpers, when `\Drupal::` is appropriate
- `../../references/civictheme-field-storage.md` — storage type, cardinality, max length, HTML support, and bundle attachments for every canonical `field_c_p_*` / `field_c_n_*`. Consult before mapping a field to a component prop: if the target prop expects HTML but the field is `string` / `string_long` (e.g. `field_c_p_summary`, `field_c_p_url`), warn the author — the markup will render escaped. Use it to confirm cardinality before deciding the `$multiple` flag on `civictheme_get_field_value()`.

## Output contract

```yaml
paragraph_machine_name: <machine_name>
component_namespace: <[THEME_MACHINE_NAME]:[name] or civictheme:[name]>
files:
  - path: templates/paragraph--[paragraph-machine-name].html.twig
    purpose: thin paragraph template — passes fields as props to the SDC component
    contents: |
      <full file contents>
  - path: includes/paragraphs--[paragraph-machine-name].inc
    purpose: preprocess hook — field mapping, cache-tag attachment, content null, JS library attachment
    contents: |
      <full file contents — must include $variables['#cache']['tags'] = $paragraph->getCacheTags(); and pass $variables as $build to civictheme_get_field_referenced_entities / civictheme_get_referenced_entity_labels where referenced entities are loaded>
  - path: [THEME_MACHINE_NAME].theme
    purpose: preprocess include registration
    contents: |
      <only the new require_once line — not the entire file>
  - path: [THEME_MACHINE_NAME].libraries.yml  # only if JS needed
    purpose: JS-only library entry
    contents: |
      <only the new library entry — not the entire file>
post_generation_notes:
  - Ensure the paragraph bundle and all mapped fields exist in Drupal configuration before testing.
  - Drupal configuration must exist before testing: field.storage.*, field.field.*, core.entity_form_display.*, core.entity_view_display.*, paragraphs.paragraphs_type.*. Export from a working environment via `drush cex` or create manually in config/install.
  - Run drush cr after adding templates and preprocess hooks.
```
