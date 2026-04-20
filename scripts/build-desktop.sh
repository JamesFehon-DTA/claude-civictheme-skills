#!/usr/bin/env bash
# Package each skill folder under skills/ as a <name>.skill zip archive
# suitable for upload to a Claude Desktop project's skill knowledge.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PACKAGER="${PACKAGER:-python3 -m scripts.package_skill}"
OUT="$ROOT/dist/desktop"

rm -rf "$OUT"
mkdir -p "$OUT"

cd "$ROOT"
for d in skills/*/; do
  name="$(basename "$d")"
  [ "$name" = "_shared" ] && continue
  $PACKAGER "$d" "$OUT"
done
