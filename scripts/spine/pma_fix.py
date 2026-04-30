#!/usr/bin/env python3
"""
pma_fix.py — Premultiply a PNG's RGB by its alpha channel and add pma:true to
the atlas header. Run this AFTER make_atlas.py to make the output truly
PMA-correct and consistent across runtimes (Phaser spine-phaser plugin and
the official Spine Web Player both default to pma=true if the atlas does
not declare otherwise).

Usage:
    python3 scripts/spine/pma_fix.py <atlas_dir>

Where <atlas_dir> contains <name>.png and <name>.atlas (e.g. built/).
"""
import sys
from pathlib import Path
from PIL import Image


def premultiply(png_path: Path) -> None:
    img = Image.open(png_path).convert("RGBA")
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 255:
                continue
            af = a / 255.0
            px[x, y] = (int(r * af), int(g * af), int(b * af), a)
    img.save(png_path, "PNG")
    print(f"  premultiplied: {png_path.name}")


def add_pma_directive(atlas_path: Path) -> None:
    text = atlas_path.read_text()
    if "pma:" in text:
        print(f"  atlas already declares pma: {atlas_path.name}")
        return
    lines = text.splitlines()
    # Insert "pma: true" after the size: line (atlas header convention)
    out = []
    inserted = False
    for line in lines:
        out.append(line)
        if not inserted and line.strip().startswith("size:"):
            out.append("pma: true")
            inserted = True
    atlas_path.write_text("\n".join(out) + "\n")
    print(f"  added pma:true to {atlas_path.name}")


def main():
    if len(sys.argv) != 2:
        print("Usage: pma_fix.py <atlas_dir>")
        sys.exit(1)
    d = Path(sys.argv[1])
    if not d.is_dir():
        print(f"Not a directory: {d}")
        sys.exit(1)
    for png in d.glob("*.png"):
        premultiply(png)
    for atlas in d.glob("*.atlas"):
        add_pma_directive(atlas)
    print("Done.")


if __name__ == "__main__":
    main()
