# Changelog

## 1.5.0

Closes a routing gap where a UIKit component **port** was hand-authored and never triggered any skill, missing the reserved-`attributes` convention.

- **New commands `civictheme-skills:init` and `civictheme-skills:update`** – write/maintain a managed block in the consumer repo's `CLAUDE.md` so skill routing survives even when the agent isn't thinking about skills. Detects UIKit (`packages/sdc/`) vs Drupal sub-theme; asks when neither is detectable. Idempotent and byte-stable; never touches the rest of the file.
- **Type-selector is now a universal front door.** It detects `packages/sdc/` first and routes UIKit work to the UIKit skills up front, instead of advertising UIKit triggers and then disowning them. `packages/sdc/` is now a stated routing signal in every skill description.
- **Porting and extending now route.** `civictheme-uikit-component-generator` triggers on "pull/port/migrate/copy a component in from another repo" and on "add a new variant/type/option" to an existing component – the two phrasings that slipped past before.
- **Reserved-`attributes` rule is enforced.** `civictheme-health-check` fails any `*.component.yml` that declares `attributes` under `props`; the generators carry the same rule as a checklist item. Removed the stray `attributes` declaration from the `civictheme-sdc-generator` shared-props example.
- **SessionStart prime hook.** In a CivicTheme repo, the plugin now re-injects the routing rule into context on every session start – and, via the `compact` matcher, after each compaction, which is when a mid-task agent loses it. Silent in every other repo. This is the guard that does not depend on the agent reading CLAUDE.md.
