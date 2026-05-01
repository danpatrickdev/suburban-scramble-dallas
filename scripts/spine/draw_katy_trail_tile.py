#!/usr/bin/env python3
"""
draw_katy_trail_tile.py — paint the Katy Trail floor tile as a SINGLE
trail (not a multi-lane road).

The tile is 540×256 wide (full game width) so it only tiles vertically.
Layout: thin grass strip on each side, one wide concrete trail in the
middle with a soft dashed centerline. Painted-style with multi-tone
shading, no pixel scatter.

Output: static/assets/tiles/katy_trail.png
"""
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from cel_paint import (
    INK,
    painterly_field,
    aa_ellipse,
    darken, lighten,
)

OUT = Path("static/assets/tiles/katy_trail.png")
W, H = 540, 256

GRASS_L_END = 36
GRASS_R_START = W - 36


def main():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    # Grass borders (left + right)
    GRASS = (76, 144, 64, 255)
    painterly_field(img, 0, GRASS_L_END, 0, H, GRASS,
                    light=lighten(GRASS, 0.30),
                    dark=darken(GRASS, 0.25),
                    blur=18)
    painterly_field(img, GRASS_R_START, W, 0, H, GRASS,
                    light=lighten(GRASS, 0.30),
                    dark=darken(GRASS, 0.25),
                    blur=18)

    # Trail surface — one wide concrete strip
    CONCRETE = (212, 210, 198, 255)
    painterly_field(img, GRASS_L_END, GRASS_R_START, 0, H, CONCRETE,
                    light=lighten(CONCRETE, 0.18),
                    dark=darken(CONCRETE, 0.18),
                    blur=24)

    d = ImageDraw.Draw(img)

    # Faint dashed centerline (subtle — it's a TRAIL, not a road)
    YELLOW = (252, 200, 70, 255)
    YELLOW_S = darken(YELLOW, 0.30)
    cx_trail = (GRASS_L_END + GRASS_R_START) // 2
    for y in range(0, H, 44):
        d.rounded_rectangle([cx_trail - 3, y + 9, cx_trail + 3, y + 31], radius=3, fill=YELLOW_S)
        d.rounded_rectangle([cx_trail - 2, y + 7, cx_trail + 2, y + 29], radius=3, fill=YELLOW)
        d.rounded_rectangle([cx_trail - 1, y + 8, cx_trail + 1, y + 16], radius=1, fill=lighten(YELLOW, 0.30))

    # Crisp ink edges where grass meets trail
    def painted_edge(x):
        d.line([(x + 1, 0), (x + 1, H)], fill=darken(GRASS, 0.5), width=3)
        d.line([(x, 0), (x, H)], fill=INK, width=2)

    painted_edge(GRASS_L_END)
    painted_edge(GRASS_R_START - 1)

    # Painted grass clumps along the edges
    def grass_clump(x, y):
        aa_ellipse(img, x, y + 2, 6, 3, darken(GRASS, 0.45))
        aa_ellipse(img, x - 1, y, 5, 3, GRASS)
        aa_ellipse(img, x + 1, y - 1, 4, 2, lighten(GRASS, 0.30))

    # Tan worn-trail markings down the concrete (subtle painted dabs
    # suggesting foot traffic / wear, not pixel noise)
    WORN = (190, 160, 110, 90)
    for y in (40, 110, 180, 230):
        x = cx_trail - 80 + ((y * 3) % 160)
        ax = (x % 30) - 15
        aa_ellipse(img, x + ax, y, 8, 3, WORN)
        aa_ellipse(img, x + ax + 36, y + 12, 6, 2, WORN)

    # Grass clumps in left and right strips
    for y in (28, 96, 164, 224):
        grass_clump(14, y)
        grass_clump(W - 14, y + 16)
        grass_clump(28, y + 8)
        grass_clump(W - 28, y - 4)

    # Subtle warm sun overlay across the trail (atmospheric)
    SUN = (255, 220, 160, 36)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rectangle(
        [GRASS_L_END + 16, 28, GRASS_R_START - 16, H - 28],
        fill=SUN,
    )
    overlay = overlay.filter(ImageFilter.GaussianBlur(28))
    img.alpha_composite(overlay)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG")
    print(f"wrote {OUT}  ({W}×{H})")


if __name__ == "__main__":
    main()
