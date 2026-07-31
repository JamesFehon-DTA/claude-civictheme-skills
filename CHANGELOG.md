# Changelog

## Unreleased

<!-- Write the notes for the next release here. The release workflow renames this heading to the new version and publishes the section as the GitHub release body. An empty section fails the release. -->

## 1.6.0

Adds a reuse gate so component-JS work checks CivicTheme's existing behaviours before authoring new script, plus a read hook that removes per-file permission prompts.

- **Reuse gate before any component JS.** New `core-behaviours.md` maps each interaction (show/hide, dismiss, sticky, tabs, popover, skip-link) to the `00-base` behaviour that already implements it, with data-attribute contracts. The selector and UIKit generator both fire the gate: if a primitive matches, emit its markup and delete the bespoke script. Applies to ports too.
- **`.storybook/` and story-API changes route as `config`,** not component work – edit in place, validate with build/lint, skip the generator's contract.
- **JS init timing and verification documented.** Why the top-level `querySelectorAll` sweep works for `00-base` but not per-component files; new `js-verification.md` for the HTML-addon serialisation and `transitionend` traps.
- **Plugin reads its own bundle without prompts.** `PreToolUse` hook scoped to the resolved `$CLAUDE_PLUGIN_ROOT`; rejects symlink and `..` escapes, never denies.
- **Storybook story conventions expanded** – peer-mirrored titles, `tags`, explicit `argTypes`, no demo `play` functions.
- **Health check gates the silent SB8 background pattern** on the sub-theme side, where `validate` is absent.
- **`toolchain.md` sync model corrected** – `.stories.twig` fixtures exist in both packages and are hand-maintained.
- **Release workflow refuses a mismatched manifest** – version base checked against the latest tag, tag verified before push.

## 1.5.0

Closes a routing gap where a UIKit component **port** was hand-authored and never triggered any skill, missing the reserved-`attributes` convention.

- **New commands `civictheme-skills:init` and `civictheme-skills:update`** – write/maintain a managed block in the consumer repo's `CLAUDE.md` so skill routing survives even when the agent isn't thinking about skills. Detects UIKit (`packages/sdc/`) vs Drupal sub-theme; asks when neither is detectable. Idempotent and byte-stable; never touches the rest of the file.
- **Type-selector is now a universal front door.** It detects `packages/sdc/` first and routes UIKit work to the UIKit skills up front, instead of advertising UIKit triggers and then disowning them. `packages/sdc/` is now a stated routing signal in every skill description.
- **Porting and extending now route.** `civictheme-uikit-component-generator` triggers on "pull/port/migrate/copy a component in from another repo" and on "add a new variant/type/option" to an existing component – the two phrasings that slipped past before.
- **Reserved-`attributes` rule is enforced.** `civictheme-health-check` fails any `*.component.yml` that declares `attributes` under `props`; the generators carry the same rule as a checklist item. Removed the stray `attributes` declaration from the `civictheme-sdc-generator` shared-props example.
- **SessionStart prime hook.** In a CivicTheme repo, the plugin now re-injects the routing rule into context on every session start – and, via the `compact` matcher, after each compaction, which is when a mid-task agent loses it. Silent in every other repo. This is the guard that does not depend on the agent reading CLAUDE.md.
