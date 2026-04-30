#!/usr/bin/env bash
# Build all spine skeletons + atlases for the cast.
# Run from project root: bash scripts/spine/build_all.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

CHARS=(rosie charlie tia nancy katie influencer)

for name in "${CHARS[@]}"; do
    echo "── $name ───────────────────────────────────"
    out="static/assets/spine/$name/built"
    parts="static/assets/spine/$name/parts"
    config="scripts/spine/${name}_config.json"
    mkdir -p "$out"
    python3 tools/spine-animation-ai/scripts/build_spine_json.py \
        --config "$config" \
        --output "$out/$name.json" >/dev/null
    python3 tools/spine-animation-ai/scripts/make_atlas.py \
        --parts "$parts" \
        --output "$out" \
        --name "$name" >/dev/null
    python3 scripts/spine/pma_fix.py "$out" >/dev/null
    python3 scripts/spine/fix_curves.py "$out/$name.json"
done

echo "Done."
