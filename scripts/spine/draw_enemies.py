#!/usr/bin/env python3
"""
draw_enemies.py — repaint the Peloton / Leash / Coffee enemy atlases in
the same cel-animation style as the player cast (bold ink outlines, flat
saturated fills, soft cel highlights).

Each atlas keeps the existing 48×48 frame size and frame-name structure
(idle_0..3, walk_0..3, attack_0..2, special_0..2) so EnemyFactory and the
existing animations work unchanged.

Output:
  static/assets/enemies/peloton.png + .json
  static/assets/enemies/leash.png   + .json
  static/assets/enemies/coffee.png  + .json
"""
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
from cel_paint import (
    INK,
    aa_ellipse as _aa_ellipse,
    painted_ellipse,
    darken, lighten,
)

FRAME = 48
INK_THIN = (18, 22, 28, 200)


def fill_outlined_ellipse(img, cx, cy, rx, ry, fill, thick=2):
    """Painted ellipse for small (~48px) enemy sprites — uses the same
    Magic-Design painted_ellipse helper as the player parts but with
    thinner outlines tuned for the smaller frame."""
    painted_ellipse(img, cx, cy, rx, ry, fill,
                    outline_top=max(1, thick - 1),
                    outline_bottom=thick + 1)


def cel_highlight(img, cx, cy, rx, ry, fill):
    # No-op: painted_ellipse already adds a highlight + rim. Keep the
    # symbol so existing call sites don't break.
    pass


# ── Peloton (cyclist on a road bike, top-down) ───────────────────────────

def peloton_frame(bob: int, wheel_phase: int) -> Image.Image:
    """bob: vertical offset (-1..1). wheel_phase: 0..3 cycle for wheel spokes."""
    img = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
    cx = FRAME // 2
    cy = FRAME // 2 + bob
    # Bike frame (gray with bright accent)
    BIKE_FRAME = (80, 90, 110, 255)
    BIKE_HL = (140, 152, 178, 255)
    # Wheels (front and back)
    fill_outlined_ellipse(img, cx, cy - 16, 6, 6, (40, 44, 56, 255))
    fill_outlined_ellipse(img, cx, cy - 16, 4, 4, (220, 220, 224, 255))
    fill_outlined_ellipse(img, cx, cy + 16, 6, 6, (40, 44, 56, 255))
    fill_outlined_ellipse(img, cx, cy + 16, 4, 4, (220, 220, 224, 255))
    # Wheel spokes (rotating)
    d = ImageDraw.Draw(img)
    for w_y in (cy - 16, cy + 16):
        a = wheel_phase * 0.5
        for k in range(4):
            ang = a + k * (3.14159 / 2)
            from math import cos, sin
            d.line(
                [(w_y_x := cx + int(cos(ang) * 4)), w_y + int(sin(ang) * 4),
                 cx, w_y],
                fill=INK_THIN, width=1,
            )
    # Bike body bar
    d.rectangle([cx - 1, cy - 12, cx + 1, cy + 12], fill=INK)
    # Cyclist torso (bright spandex top — alternating colors between frames)
    SPANDEX = (240, 70, 92, 255) if (wheel_phase & 1) else (60, 180, 240, 255)
    fill_outlined_ellipse(img, cx, cy, 9, 14, SPANDEX)
    cel_highlight(img, cx, cy, 9, 14, SPANDEX)
    # Helmet head
    fill_outlined_ellipse(img, cx, cy - 8, 6, 7, (240, 220, 70, 255))
    cel_highlight(img, cx, cy - 8, 6, 7, (240, 220, 70, 255))
    # Sunglasses bar
    d.line([(cx - 4, cy - 8), (cx + 4, cy - 8)], fill=INK, width=2)
    return img


# ── Leash (horizontal red retractable, screen-spanning) ──────────────────

def leash_frame(twist: int) -> Image.Image:
    """twist: 0..3 sway phase."""
    img = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
    cx = FRAME // 2
    cy = FRAME // 2 + twist - 1
    # Plastic handle (left)
    fill_outlined_ellipse(img, 8, cy, 6, 8, (220, 70, 92, 255))
    cel_highlight(img, 8, cy, 6, 8, (220, 70, 92, 255))
    # Cord stretching across (taut red line)
    d = ImageDraw.Draw(img)
    d.line([(14, cy), (FRAME - 6, cy)], fill=INK, width=4)
    d.line([(14, cy), (FRAME - 6, cy)], fill=(240, 80, 96, 255), width=2)
    # Clip on right end
    fill_outlined_ellipse(img, FRAME - 8, cy, 4, 4, (200, 200, 210, 255))
    return img


# ── Coffee (brown puddle splatter) ───────────────────────────────────────

def coffee_frame(spread: int) -> Image.Image:
    """spread: 0..3 ripple phase."""
    img = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
    cx, cy = FRAME // 2, FRAME // 2
    BROWN = (98, 60, 36, 255)
    BROWN_L = (140, 92, 56, 255)
    BROWN_FOAM = (200, 168, 132, 255)
    # Outer puddle (slightly bigger each ripple frame)
    rx = 18 + spread
    ry = 12 + spread // 2
    fill_outlined_ellipse(img, cx, cy + 2, rx, ry, BROWN)
    # Lighter inner pool
    _aa_ellipse(img, cx - 1, cy + 1, rx - 5, ry - 4, BROWN_L)
    # Foam highlights on top
    _aa_ellipse(img, cx - 4, cy - 1, 5, 2, BROWN_FOAM)
    _aa_ellipse(img, cx + 6, cy + 4, 3, 1, BROWN_FOAM)
    # Splatter dots radiating outward
    d = ImageDraw.Draw(img)
    for ang_deg in (10, 70, 130, 200, 270, 340):
        from math import cos, sin, radians
        sx = cx + int(cos(radians(ang_deg)) * (rx + 3))
        sy = cy + int(sin(radians(ang_deg)) * (ry + 2))
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=BROWN)
    return img


# ── Atlas builder ────────────────────────────────────────────────────────

def build_atlas(name: str, frames: list[Image.Image]):
    n = len(frames)
    sheet = Image.new("RGBA", (FRAME * n, FRAME), (0, 0, 0, 0))
    meta = {"frames": {}}
    frame_names = (
        ["idle_0", "idle_1", "idle_2", "idle_3"]
        + ["walk_0", "walk_1", "walk_2", "walk_3"]
        + ["attack_0", "attack_1", "attack_2"]
        + ["special_0", "special_1", "special_2"]
    )
    assert len(frames) == len(frame_names), f"need {len(frame_names)} frames"
    for i, (img, fname) in enumerate(zip(frames, frame_names)):
        sheet.paste(img, (i * FRAME, 0), img)
        meta["frames"][fname] = {
            "frame": {"x": i * FRAME, "y": 0, "w": FRAME, "h": FRAME},
            "rotated": False,
            "trimmed": False,
            "spriteSourceSize": {"x": 0, "y": 0, "w": FRAME, "h": FRAME},
            "sourceSize": {"w": FRAME, "h": FRAME},
            "duration": 100,
        }
    out_dir = Path("static/assets/enemies")
    out_dir.mkdir(parents=True, exist_ok=True)
    sheet.save(out_dir / f"{name}.png", "PNG")
    (out_dir / f"{name}.json").write_text(json.dumps(meta, indent=1))
    print(f"  wrote {name}.png + {name}.json ({n} frames)")


def main():
    # Peloton: 4 idle (gentle bob), 4 walk (faster bob + spinning wheels), 3 attack, 3 special
    peloton_frames = [
        # idle
        peloton_frame(0, 0), peloton_frame(-1, 0), peloton_frame(0, 1), peloton_frame(1, 1),
        # walk
        peloton_frame(0, 2), peloton_frame(-2, 3), peloton_frame(0, 0), peloton_frame(2, 1),
        # attack
        peloton_frame(0, 2), peloton_frame(-1, 3), peloton_frame(0, 0),
        # special
        peloton_frame(-1, 0), peloton_frame(0, 1), peloton_frame(1, 2),
    ]
    build_atlas("peloton", peloton_frames)

    # Leash: small twist phases
    leash_frames = [
        leash_frame(0), leash_frame(1), leash_frame(2), leash_frame(1),
        leash_frame(0), leash_frame(1), leash_frame(2), leash_frame(1),
        leash_frame(2), leash_frame(1), leash_frame(0),
        leash_frame(0), leash_frame(2), leash_frame(0),
    ]
    build_atlas("leash", leash_frames)

    # Coffee: ripple spread
    coffee_frames = [
        coffee_frame(0), coffee_frame(1), coffee_frame(2), coffee_frame(1),
        coffee_frame(0), coffee_frame(1), coffee_frame(2), coffee_frame(3),
        coffee_frame(2), coffee_frame(1), coffee_frame(0),
        coffee_frame(1), coffee_frame(2), coffee_frame(3),
    ]
    build_atlas("coffee", coffee_frames)


if __name__ == "__main__":
    main()
