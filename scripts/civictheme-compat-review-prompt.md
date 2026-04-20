# CivicTheme Skills — Compatibility Review Prompt

Use this prompt to audit the skill files in `claude-civictheme-skills` against the
upstream CivicTheme source. Run it in a Claude Code session where the CivicTheme
sources are available locally (clone or worktree), OR where the agent has web
access and can read the upstream repositories and `drupal.org`.

Authoritative upstream sources:
- Drupal theme / SDC implementation: `https://github.com/civictheme/monorepo-drupal`
- UI Kit (SDC package): `https://github.com/civictheme/uikit/tree/main/packages/sdc`
- UI Kit (Twig package, for non-Drupal usage): `https://github.com/civictheme/uikit/tree/main/packages/twig`

### Breaking changes since CivicTheme 1.11.1

Package names have changed from a single package to workspace packages:
- Use `@civictheme/twig` for the Twig implementation (replaces `@civictheme/uikit` for non-Drupal consumers).
- Use `@civictheme/sdc` for the Drupal SDC implementation.

CivicTheme (the Drupal theme) is switching to the SDC implementation. Skills
that reference `@civictheme/uikit`, the old single-package layout, or the legacy
`civictheme/monorepo` repo URL are out of date and should be flagged.

Replace `<PATH_TO_SKILLS_REPO>` and `<PATH_TO_CIVICTHEME>` before running.

---

You are auditing a prompt library called `claude-civictheme-skills` for
compatibility with the **upstream CivicTheme Drupal theme**. The skills live at
`<PATH_TO_SKILLS_REPO>`; authoritative CivicTheme sources are at
`<PATH_TO_CIVICTHEME>` or, on the web:
- `https://github.com/civictheme/monorepo-drupal` (Drupal theme)
- `https://github.com/civictheme/uikit/tree/main/packages/sdc` (SDC components)
- `https://github.com/civictheme/uikit/tree/main/packages/twig` (Twig components)

The skills are prompts, not code. Each skill tells Claude how to generate Drupal
theme files (SDC components, paragraph integration, Twig, SCSS, JS libraries).
If a skill misstates a CivicTheme API, convention, or file contract, every
component generated from that skill will be subtly broken — and the breakage is
invisible until the generated code lands in a real sub-theme.

Your job: find claims in the skills that **do not match** the real CivicTheme
source. Do not critique writing style, tone, or ordering — only correctness.

## Skills to audit

- `skills/router.md` — classifier/entry point
- `skills/handlers/civictheme-sdc-generator/` — new SDC components
- `skills/handlers/civictheme-override-generator/` — override existing CivicTheme components
- `skills/handlers/civictheme-paragraph-generator/` — paragraph bundle integration
- `skills/handlers/civictheme-style-override/` — SCSS variable overrides
- `skills/handlers/civictheme-js-enhancement/` — JS/CSS enhancements without SDC

Each handler has a `SKILL.md` plus `references/*.md`. Audit all of them.

## Specific claim categories to verify

For each, find where it appears in the skills, then confirm or refute from upstream.

### 1. CivicTheme PHP helper functions
Verify these function names, signatures, and behaviours match the CivicTheme
source. Grep the CivicTheme monorepo (typically under `civictheme.theme` or
`includes/*.inc`) for the function definitions.

- `civictheme_get_field_value($entity, $field_name, $multiple, $default)`
- `_civictheme_preprocess_paragraph__paragraph_field__title($variables)`
- `_civictheme_preprocess_paragraph__paragraph_field__content($variables)`
- Any other `civictheme_*` or `_civictheme_*` helper mentioned in the skills.

For each: does the function exist? Do the parameters match? Does the documented
behaviour (e.g. "maps standard body/content field to `$variables['content_items']`")
match the actual implementation?

### 2. SDC `.component.yml` schema
- Do the YAML examples in `component-yml-patterns.md` and
  `storybook-patterns.md` use the correct JSON Schema shape
  (`props: { type: object, properties: { ... } }`)?
- Are `slots:`, `required:`, `status:`, `replaces:` fields documented the same
  way CivicTheme uses them?
- Does the `components_combined/` loading rule (mentioned in
  `libraries-and-assets.md`) reflect CivicTheme's actual library structure?

### 3. Libraries, assets, and overrides
Verify in the real CivicTheme `.libraries.yml` and any sub-theme examples:
- Is `libraries-override` actually the mechanism CivicTheme uses for JS/CSS
  replacement? Any `libraries-extend` uses documented?
- Are the path-resolution rules correct (left: base theme; right: sub-theme)?
- Does CivicTheme auto-enqueue compiled CSS for SDC, as the skill claims?

### 4. Field naming conventions
- Is the `field_c_p_*` prefix rule (mentioned in `field-naming.md`) a real
  CivicTheme convention, or a sub-theme-specific pattern?
- Are the "standard shared props" (`theme`, `vertical_spacing`, `with_background`)
  actually standard across CivicTheme components?

### 5. GovCMS SaaS constraints (referenced in `router.md`)
- Does the GovCMS PHPStan config actually ban `\Drupal::database()`?
- Are the `\Drupal::` uses the skills permit (entityTypeManager, currentUser,
  token) actually allowed under GovCMS SaaS?
- If GovCMS has public docs, cite them.

### 6. Storybook integration
- Does CivicTheme's Storybook setup actually import `.twig` files directly as
  components, or does it use a different preset?
- Are `argTypes` patterns consistent with how CivicTheme itself writes stories?

### 7. Package references and upstream URLs (post-1.11.1)
- Do any skills still reference `@civictheme/uikit` as a single package? Since
  1.11.1, consumers must use `@civictheme/twig` (Twig, non-Drupal) or
  `@civictheme/sdc` (Drupal SDC).
- Do any skills link to `github.com/civictheme/monorepo`? The Drupal theme now
  lives at `github.com/civictheme/monorepo-drupal`, and the components live in
  `github.com/civictheme/uikit` under `packages/sdc` and `packages/twig`.
- Flag any import paths, `package.json` snippets, or documentation references
  that use the pre-1.11.1 package name or repo URL.

## Output format

Produce a single markdown report with this structure:

```
## Verified claims
- <claim>: matches upstream at <path/URL>

## Incorrect claims
- <skill file:line>: "<quoted claim>"
  - Reality: <what the upstream source actually shows, with <path/URL>>
  - Impact: <how generated code will break>

## Unverifiable claims
- <claim>: <why — e.g. CivicTheme source does not define X either way>

## Missing guidance
- <pattern CivicTheme uses that the skills don't cover but should>
```

Prioritise **incorrect claims** over style feedback. A single wrong function
signature affects every component generated from that skill, so a short, sharp
list of real issues is more valuable than a long list of nitpicks.

If you cannot locate CivicTheme source (no local clone, no web access), stop
and say so — do not speculate.
