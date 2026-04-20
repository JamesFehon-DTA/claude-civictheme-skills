#!/usr/bin/env python3
"""Package a Claude skill directory as a .skill zip archive.

Mirrors the behaviour of the canonical `package_skill.py` shipped with the
Anthropic skill-creator skill: each `.skill` archive is a standard zip file
whose top-level directory is the skill folder, containing `SKILL.md` plus all
supporting files. File symlinks inside the skill directory are dereferenced so
every archive is self-contained.

Excluded: `__pycache__/`, `node_modules/`, `.DS_Store`, `*.pyc`, and a
top-level `evals/` directory inside the skill folder.

Usage:
    python -m scripts.package_skill <skill_dir> <output_dir>
    python scripts/package_skill.py <skill_dir> <output_dir>
"""
from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

EXCLUDE_DIR_NAMES = {"__pycache__", "node_modules"}
EXCLUDE_FILE_NAMES = {".DS_Store"}
EXCLUDE_SUFFIXES = {".pyc"}
EXCLUDE_TOPLEVEL = {"evals"}


def _should_exclude(rel_parts: tuple[str, ...], name: str) -> bool:
    if name in EXCLUDE_FILE_NAMES:
        return True
    if any(part in EXCLUDE_DIR_NAMES for part in rel_parts):
        return True
    if rel_parts and rel_parts[0] in EXCLUDE_TOPLEVEL:
        return True
    if Path(name).suffix in EXCLUDE_SUFFIXES:
        return True
    return False


def package(skill_dir: Path, output_dir: Path) -> Path:
    skill_dir = skill_dir.resolve()
    if not skill_dir.is_dir():
        raise SystemExit(f"error: {skill_dir} is not a directory")
    if not (skill_dir / "SKILL.md").is_file():
        raise SystemExit(f"error: {skill_dir}/SKILL.md not found")

    output_dir.mkdir(parents=True, exist_ok=True)
    archive_name = skill_dir.name
    out_path = output_dir / f"{archive_name}.skill"

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(skill_dir.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(skill_dir)
            if _should_exclude(rel.parts[:-1], path.name):
                continue
            arcname = Path(archive_name, *rel.parts).as_posix()
            zf.write(path, arcname)
    return out_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Package a Claude skill directory into a .skill zip archive."
    )
    parser.add_argument("skill_dir", type=Path, help="Path to the skill folder.")
    parser.add_argument("output_dir", type=Path, help="Directory to write <name>.skill into.")
    args = parser.parse_args(argv)
    out = package(args.skill_dir, args.output_dir)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
