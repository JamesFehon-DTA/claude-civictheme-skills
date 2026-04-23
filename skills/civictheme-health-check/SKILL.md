---
name: civictheme-health-check
description: Run the full CivicTheme validation sequence (lint → validate → theme-variable usage check → a11y anti-pattern grep) and consolidate the results into a single structured report. Use when the user asks to "run checks", "run validation", "health-check the theme", "verify the component set", "lint and validate", or wants a pre-commit / pre-PR sanity pass across the whole repo. Works in both a Drupal sub-theme and a CivicTheme UIKit / design-system repo — detects which context it is in by probing for `packages/sdc/` and branches the command set accordingly. Not a component-pattern handler — this is a diagnostics skill and is not routed through `civictheme-component-type-selector`.
---

# CivicTheme Health Check

Diagnostic skill. Run the standard validation sequence for a CivicTheme repo — UIKit or Drupal sub-theme — and return one consolidated report. No file generation.

This skill is **instructions for Claude, not an executable script**. The steps below tell Claude which commands to run via the Bash tool, how to parse their output, and how to shape the consolidated report. Do not attempt to execute this file as a shell program; follow it as a procedure.

## Context detection

Before running any command, determine which repo archetype this is:

1. Check for `packages/sdc/` at the repo root.
   - **Present** → UIKit / design-system / component-library repo. The authoring source is `packages/sdc/`; `packages/twig/` is a generated derivative.
   - **Absent** → Drupal sub-theme. Components live under the sub-theme directory; there is no two-package SCSS pipeline.
2. Read the repo's `package.json` (root, or the workspace root if `packages/sdc/` is present) and capture the `scripts` object. This is the authoritative list of what commands are actually wired up — probe it before invoking any command, and mark anything absent as `not_configured` rather than running it and catching a shell error.

Record the detected context and carry it into the report (`context: uikit` or `context: sub_theme`). It changes which commands are relevant (see **Context-specific additions** below) but does not change the four baseline steps.

## The four baseline steps

Run each in order. Do not parallelise — a failure in one step can explain failures in the next (e.g. `lint` auto-formatting can eliminate a `validate` failure by chance, or a `validate` failure can make the a11y grep findings impossible to interpret).

For each step, record: the step name, the exact command invoked, the status (`pass` / `fail` / `not_configured`), and — on failure — the relevant output lines or file paths plus a pointer to the rule or reference being violated.

### Step 1 — lint

Prefer the repo's configured lint command. Probe `package.json` scripts in this order and use the first that exists:

1. `npm run lint`
2. `npm run lint:fix` — only if `lint` is absent; note that this mutates files, so prefer the non-fix form for a diagnostic pass

If none exists, report `not_configured`. Do not invent a lint command.

Expected failure shape: stylelint / ESLint / PHPCS violations, one per line with file path and line number. Include the first ~20 failure lines in the report; elide the rest with a `… (N more)` marker.

### Step 2 — validate

```
npm run validate
```

On the UIKit side, `validate` runs both `validate-component-enums.js` and `validate-theme-variables.js` (see `references/variables-pipeline.md` for how the theme-variable check ties to the SCSS → CSS custom property pipeline — a failure here almost always means a `ct-component-property(…)` call has no matching declaration in `components/variables.components.scss`).

On the sub-theme side, the script may not exist. If the `validate` script is not in `package.json`, report `not_configured`.

Expected failure shape: enum-mismatch lines (unknown value on a `size` / `theme` / `type` field in `.component.yml`), or missing-variable lines (an `$ct-[component]-[theme]-…` referenced but never assigned). For each failure, note the file and — when the failure message is a missing variable — cite `references/variables-pipeline.md` so the reader knows where to look for the expected shape.

### Step 3 — validate-theme-variable-usage (optional)

```
npm run validate-theme-variable-usage
```

This command is not universally present. Probe `package.json.scripts` for the key `validate-theme-variable-usage` before invoking. **If absent, report `not_configured`, not `fail`.** The distinction matters: `not_configured` means "this check does not apply to this repo"; `fail` means "this check ran and found a problem". Conflating the two produces false alarms in repos that never installed the script.

When present, it is a stricter theme-variable audit than `validate`. Failures here almost always trace back to the four-stage pipeline in `references/variables-pipeline.md`; cite that file in each failure entry.

### Step 4 — a11y anti-pattern grep against Twig templates

This step is **dynamic**. The grep patterns are derived from the current rule set in `references/accessibility.md` at run time — they are not hardcoded in this SKILL.md. If accessibility.md gains a rule #D / #E / …, the health check picks it up without a skill edit.

Procedure:

1. **Read `references/accessibility.md` first.** Do not skip this step. The file is the source of truth for what counts as an anti-pattern.
2. **For each rule (#A, #B, #C, and any later letters), identify the banned pattern.** Every rule has a "do not emit" clause — the grep target is the literal shape of that clause as it would appear in Twig source. Examples of how to derive the grep, based on the current rule set:
   - **Rule #A — `disabled` on `<a>`.** The banned shape is a `disabled` attribute inside an `<a …>` opening tag (either literal or via a Twig conditional). A reasonable first-pass regex: `<a\b[^>]*\bdisabled\b` (catches the attribute directly on the anchor). Also worth scanning for `{% if .* %}disabled{% endif %}` *inside* an anchor tag — narrow with surrounding context if the first regex produces noise.
   - **Rule #B — `aria-label="Opens in a new tab"` replacing the accessible name.** The banned shape is an `aria-label` whose value is exactly the new-tab notice, with no other label text. Regex: `aria-label=(?:"|')Opens in a new (?:tab|window)(?:"|')`. The correct pattern (visually-hidden suffix span) is allowed; only the label-only form is banned.
   - **Rule #C — decorative icon spans missing `aria-hidden="true"`.** Harder to grep for with a single regex because it is an *absence*. A practical proxy: list every `include 'civictheme:icon'` call site, then flag those not enclosed by a span carrying `aria-hidden="true"`. If the grep is ambiguous (inline icons inside label text), report the hits as *candidates* needing human review, not definitive failures.
3. **Run the greps.** Scope to `.twig` files. The correct search roots:
   - UIKit: `packages/sdc/components/` (source of truth — `packages/twig/` is a derivative and will contain the same hits).
   - Sub-theme: the sub-theme directory's `components/` tree (and any `templates/` tree containing Twig overrides).
4. **Build findings.** For each hit, record the file path, line number, the matched text, and the rule letter. Cite `references/accessibility.md` with the anchor (`#A`, `#B`, etc.) so the reader can jump straight to the rule prose.

If a rule's banned pattern is phrased in accessibility.md as an absence (e.g. Rule #C), report its findings as *candidates* with a note explaining the grep cannot be definitive. Do not silently drop the rule — the intent is that every rule in accessibility.md shows up in the report, even if only to say "no candidates found" or "manual review needed".

The grep is not a replacement for a11y audit tooling. It catches the three known anti-patterns that generator skills are meant to prevent at generation time; it is a regression tripwire, not a full a11y review.

## Context-specific additions

Run these in addition to the baseline four, only when the context matches.

### UIKit only

- `npm run components:check` — fails if `packages/twig/` is not a byte-accurate derivative of `packages/sdc/`. Run this after `validate` and before the a11y grep. A failure here means someone hand-edited a file in `packages/twig/`; the fix is to rerun `npm run components:update` and commit the regenerated output, not to chase the diff manually.

Do **not** run `dist:sdc` / `dist:twig` as part of the health check. Those are iteration-loop build steps (see `civictheme-uikit-scss-iteration`); they are not validation steps and their output is not a pass/fail signal for repo health.

### Sub-theme only

There is no universally-installed Drupal-side validator that mirrors `components:check`. If the project has configured a custom script (common patterns: `drush site:status` for a smoke test, `drush sdc:list` to audit component discovery), and the user has asked for those to be included, probe `package.json.scripts` and `composer.json.scripts` for the script name before invoking. Otherwise the baseline four are the full health check on the sub-theme side.

## Output contract

Return a single structured report. The shape:

```yaml
context: uikit
repo_root: /absolute/path/to/repo
steps:
  - name: lint
    command: npm run lint
    status: pass
    failures: []
  - name: validate
    command: npm run validate
    status: fail
    failures:
      - file: packages/sdc/components/01-atoms/button/button.scss
        line: 42
        message: "missing variable $ct-button-light-background-color"
        rule: "references/variables-pipeline.md — stage 3"
  - name: validate-theme-variable-usage
    command: npm run validate-theme-variable-usage
    status: not_configured
    note: "script not present in package.json"
  - name: components_check
    command: npm run components:check
    status: pass
    failures: []
  - name: a11y_grep
    source_rules_file: skills/_shared/references/accessibility.md
    rules_checked:
      - "A"
      - "B"
      - "C"
    status: fail
    findings:
      - rule: "A"
        rule_anchor: "references/accessibility.md#A"
        description: "disabled attribute on <a>"
        hits:
          - path: packages/sdc/components/01-atoms/button/button.twig
            line: 17
            match: "<a class=\"ct-button\" disabled>"
      - rule: "C"
        rule_anchor: "references/accessibility.md#C"
        description: "decorative icon without aria-hidden=true (candidate)"
        candidates: true
        hits: []
summary: "2 failures: validate (1 missing variable), a11y grep (1 hit on rule A). All other steps pass or not-configured."
```

Every step appears in the report even when it passes or is not configured — a missing step in the output is ambiguous (did it fail? was it skipped? did the skill forget?). An explicit `not_configured` with a one-line `note` is the readable form.

The `summary` line is the human-readable digest — one sentence, failure-first. A reader should be able to glance at `summary` and know whether the repo is clean.

## Reference files

- `references/accessibility.md` — **required reading for step 4.** The a11y grep step builds its patterns from the rules here at run time. Do not hardcode rule shapes; re-derive them every run so a11y.md additions land automatically.
- `references/variables-pipeline.md` — cite from step 2 and step 3 failure entries. The four-stage pipeline explains why a "missing variable" failure from `validate` or `validate-theme-variable-usage` is almost always a stage-3 gap (variable not declared in `components/variables.components.scss`).

## Out of scope

- **Fixing what the health check finds.** This skill reports; it does not edit. Once the report identifies a failure, route the fix through the matching generator or iteration skill (`civictheme-uikit-scss-iteration` for SCSS edits, the appropriate generator for markup regeneration).
- **Component generation.** The type-selector and generator skills own that.
- **Full accessibility audit.** The a11y grep catches the three generator-prevented anti-patterns; it does not cover colour contrast, focus order, heading hierarchy, landmark regions, or other audit surfaces that need a browser or axe-core.
- **Drupal runtime checks.** `drush cr`, SDC discovery, config-import status — these are deployment concerns, not a repo-level health check. Flag them in the report only if the user has explicitly asked for them.
