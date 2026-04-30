#!/usr/bin/env python3
"""
fix_curves.py — Strip malformed bezier `curve` arrays from multi-channel bone
timelines (translate, scale, shear) in a Spine 4.2 JSON skeleton.

Background: the Spine 4.2 JSON loader expects bezier curves on multi-channel
bone timelines to have N*4 values (one quad per channel). The Genielabs
build_spine_json.py pipeline emits a single 4-value curve regardless of
channel count, which is correct for single-channel `rotate` but breaks
`translate`/`scale`/`shear`. The runtime reads `curve[4..7]` for the second
channel and gets `undefined`, which propagates as NaN through the bone's
applied transform, world transform, and finally the rendered vertex
positions — producing a silently invisible skeleton.

Cheap, correct fix: drop `curve` from multi-channel keyframes. Linear
interpolation reads fine for our subtle motion (idle bob, walk wag, etc.).
If we ever need eased curves on translate, switch to channel-split timelines
(`translatex`, `translatey`) or expand `curve` to 8 values.

Usage:
    python3 scripts/spine/fix_curves.py <skeleton.json>
"""
import json
import sys
from pathlib import Path

MULTI = {"translate", "scale", "shear"}


def fix(p: Path) -> int:
    with p.open() as f:
        data = json.load(f)
    fixed = 0
    for anim in data.get("animations", {}).values():
        for bone_anims in anim.get("bones", {}).values():
            for tl_name, keys in bone_anims.items():
                if tl_name not in MULTI:
                    continue
                for k in keys:
                    if "curve" in k and isinstance(k["curve"], list) and len(k["curve"]) == 4:
                        del k["curve"]
                        fixed += 1
    with p.open("w") as f:
        json.dump(data, f, indent=2)
    return fixed


def main():
    if len(sys.argv) != 2:
        print("Usage: fix_curves.py <skeleton.json>")
        sys.exit(1)
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"Not a file: {path}")
        sys.exit(1)
    n = fix(path)
    print(f"stripped {n} malformed curves from {path.name}")


if __name__ == "__main__":
    main()
