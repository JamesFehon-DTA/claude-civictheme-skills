# UIKit Toolchain Reference

Source: `package.json` and `README.md` in the UIKit repo root.

---

## Scripts relevant to this skill

Run from the UIKit repo root after authoring a new component.

| Command | Purpose |
|---|---|
| `npm run dist` | Compile SCSS → CSS across all workspaces |
| `npm run validate` | Validate `.component.yml` enum values and theme variables |
| `npm run dev:twig` | Start Storybook dev server for the twig package |
| `npm run lint` | Lint all workspaces — run before committing |

`npm run validate` covers both `validate-component-enums.js` and `validate-theme-variables.js`. Use it rather than calling either script directly.

---

## Scripts not relevant to this skill

These scripts exist but operate on the SDC ↔ twig sync workflow used by CivicTheme maintainers. They are documented here for context only.

| Command | What it does | Why excluded |
|---|---|---|
| `npm run components:update:twig` | Syncs twig files SDC → twig with namespace transforms | Wrong direction for twig-first authoring |
| `npm run components:update:sdc` | Regenerates docblock headers in SDC files from `.component.yml` | No SDC component exists yet |
| `npm run components:update` | Runs both of the above | Same reasons |
| `npm run components:check` | Validates SDC ↔ twig sync state | No SDC counterpart to check against |

---

## Pre-commit hooks (Husky)

Husky runs quality checks before each commit: lint, tests, and `components:check` (verifies SDC and twig are in sync). For twig-only components with no SDC counterpart, `components:check` passes — the check only validates that existing SDC components are reflected in twig, and a net-new twig-only component has no SDC source to be checked against.

To bypass hooks in exceptional circumstances only:
```bash
HUSKY=0 git push
```

---

## Authoring workflow (this skill)

This skill targets twig-first authoring. Components are created in `packages/twig/components/` directly — there is no SDC source to sync from. A future twig → SDC promotion path may be added later.

The CivicTheme maintainer workflow (SDC → twig) is the reverse: components are authored in `packages/sdc/`, then synced to the twig package. Do not follow that path unless working in the SDC-first maintainer workflow.
