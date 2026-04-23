#!/usr/bin/env python3
"""Static checks for the skills in this repo.

Runs without network or LLM calls — validates structure only.
Exits non-zero on any failure so it can gate CI.

Checks:
- SKILL.md exists, has valid YAML frontmatter with name + description
- frontmatter `name` matches directory
- every `references/*.md` cited in SKILL.md exists, and vice versa (no orphans)
- router.md references every handler directory
- every markdown relative link across the repo resolves to a real file
- every fenced ```yaml block parses as valid YAML
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FAIL: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"
ROUTER_NAME = "civictheme-component-type-selector"
ROUTER = SKILLS / ROUTER_NAME / "SKILL.md"
SKIP_SKILL_DIRS = {"_shared"}

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
REF_CITATION_RE = re.compile(r"`references/([a-zA-Z0-9_\-.]+\.md)`")
MD_LINK_RE = re.compile(r"(?<!\!)\[[^\]]+\]\(([^)]+)\)")
YAML_FENCE_RE = re.compile(r"```ya?ml\n(.*?)```", re.DOTALL)


def parse_frontmatter(text: str) -> dict | None:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        return {"_parse_error": str(e)}


def check_skill(skill_dir: Path, errors: list[str]) -> None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append(f"{skill_dir.name}: SKILL.md missing")
        return

    text = skill_md.read_text()
    fm = parse_frontmatter(text)
    if fm is None:
        errors.append(f"{skill_md}: no YAML frontmatter")
        return
    if "_parse_error" in fm:
        errors.append(f"{skill_md}: frontmatter YAML invalid: {fm['_parse_error']}")
        return

    for field in ("name", "description"):
        if not fm.get(field):
            errors.append(f"{skill_md}: frontmatter missing '{field}'")

    if fm.get("name") and fm["name"] != skill_dir.name:
        errors.append(
            f"{skill_md}: name '{fm['name']}' does not match directory '{skill_dir.name}'"
        )

    cited = set(REF_CITATION_RE.findall(text))
    refs_dir = skill_dir / "references"
    present = {p.name for p in refs_dir.glob("*.md")} if refs_dir.exists() else set()

    for missing in cited - present:
        errors.append(f"{skill_md}: cites references/{missing} but file does not exist")
    for orphan in present - cited:
        errors.append(
            f"{skill_md}: references/{orphan} exists but is not cited in SKILL.md"
        )


def check_router(errors: list[str]) -> None:
    # Invariant: the router's SKILL.md must mention every skill directory by name,
    # so no handler becomes an orphan. Three skills are deliberately *not* routed
    # through the type-selector — they are direct entry points, named only in the
    # router's §Out of scope / §Related skills exit notes:
    #   - civictheme-uikit-component-generator (UIKit authoring)
    #   - civictheme-uikit-scss-iteration      (UIKit SCSS edits)
    #   - civictheme-health-check              (diagnostics)
    # Because this check is a plain substring search over the whole SKILL.md,
    # those exit-note mentions satisfy the invariant without making the skills
    # part of `recommended_next_skill`. If a future refactor narrows the check
    # to routing-table or enum membership, introduce an allowlist for these
    # three skills rather than forcing them into the classifier enum.
    if not ROUTER.exists():
        errors.append(f"{ROUTER}: missing")
        return
    handler_names = {
        p.name for p in SKILLS.iterdir()
        if p.is_dir() and p.name not in SKIP_SKILL_DIRS and p.name != ROUTER_NAME
    }
    text = ROUTER.read_text()
    for name in handler_names:
        if name not in text:
            errors.append(f"{ROUTER.relative_to(REPO)}: does not reference handler '{name}'")


SKIP_DIRS = {".git", ".claude", "node_modules"}


def iter_md_files():
    for md in REPO.rglob("*.md"):
        if SKIP_DIRS.intersection(md.parts):
            continue
        yield md


def check_markdown_links(errors: list[str]) -> None:
    """Every relative markdown link must resolve to a real file in the repo."""
    for md in iter_md_files():
        text = md.read_text()
        for target in MD_LINK_RE.findall(text):
            target = target.split()[0]  # strip optional "title"
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            resolved = (md.parent / path_part).resolve()
            if not resolved.exists():
                rel = md.relative_to(REPO)
                errors.append(f"{rel}: broken link → {target}")


PLACEHOLDER_RE = re.compile(r"\[[A-Z][A-Z0-9_]+\]|<[^>]+>")


def check_yaml_blocks(errors: list[str]) -> None:
    """Every fenced yaml block must parse. Skips blocks with template placeholders."""
    for md in iter_md_files():
        text = md.read_text()
        for i, block in enumerate(YAML_FENCE_RE.findall(text), 1):
            if PLACEHOLDER_RE.search(block):
                continue
            try:
                yaml.safe_load(block)
            except yaml.YAMLError as e:
                rel = md.relative_to(REPO)
                first_line = str(e).splitlines()[0]
                errors.append(f"{rel}: yaml block #{i} does not parse: {first_line}")


def main() -> int:
    errors: list[str] = []
    if not SKILLS.exists():
        print(f"FAIL: {SKILLS} does not exist", file=sys.stderr)
        return 1

    for skill_dir in sorted(SKILLS.iterdir()):
        if skill_dir.is_dir() and skill_dir.name not in SKIP_SKILL_DIRS:
            check_skill(skill_dir, errors)

    check_router(errors)
    check_markdown_links(errors)
    check_yaml_blocks(errors)

    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        print(f"\n{len(errors)} issue(s) found", file=sys.stderr)
        return 1

    print("OK: all skill checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
