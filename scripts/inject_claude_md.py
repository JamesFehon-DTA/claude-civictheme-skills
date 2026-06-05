#!/usr/bin/env python3
"""Write/maintain the civictheme-skills managed block in a consumer repo's CLAUDE.md.

Drives `civictheme-skills:init` and `civictheme-skills:update`. Detects the repo
archetype (UIKit vs Drupal sub-theme), then injects or re-syncs a managed block
delimited by HTML-comment markers, never touching the rest of the file.

Block body is read from the matching template in ../templates/ so the manual-paste
path and the automated path stay byte-identical.

Modes:
  init    insert the block once; no-op if a block is already present.
  update  replace the block content in place; insert it if absent.
  prime   print a terse routing primer for a SessionStart hook (silent outside a
          CivicTheme repo). With --hook-json, wraps it in the SessionStart
          additionalContext envelope. Re-injects the rule after compaction, which
          is when a mid-task agent loses it. (PreCompact cannot inject context;
          SessionStart re-fires with matcher "compact" after a compaction.)

Detection:
  - packages/sdc/ present                          -> uikit
  - a *.info.yml declaring `base theme: civictheme` -> sub-theme (records machine name)
  - neither                                         -> exit 3 (ambiguous; caller asks)

Override detection with --type uikit|sub-theme [--theme NAME] for the ask-then-rerun path.

Exit codes: 0 changed/no-op OK, 2 usage/IO error, 3 ambiguous repo (caller must ask).
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPTS_DIR.parent
TEMPLATES_DIR = PLUGIN_ROOT / "templates"

BEGIN = "<!-- BEGIN civictheme-skills (managed by civictheme-skills:update) -->"
END = "<!-- END civictheme-skills -->"

# Whole managed block, markers inclusive, anywhere in the file.
BLOCK_RE = re.compile(
    re.escape(BEGIN) + r".*?" + re.escape(END),
    re.DOTALL,
)
# Leading template header comment (the "paste only the section below" note).
HEADER_COMMENT_RE = re.compile(r"\A\s*<!--.*?-->\s*", re.DOTALL)

TEMPLATE_BY_TYPE = {
    "uikit": "consumer-uikit-claude-md.md",
    "sub-theme": "consumer-sub-theme-claude-md.md",
}


def detect_type(repo: Path) -> tuple[str | None, str | None]:
    """Return (repo_type, theme_machine_name). Type is None when ambiguous."""
    if (repo / "packages" / "sdc").is_dir():
        return "uikit", None

    name = _find_subtheme(repo)
    if name is not None:
        return "sub-theme", name

    return None, None


def _find_subtheme(repo: Path) -> str | None:
    """Machine name of a sub-theme whose *.info.yml sets `base theme: civictheme`."""
    base_theme_re = re.compile(r"^\s*base theme\s*:\s*['\"]?civictheme['\"]?\s*$", re.M)
    candidates: list[Path] = []
    # Prefer the conventional location, then fall back to a shallow repo scan.
    custom = repo / "themes" / "custom"
    if custom.is_dir():
        candidates += sorted(custom.glob("*/*.info.yml"))
    candidates += sorted(repo.glob("*.info.yml"))
    candidates += sorted(repo.glob("themes/*/*.info.yml"))

    seen: set[Path] = set()
    for info in candidates:
        info = info.resolve()
        if info in seen or not info.is_file():
            continue
        seen.add(info)
        try:
            if base_theme_re.search(info.read_text(encoding="utf-8")):
                return info.name[: -len(".info.yml")]
        except OSError:
            continue
    return None


def template_body(repo_type: str) -> str:
    """Block body = template file with its leading header comment stripped."""
    path = TEMPLATES_DIR / TEMPLATE_BY_TYPE[repo_type]
    text = path.read_text(encoding="utf-8")
    body = HEADER_COMMENT_RE.sub("", text, count=1)
    return body.strip("\n")


PRIMER = {
    "uikit": (
        "CivicTheme UIKit repo detected (packages/sdc/). Route component work through the "
        "skills – do not hand-author component files:\n"
        "- New, ported-in, or extended (new variant/type/option) component -> civictheme-uikit-component-generator\n"
        "- SCSS-only change to an existing component -> civictheme-uikit-scss-iteration\n"
        "- Validation / pre-PR check -> civictheme-health-check\n"
        "Porting or copying a component in from another repo, and adding a new variant/type, "
        "are component work – classify before copying or editing, not after. Dispatch the Skill "
        "tool; do not substitute a Read of SKILL.md. Never declare `attributes` under props (it is "
        "the reserved Drupal Attribute object); render it with "
        "`{% if attributes is defined and attributes is not null %}{{- attributes -}}{% endif %}`."
    ),
    "sub-theme": (
        "CivicTheme Drupal sub-theme detected. Run civictheme-component-type-selector to classify "
        "before any component change – including bare \"fix the X\" requests, ports, and one-file "
        "edits – then follow its routing. Dispatch the Skill tool; do not substitute a Read of "
        "SKILL.md. Never declare `attributes` under props in a *.component.yml (it is the reserved "
        "Drupal Attribute object)."
    ),
}


def build_primer(repo_type: str, hook_json: bool) -> str:
    text = PRIMER[repo_type]
    if not hook_json:
        return text
    import json

    return json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": text,
            }
        }
    )


def build_block(repo_type: str, theme: str | None) -> str:
    meta = f"type={repo_type}"
    if theme:
        meta += f"; theme={theme}"
    lines = [
        BEGIN,
        f"<!-- detected: {meta} -->",
        template_body(repo_type),
        END,
    ]
    return "\n".join(lines)


def apply_block(original: str, block: str, mode: str) -> tuple[str, str]:
    """Return (new_text, action). Collapses any duplicate blocks to exactly one."""
    matches = list(BLOCK_RE.finditer(original))

    if matches:
        if mode == "init" and len(matches) == 1:
            return original, "noop-present"
        first = matches[0]
        if len(matches) > 1:
            # Splice the canonical block at the first spot; strip every other copy.
            head = original[: first.start()]
            tail = BLOCK_RE.sub("", original[first.end():])
            return head + block + tail, "deduped"
        rebuilt = original[: first.start()] + block + original[first.end():]
        return (rebuilt, "replaced") if rebuilt != original else (original, "noop-stable")

    # No block yet: insert.
    if original.strip() == "":
        return block + "\n", "created"
    sep = "" if original.endswith("\n\n") else ("\n" if original.endswith("\n") else "\n\n")
    return original + sep + block + "\n", "inserted"


def summarise(path: Path, before: str, after: str, action: str) -> str:
    rel = path
    if action == "noop-present":
        return f"{rel}: managed block already present – no change (run `update` to re-sync)."
    if action == "noop-stable":
        return f"{rel}: managed block already current – no change."
    diff = "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile=f"a/{rel.name}",
            tofile=f"b/{rel.name}",
        )
    )
    verb = {
        "created": "created CLAUDE.md with managed block",
        "inserted": "inserted managed block",
        "replaced": "re-synced managed block",
        "deduped": "collapsed duplicate managed blocks to one",
    }[action]
    return f"{rel}: {verb}.\n\n{diff}" if diff else f"{rel}: {verb}."


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["init", "update", "prime"], required=True)
    ap.add_argument("--repo", default=".", help="target repo root (default: cwd)")
    ap.add_argument("--type", choices=["uikit", "sub-theme"], help="override detection")
    ap.add_argument("--theme", help="theme machine name (with --type sub-theme)")
    ap.add_argument(
        "--hook-json",
        action="store_true",
        help="prime mode: emit the SessionStart additionalContext JSON envelope",
    )
    args = ap.parse_args(argv)

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        if args.mode == "prime":
            return 0  # hooks must be silent no-ops on a bad/zero cwd
        print(f"FAIL: --repo {repo} is not a directory", file=sys.stderr)
        return 2

    if args.type:
        repo_type, theme = args.type, args.theme
        if repo_type == "sub-theme" and not theme:
            _, theme = "sub-theme", _find_subtheme(repo)
    else:
        repo_type, theme = detect_type(repo)

    if args.mode == "prime":
        # Silent no-op outside a detectable CivicTheme repo, so the hook is
        # inert in every other project the plugin is installed into.
        if repo_type is not None:
            print(build_primer(repo_type, args.hook_json))
        return 0

    if repo_type is None:
        print(
            "AMBIGUOUS: could not detect repo type.\n"
            "  - No packages/sdc/ (UIKit signal).\n"
            "  - No *.info.yml with `base theme: civictheme` (sub-theme signal).\n"
            "Ask the user, then re-run with --type uikit|sub-theme.",
            file=sys.stderr,
        )
        return 3

    claude_md = repo / "CLAUDE.md"
    before = claude_md.read_text(encoding="utf-8") if claude_md.exists() else ""
    block = build_block(repo_type, theme)
    after, action = apply_block(before, block, args.mode)

    if after != before:
        claude_md.write_text(after, encoding="utf-8")

    meta = f"type={repo_type}" + (f", theme={theme}" if theme else "")
    print(f"detected: {meta}")
    print(summarise(claude_md, before, after, action))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
