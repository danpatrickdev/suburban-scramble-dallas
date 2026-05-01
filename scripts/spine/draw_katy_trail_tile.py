#!/usr/bin/env python3
"""
draw_katy_trail_tile.py — repaint the Katy Trail floor tile in a clean
2D-animation style. Replaces the noisier pixel-art version with smooth,
softly textured grass + concrete + crushed-granite paths.

The tile is 256×256 (4× the previous 64×64 so the texture reads crisper at
any scale), seamless top↔bottom, lays out:
  - left grass strip
  - concrete cycling path with thin yellow centerline
  - thin grass divider
  - crushed-granite pedestrian path
  - right grass strip

Output: static/assets/tiles/katy_trail.png
"""
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path
import random

random.seed(42)  # deterministic output

OUT = Path("static/assets/tiles/katy_trail.png")
W, H = 256, 256

# Layout (column ranges in pixels). Real Katy Trail layout: grass | bike path |
# tiny divider | pedestrian path | grass.
GRASS_L_END = 16
BIKE_END = 124
DIVIDER_END = 132
PED_END = 240
# tail end → grass


def main():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # ── Grass base ───────────────────────────────────────────────────────
    GRASS = (108, 158, 88, 255)
    GRASS_DARK = (84, 128, 70, 255)
    GRASS_LIGHT = (132, 180, 104, 255)
    d.rectangle([0, 0, W - 1, H - 1], fill=GRASS)

    # ── Cycling path (concrete) ──────────────────────────────────────────
    CONCRETE = (212, 210, 200, 255)
    CONCRETE_S = (188, 186, 178, 255)
    d.rectangle([GRASS_L_END, 0, BIKE_END - 1, H - 1], fill=CONCRETE)

    # ── Pedestrian path (crushed granite) ────────────────────────────────
    GRANITE = (210, 180, 140, 255)
    GRANITE_S = (186, 156, 116, 255)
    d.rectangle([DIVIDER_END, 0, PED_END - 1, H - 1], fill=GRANITE)

    # ── Yellow centerline on the bike path (dashed) ──────────────────────
    YELLOW = (240, 196, 80, 255)
    cx_bike = (GRASS_L_END + BIKE_END) // 2
    for y in range(0, H, 32):
        d.rectangle([cx_bike - 2, y + 4, cx_bike + 2, y + 24], fill=YELLOW)

    # ── Subtle concrete shading bands (lateral, 2D-anim cel-shading) ─────
    for y in range(0, H, 64):
        d.rectangle([GRASS_L_END, y + 28, BIKE_END - 1, y + 32], fill=CONCRETE_S)

    # ── Granite scatter (cel-shaded gravel dots) ─────────────────────────
    for _ in range(80):
        x = random.randint(DIVIDER_END + 4, PED_END - 6)
        y = random.randint(2, H - 4)
        size = random.choice([1, 1, 1, 2])
        c = random.choice([GRANITE_S, (160, 134, 96, 255), (230, 200, 160, 255)])
        d.rectangle([x, y, x + size, y + size], fill=c)

    # ── Grass texture (cel-shaded blade clusters, no pixel noise) ────────
    def grass_strip(x0, x1):
        for _ in range(int((x1 - x0) * 0.6)):
            x = random.randint(x0, x1 - 2)
            y = random.randint(0, H - 4)
            color = random.choice([GRASS_DARK, GRASS_LIGHT, GRASS_LIGHT])
            d.rectangle([x, y, x + 1, y + 2], fill=color)

    grass_strip(0, GRASS_L_END)
    grass_strip(BIKE_END, DIVIDER_END)
    grass_strip(PED_END, W)

    # ── Path edge highlights (sharp 2D-anim line) ────────────────────────
    EDGE = (60, 70, 50, 220)
    d.line([(GRASS_L_END, 0), (GRASS_L_END, H)], fill=EDGE, width=1)
    d.line([(BIKE_END - 1, 0), (BIKE_END - 1, H)], fill=EDGE, width=1)
    d.line([(DIVIDER_END, 0), (DIVIDER_END, H)], fill=EDGE, width=1)
    d.line([(PED_END - 1, 0), (PED_END - 1, H)], fill=EDGE, width=1)

    # ── Soft gradient between bike path and grass divider for depth ──────
    # Slight lighter ribbon down the granite path (sun catches the gravel)
    SUN = (235, 215, 170, 60)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle([DIVIDER_END + 6, 0, PED_END - 6, H - 1], fill=SUN)
    overlay = overlay.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, overlay)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, "PNG")
    print(f"wrote {OUT}  ({W}×{H})")


if __name__ == "__main__":
    main()
