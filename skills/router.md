---
name: civictheme-component-type-selector
description: Use this skill whenever the user mentions creating, overriding, or styling any CivicTheme component, adding JS/CSS behaviour to a CivicTheme sub-theme, or creating a paragraph or content element. This is the required entry point — always classify before generating. Also triggers for "create a component", "override a component", "style a component", "scaffold a component", "add a paragraph type", "create a content element", "add sortable table", "add filterable table", "add JS enhancement", or any mention of CivicTheme SDC work.
---

# CivicTheme Component Type Selector

Classification-only skill. Determine the correct component pattern and recommend the next skill. Do not generate files.

## Required project context

Confirm before classifying — ask the user only if values are unknown:

| Variable | Description | Example |
|---|---|---|
| `[THEME_MACHINE_NAME]` | Sub-theme machine name (no "civic" prefix) | `my_agency` |
| `[THEME_DIR]` | Path to sub-theme root | `web/themes/custom/my_agency` |
| `[BASE_THEME_DIR]` | Path to CivicTheme base theme | `web/themes/contrib/civictheme` |

## Five component patterns

| Pattern | When to use |
|---|---|
| `new_sdc_component` | Brand-new UI not present in CivicTheme |
| `override_existing_civictheme_component` | Replace markup, structure, or behaviour of an existing CivicTheme component |
| `style_only_override_existing_civictheme_component` | Change appearance only — colour, spacing, typography; no markup changes |
| `js_css_enhancement_without_sdc_component` | Add JS/CSS behaviour to existing markup; no new SDC |
| `paragraph_or_content_element_using_civictheme_component` | Drupal content-authoring pattern wrapping an SDC component |

## Decision logic

1. New UI pattern not present in CivicTheme → `new_sdc_component`
2. Change markup, structure, or logic of an existing component → `override_existing_civictheme_component`
3. Change appearance only (colour, spacing, border, typography) → `style_only_override_existing_civictheme_component`
4. Add JS/CSS to existing markup without creating an SDC → `js_css_enhancement_without_sdc_component`
5. Drupal content authoring pattern wrapping an SDC component → `paragraph_or_content_element_using_civictheme_component`
6. Ambiguous → ask exactly one question: "Are you changing markup/behaviour, appearance only, or creating a new authoring pattern?"

**Style-first rule:** If the user describes changes that sound structural but a style-only variable override would satisfy the actual need, classify as `style_only_override_existing_civictheme_component` and explain why before proceeding.

## Output contract

```yaml
component_pattern: <new_sdc_component | override_existing_civictheme_component | style_only_override_existing_civictheme_component | js_css_enhancement_without_sdc_component | paragraph_or_content_element_using_civictheme_component>
reason: <one sentence>
project_context:
  theme_machine_name: <[THEME_MACHINE_NAME]>
  theme_dir: <[THEME_DIR]>
  base_theme_dir: <[BASE_THEME_DIR]>
recommended_next_skill: <civictheme-sdc-generator | civictheme-override-generator | civictheme-style-override | civictheme-js-enhancement | civictheme-paragraph-generator>
```

Pass `project_context` verbatim to the next skill — all downstream skills require these values.
