#!/usr/bin/env python3
"""
draw_katy_trail_tile.py — paint the Katy Trail floor tile in a Humongous-
Entertainment painted-background style: flat saturated color fields, soft
gradient shading inside the path, crisp dark cel-ink edges, no pixel
scatter noise.

Output: static/assets/tiles/katy_trail.png  (256×256 seamless top↔bottom)
"""
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path

OUT = Path("static/assets/tiles/katy_trail.png")
W, H = 256, 256

# Layout (column ranges in pixels). Real Katy Trail layout, simplified.
GRASS_L_END = 18
BIKE_END = 124
DIVIDER_END = 134
PED_END = 240
INK = (28, 32, 24, 255)


def paint_field(img, x0, x1, base, light, dark):
    """Fill a vertical strip with flat base color + soft horizontal cel
    bands of light/dark to suggest painted depth, no per-pixel noise."""
    d = ImageDraw.Draw(img)
    d.rectangle([x0, 0, x1 - 1, H - 1], fill=base)
    # Soft band overlay — wide flat ribbons at fixed Y, slightly lighter
    # near the top of each tile and slightly darker near the middle.
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    # light band (sun catch)
    od.rectangle([x0, 18, x1 - 1, 56], fill=(*light[:3], 60))
    # darker band (shadow seam)
    od.rectangle([x0, 130, x1 - 1, 168], fill=(*dark[:3], 60))
    overlay = overlay.filter(ImageFilter.GaussianBlur(14))
    img.alpha_composite(overlay)


def main():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # ── Grass field ──────────────────────────────────────────────────────
    GRASS = (88, 156, 78, 255)
    GRASS_L = (134, 196, 110, 255)
    GRASS_D = (62, 116, 60, 255)
    paint_field(img, 0, W, GRASS, GRASS_L, GRASS_D)

    # ── Cycling path (concrete) ──────────────────────────────────────────
    CONCRETE = (220, 218, 208, 255)
    CONCRETE_L = (240, 238, 228, 255)
    CONCRETE_D = (188, 184, 170, 255)
    paint_field(img, GRASS_L_END, BIKE_END, CONCRETE, CONCRETE_L, CONCRETE_D)

    # ── Pedestrian path (crushed granite) ────────────────────────────────
    GRANITE = (220, 188, 138, 255)
    GRANITE_L = (240, 212, 168, 255)
    GRANITE_D = (188, 152, 102, 255)
    paint_field(img, DIVIDER_END, PED_END, GRANITE, GRANITE_L, GRANITE_D)

    # ── Yellow centerline on the bike path (hand-painted dashes) ─────────
    d = ImageDraw.Draw(img)
    YELLOW = (252, 200, 70, 255)
    YELLOW_S = (200, 144, 38, 255)
    cx_bike = (GRASS_L_END + BIKE_END) // 2
    for y in range(0, H, 36):
        # Shadow under dash for cel depth
        d.rounded_rectangle([cx_bike - 3, y + 6, cx_bike + 3, y + 26], radius=2, fill=YELLOW_S)
        d.rounded_rectangle([cx_bike - 2, y + 5, cx_bike + 2, y + 25], radius=2, fill=YELLOW)

    # ── Crisp dark cel-ink edges where surfaces meet ─────────────────────
    edge_pad = 1
    d.line([(GRASS_L_END, 0), (GRASS_L_END, H)], fill=INK, width=2)
    d.line([(BIKE_END, 0), (BIKE_END, H)], fill=INK, width=2)
    d.line([(DIVIDER_END, 0), (DIVIDER_END, H)], fill=INK, width=2)
    d.line([(PED_END, 0), (PED_END, H)], fill=INK, width=2)

    # ── Small painted detail clusters (clumps of grass + gravel pebbles) ─
    # Far less frequent than the noise scatter; each cluster is a
    # cel-shaded 2-color blob.
    def grass_clump(x, y):
        d.ellipse([x - 4, y - 2, x + 4, y + 2], fill=GRASS_D)
        d.ellipse([x - 2, y - 4, x + 4, y + 1], fill=GRASS_L)

    def pebble(x, y, sz=2):
        d.ellipse([x - sz, y - sz, x + sz, y + sz], fill=GRANITE_D)
        d.ellipse([x - sz + 1, y - sz + 1, x, y - 1], fill=GRANITE_L)

    # Grass clumps in left strip
    for y in (24, 80, 138, 198):
        grass_clump(8, y)
    # Grass clumps in divider
    for y in (40, 110, 188):
        grass_clump((BIKE_END + DIVIDER_END) // 2, y)
    # Grass clumps in right strip
    for y in (32, 96, 156, 222):
        grass_clump(W - 8, y)
    # Painted gravel pebbles in pedestrian path (sparse, intentional)
    for x, y in [(150, 28), (188, 70), (158, 108), (210, 142), (172, 184), (200, 220)]:
        pebble(x, y)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG")
    print(f"wrote {OUT}  ({W}×{H})")


if __name__ == "__main__":
    main()
