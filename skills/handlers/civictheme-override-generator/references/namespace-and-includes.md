# Namespace & Include Strategy

How Twig includes resolve inside a CivicTheme sub-theme override, which include style to prefer, and what breaks silently when an override gets it wrong.

All upstream references below are against CivicTheme 1.12.2 shipped artefact (`civictheme.info.yml` version `1.12.2`, datestamp `1764722783`). Verify against your installed version before relying on exact namespace names.

## Two include systems, both active

CivicTheme 1.12.x runs two Twig resolution systems simultaneously:

### 1. Drupal core SDC (machine-name includes)

```twig
{% include 'civictheme:text-icon' with { ... } only %}
```

- Resolves through Drupal core's Single Directory Components discovery.
- Namespace is the **theme machine name** (`civictheme`), auto-registered — no `.info.yml` entry required for SDC itself.
- Override mechanism: copy the component directory into the sub-theme's `components/` and add `replaces: civictheme:[name]` to the sub-theme `.component.yml`. Drupal routes `civictheme:[name]` to the override automatically.

### 2. components contrib module (namespaced-path includes)

```twig
{% include '@atoms/button/button.twig' %}
```

- Provided by the `drupal/components` contrib module (declared as a dependency in `civictheme.info.yml`: `- components:components`).
- Namespaces are registered explicitly in `.info.yml` under `components: namespaces:`.
- Pre-dates SDC. Still present because CivicTheme shipped it before Drupal core added SDC and sub-themes may depend on the paths.

## What CivicTheme upstream actually uses

**Verified against shipped 1.12.2:** upstream Twig templates use SDC machine-name includes exclusively. `grep 'include .@' components/01-atoms/button/` in a shipped CivicTheme returns nothing for `@atoms/...` or `@civictheme/...` style paths. The components-contrib namespaces are declared but not exercised by CivicTheme's own code.

**Recommendation for sub-theme overrides:** match the upstream convention — use `civictheme:[name]` machine-name includes inside overridden templates. Reasons:

- Survives upstream filesystem reorganisation — the `replaces:` target is versioned by SDC metadata, not by path.
- Routes correctly to any upstream replacement or sub-theme override without template edits.
- Doesn't depend on the continued presence of the components-contrib module (Drupal core SDC is the long-term direction).

Do NOT convert upstream `civictheme:name` includes to `@atoms/name/name.twig` style during an override. It's a silent stability regression.

## Registering namespaces in the shipped `civictheme.info.yml`

For reference — the base theme registers these namespaces:

```yaml
dependencies:
  - components:components

components:
  namespaces:
    base:
      - components/00-base
    atoms:
      - components/01-atoms
    molecules:
      - components/02-molecules
    organisms:
      - components/03-organisms
    ct-atoms:
      - components/01-atoms
    ct-molecules:
      - components/02-molecules
    ct-organisms:
      - components/03-organisms
    ct-templates:
      - components/04-templates
```

Includes resolving to these paths (`@atoms/...`, `@ct-atoms/...`, etc.) are available to any theme that depends on CivicTheme.

## When a sub-theme needs its own namespace registration

Only if the sub-theme publishes Twig templates that other themes or modules include via `@[THEME_MACHINE_NAME]/...` paths. For standard SDC overrides via `replaces:`, no registration is needed.

If the sub-theme does need its own namespace, register it in `[THEME_MACHINE_NAME].info.yml`:

```yaml
dependencies:
  - components:components

components:
  namespaces:
    [THEME_MACHINE_NAME]:
      - components
```

This exposes `@[THEME_MACHINE_NAME]/subdir/file.twig` to any Twig caller.

## Failure modes

Three silent or hard failures to watch for after generating an override:

| Symptom | Cause | Diagnosis |
|---|---|---|
| **Hard render error** on a page that uses the overridden component | Overridden template has a stale `@civictheme/...` or `@atoms/...` include pointing at a path upstream has moved or renamed | Search the override for `@` includes and convert to `civictheme:name` machine-name form |
| **Component renders with base markup, not override markup** | SDC discovery cache wasn't cleared after adding `replaces:` | Run `drush cr` — SDC component discovery is cached and `replaces:` won't take effect without a rebuild |
| **Component renders with default prop values, not the values passed in** | Override was copied from an older CivicTheme version; the prop API has since changed (prop renamed, new required prop added) | Diff `[BASE_THEME_DIR]/components/[level]/[name]/[name].component.yml` against the override and reconcile |

## Post-generation checklist

After generating an override, verify:

1. `.component.yml` contains `replaces: civictheme:[name]` and preserves all base props verbatim.
2. No `@civictheme/...` or `@atoms/...` includes appear in the overridden `.twig` — all includes use `civictheme:name` form.
3. `{{ attributes }}` appears on the root element (cache metadata bubbles through it).
4. `drush cr` has been run after adding the override.
5. The override's `.component.yml` matches upstream's current prop schema — run a diff if the base theme was updated recently.
