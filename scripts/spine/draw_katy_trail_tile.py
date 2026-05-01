#!/usr/bin/env python3
"""
draw_katy_trail_tile.py — paint the Katy Trail floor tile in a Magic
Design Studios painted-2D style: each surface gets a base color plus
soft gaussian-blurred light/shadow bands, painted detail clusters
(grass clumps + pebble groups), crisp ink-line edges, and an overall
warm sun-ribbon overlay for atmospheric depth.

Output: static/assets/tiles/katy_trail.png  (256×256 seamless top↔bottom)
"""
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from cel_paint import (
    INK,
    painterly_field,
    brush_dabs,
    aa_ellipse,
    painted_ellipse,
    darken, lighten,
)

OUT = Path("static/assets/tiles/katy_trail.png")
W, H = 256, 256

# Layout columns
GRASS_L_END = 18
BIKE_END = 124
DIVIDER_END = 134
PED_END = 240


def main():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # Grass field (full-width base — gets covered by the path strips)
    GRASS = (76, 144, 64, 255)
    painterly_field(img, 0, W, 0, H, GRASS,
                    light=lighten(GRASS, 0.30),
                    dark=darken(GRASS, 0.25),
                    blur=24)

    # Concrete bike path
    CONCRETE = (212, 210, 198, 255)
    painterly_field(img, GRASS_L_END, BIKE_END, 0, H, CONCRETE,
                    light=lighten(CONCRETE, 0.18),
                    dark=darken(CONCRETE, 0.18),
                    blur=22)

    # Crushed-granite pedestrian path (warmer, sandier)
    GRANITE = (218, 180, 130, 255)
    painterly_field(img, DIVIDER_END, PED_END, 0, H, GRANITE,
                    light=lighten(GRANITE, 0.20),
                    dark=darken(GRANITE, 0.22),
                    blur=22)

    # ── Painted yellow centerline dashes on the bike path ────────────────
    d = ImageDraw.Draw(img)
    YELLOW = (252, 200, 70, 255)
    YELLOW_S = darken(YELLOW, 0.30)
    cx_bike = (GRASS_L_END + BIKE_END) // 2
    for y in range(0, H, 36):
        # Hand-painted feel: shadow under, base on top, narrow highlight
        d.rounded_rectangle([cx_bike - 4, y + 7, cx_bike + 4, y + 27], radius=3, fill=YELLOW_S)
        d.rounded_rectangle([cx_bike - 3, y + 5, cx_bike + 3, y + 25], radius=3, fill=YELLOW)
        d.rounded_rectangle([cx_bike - 1, y + 6, cx_bike + 1, y + 14], radius=1, fill=lighten(YELLOW, 0.30))

    # ── Cel-ink edges where surfaces meet (variable weight: thicker on the
    #    grass side, thinner on the path side, like brushwork) ────────────
    def painted_edge(x):
        # Two-pass line: thicker shadow line offset to grass, then crisp ink
        d.line([(x + 1, 0), (x + 1, H)], fill=darken(GRASS, 0.5), width=3)
        d.line([(x, 0), (x, H)], fill=INK, width=2)

    painted_edge(GRASS_L_END)
    painted_edge(BIKE_END - 1)
    painted_edge(DIVIDER_END)
    painted_edge(PED_END - 1)

    # ── Painted detail clusters ──────────────────────────────────────────
    def grass_clump(x, y):
        # Multi-tone clump: dark base, mid blade, light highlight
        aa_ellipse(img, x, y + 2, 6, 3, darken(GRASS, 0.45))
        aa_ellipse(img, x - 1, y, 5, 3, GRASS)
        aa_ellipse(img, x + 1, y - 1, 4, 2, lighten(GRASS, 0.30))

    def pebble(x, y):
        aa_ellipse(img, x, y + 1, 3, 2, darken(GRANITE, 0.30))
        aa_ellipse(img, x, y, 2, 2, GRANITE)
        aa_ellipse(img, x, y - 1, 1, 1, lighten(GRANITE, 0.40))

    # Grass clumps along the LEFT strip (vary positions)
    left_clumps = [(8, 24), (6, 78), (10, 130), (5, 188), (9, 232)]
    # Divider clumps
    div_x = (BIKE_END + DIVIDER_END) // 2
    div_clumps = [(div_x, 30), (div_x, 92), (div_x - 1, 156), (div_x + 1, 214)]
    # Right strip
    right_clumps = [(W - 8, 18), (W - 11, 70), (W - 6, 124), (W - 10, 178), (W - 7, 230)]

    for x, y in left_clumps + div_clumps + right_clumps:
        grass_clump(x, y)

    # Pebble clusters in the granite path (irregular grouping)
    pebbles = [(150, 30), (158, 36), (165, 32),
               (190, 70), (198, 78),
               (155, 110), (165, 116),
               (210, 142), (218, 148), (212, 154),
               (170, 188), (178, 192),
               (200, 220), (208, 228), (200, 234)]
    for x, y in pebbles:
        pebble(x, y)

    # ── Warm sun-ribbon overlay along granite path for atmosphere ────────
    SUN_OVERLAY = (255, 220, 160, 50)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rectangle(
        [DIVIDER_END + 8, 30, PED_END - 8, H - 30],
        fill=SUN_OVERLAY,
    )
    overlay = overlay.filter(ImageFilter.GaussianBlur(20))
    img.alpha_composite(overlay)

    # ── Subtle vignette at the very tile edges so the seam doesn't pop ───
    # (only blurred horizontal — vertical seams are at top/bottom of tile
    # and we DO want them to repeat cleanly so no top/bottom vignette)
    edge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ed = ImageDraw.Draw(edge)
    ed.rectangle([0, 0, 6, H], fill=(0, 0, 0, 50))
    ed.rectangle([W - 6, 0, W, H], fill=(0, 0, 0, 50))
    edge = edge.filter(ImageFilter.GaussianBlur(8))
    img.alpha_composite(edge)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG")
    print(f"wrote {OUT}  ({W}×{H})")


if __name__ == "__main__":
    main()
