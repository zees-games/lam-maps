#!/usr/bin/env bash
# Rebuilds every house in houses/ from its hand-laid plan in tools/layouts/ with the game's own builder, so the puzzles are dealt and proven the way the game's houses are.
#   [LAM_GAME=../mg-look-at-me] tools/build.sh [--check]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GAME="${LAM_GAME:-$ROOT/../mg-look-at-me}"
for layout in "$ROOT"/tools/layouts/*.json; do
	id="$(basename "$layout" .json)"
	python3 "$GAME/tools/build_levels.py" --layout "$layout" --id "$id" --out "$ROOT/houses/$id" "$@"
done
