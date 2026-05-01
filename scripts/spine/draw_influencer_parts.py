#!/usr/bin/env python3
"""
draw_influencer_parts.py — generate the Influencer (Main Character) boss
body parts as 256×256 transparent PNGs for the Spine pipeline.

Top-down view: she stands facing DOWN (toward the player) and is mid-selfie
with her phone extended to her upper-right. Pajama-Sam-style flat saturated
fills with thick outlines.

Parts (z-order, bottom → top):
  hair-back       — long brunette ponytail fanned out behind her head
  legs            — black leggings, two ovals
  arm-phone       — outstretched right arm
  body            — pink crop top torso
  head            — face from above + bangs
  phone           — white iPhone, screen lit

Outputs to: static/assets/spine/influencer/parts/<name>.png
Plus a reference render at: static/assets/spine/influencer/reference.png
"""
from PIL import Image, ImageDraw
from pathlib import Path

OUT = Path("static/assets/spine/influencer/parts")
REF = Path("static/assets/spine/influencer/reference.png")
import sys
sys.path.insert(0, str(Path(__file__).parent))
from cel_paint import (
    INK as OUTLINE,
    aa_ellipse as ellipse,
    painted_ellipse,
    painted_rounded_rect,
    darken, lighten,
)

W, H = 256, 256

# Palette — saturated cel colors, Magic Design Studios vibe.
SKIN = (250, 215, 180, 255)
SKIN_S = (215, 175, 140, 255)
HAIR = (78, 44, 24, 255)
HAIR_H = (135, 88, 50, 255)
PINK = (255, 128, 178, 255)
PINK_S = (215, 80, 128, 255)
BLACK = (24, 24, 30, 255)
BLACK_H = (70, 70, 80, 255)
WHITE = (252, 252, 250, 255)
SCREEN = (140, 220, 255, 255)
GOLD = (255, 200, 70, 255)
EYE = (38, 26, 20, 255)
LIP = (220, 70, 96, 255)


def new_part() -> Image.Image:
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def filled_outlined_ellipse(img, cx, cy, rx, ry, fill, outline=OUTLINE, thick=6):
    painted_ellipse(img, cx, cy, rx, ry, fill,
                    outline_top=max(2, thick - 2),
                    outline_bottom=thick + 1)


def rect(img, x, y, w, h, color):
    ImageDraw.Draw(img).rectangle([x, y, x + w - 1, y + h - 1], fill=color)


def filled_outlined_rect(img, x, y, w, h, fill, outline=OUTLINE, thick=4):
    painted_rounded_rect(img, x, y, w, h, fill, radius=max(2, min(w, h) // 4))


# ── Parts ─────────────────────────────────────────────────────────────────

def draw_hair_back():
    """Long ponytail spilling DOWN (away from camera, behind head)."""
    img = new_part()
    cx, cy = W // 2, H // 2
    # Thick ponytail trail flowing down past torso
    filled_outlined_ellipse(img, cx, cy + 36, 26, 60, HAIR)
    # Tip — slightly narrower
    filled_outlined_ellipse(img, cx, cy + 92, 18, 22, HAIR)
    # Highlight strands
    rect(img, cx - 6, cy + 4, 2, 100, HAIR_H)
    rect(img, cx + 4, cy + 14, 2, 90, HAIR_H)
    # Hair tie
    filled_outlined_rect(img, cx - 14, cy + 70, 28, 6, PINK_S, OUTLINE, 2)
    return img


def draw_legs():
    """Two leg ovals in black leggings, viewed top-down (slight stance)."""
    img = new_part()
    cx, cy = W // 2, H // 2
    # Left leg
    filled_outlined_ellipse(img, cx - 22, cy + 4, 16, 52, BLACK)
    # Right leg
    filled_outlined_ellipse(img, cx + 22, cy + 4, 16, 52, BLACK)
    # Sneaker tips (white) at the bottom (toward player)
    filled_outlined_ellipse(img, cx - 22, cy + 50, 14, 10, WHITE)
    filled_outlined_ellipse(img, cx + 22, cy + 50, 14, 10, WHITE)
    # Pink swoosh on each shoe
    rect(img, cx - 28, cy + 50, 12, 2, PINK)
    rect(img, cx + 18, cy + 50, 12, 2, PINK)
    # Subtle highlight on legs
    ellipse(img, cx - 18, cy - 14, 4, 30, BLACK_H)
    ellipse(img, cx + 26, cy - 14, 4, 30, BLACK_H)
    return img


def draw_body():
    """Torso in pink Lululemon crop top (top-down) with arms tucked."""
    img = new_part()
    cx, cy = W // 2, H // 2
    # Torso ellipse
    filled_outlined_ellipse(img, cx, cy, 50, 64, PINK)
    # Crop-top hem highlight (lighter band)
    rect(img, cx - 44, cy + 50, 88, 4, PINK_S)
    # Brand swoosh accent
    rect(img, cx - 8, cy - 14, 16, 3, WHITE)
    # Subtle midline shading
    rect(img, cx - 1, cy - 30, 2, 60, PINK_S)
    # Apple Watch peeking on left wrist (right side of frame as she's flipped)
    filled_outlined_rect(img, cx - 56, cy - 4, 10, 14, BLACK, OUTLINE, 2)
    rect(img, cx - 54, cy - 2, 6, 10, SCREEN)
    return img


def draw_arm_phone():
    """Outstretched right arm — extends from shoulder UPWARD (camera view).

    Bone anchors at the SHOULDER end (bottom of this image). The arm goes UP
    and slightly outward; the phone mounts at the wrist (top).
    """
    img = new_part()
    cx, cy = W // 2, H // 2
    # Upper arm
    filled_outlined_ellipse(img, cx, cy + 30, 14, 28, SKIN)
    # Forearm
    filled_outlined_ellipse(img, cx, cy - 14, 12, 30, SKIN)
    # Wrist bend dot
    ellipse(img, cx, cy, 6, 6, SKIN_S)
    # Hand
    filled_outlined_ellipse(img, cx, cy - 44, 12, 12, SKIN)
    # Watch on forearm (Apple Watch — Katie reference but boss has one too)
    filled_outlined_rect(img, cx - 8, cy - 6, 16, 14, BLACK, OUTLINE, 2)
    rect(img, cx - 6, cy - 4, 12, 10, SCREEN)
    return img


def draw_head():
    """Top of head: brunette hair, bangs, face peeking. View is top-down so
    we mostly see the crown of her hair with face features below."""
    img = new_part()
    cx, cy = W // 2, H // 2
    # Crown (hair from above)
    filled_outlined_ellipse(img, cx, cy - 8, 50, 48, HAIR)
    # Face oval (lower half — chin pointing toward player at bottom)
    filled_outlined_ellipse(img, cx, cy + 18, 32, 30, SKIN)
    # Bangs swooping over forehead
    ellipse(img, cx, cy - 4, 38, 14, HAIR)
    rect(img, cx - 36, cy - 2, 72, 6, HAIR_H)
    # Eyes (sunglasses-free, stylized)
    filled_outlined_ellipse(img, cx - 12, cy + 14, 5, 4, WHITE, OUTLINE, 2)
    filled_outlined_ellipse(img, cx + 12, cy + 14, 5, 4, WHITE, OUTLINE, 2)
    ellipse(img, cx - 12, cy + 14, 2, 2, EYE)
    ellipse(img, cx + 12, cy + 14, 2, 2, EYE)
    # Nose tiny shadow
    ellipse(img, cx, cy + 22, 2, 3, SKIN_S)
    # Lipstick smile (puckered — selfie face)
    filled_outlined_ellipse(img, cx, cy + 32, 8, 4, LIP, OUTLINE, 2)
    # Highlight lock
    rect(img, cx - 24, cy - 24, 4, 18, HAIR_H)
    rect(img, cx + 18, cy - 28, 4, 14, HAIR_H)
    return img


def draw_phone():
    """White iPhone with bright screen, lens on back."""
    img = new_part()
    cx, cy = W // 2, H // 2
    # Phone body (white with rounded corners)
    filled_outlined_rect(img, cx - 22, cy - 36, 44, 72, WHITE, OUTLINE, 3)
    # Screen
    filled_outlined_rect(img, cx - 18, cy - 30, 36, 60, BLACK, OUTLINE, 1)
    # Camera lens cluster (top of screen — facing OUT toward player)
    filled_outlined_ellipse(img, cx - 10, cy - 22, 4, 4, BLACK_H, OUTLINE, 1)
    filled_outlined_ellipse(img, cx + 6, cy - 22, 4, 4, BLACK_H, OUTLINE, 1)
    # Selfie reflection — bright screen content
    rect(img, cx - 14, cy - 12, 28, 36, SCREEN)
    # "Influencer" UI hints — heart and star
    rect(img, cx - 10, cy - 4, 4, 4, PINK)
    rect(img, cx - 4, cy - 4, 4, 4, PINK)
    rect(img, cx + 2, cy + 4, 6, 6, GOLD)
    # Flash dot
    ellipse(img, cx - 18, cy - 26, 2, 2, GOLD)
    return img


# ── Reference (assembled) ─────────────────────────────────────────────────

def build_reference(parts: dict[str, Image.Image]) -> Image.Image:
    """Stack parts in approximately their final spine layout for SIFT
    positioning and human review."""
    ref = Image.new("RGBA", (320, 480), (0, 0, 0, 0))
    cx, cy = 160, 240

    # Place each part offset roughly to bone positions (top-down, head up)
    def paste(img, dx, dy):
        ref.alpha_composite(img, (cx - W // 2 + dx, cy - H // 2 + dy))

    paste(parts["hair-back"], 0, 70)
    paste(parts["legs"], 0, 70)
    paste(parts["arm-phone"], 60, -20)
    paste(parts["body"], 0, 0)
    paste(parts["head"], 0, -80)
    paste(parts["phone"], 80, -110)
    return ref


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    parts = {
        "hair-back": draw_hair_back(),
        "legs": draw_legs(),
        "arm-phone": draw_arm_phone(),
        "body": draw_body(),
        "head": draw_head(),
        "phone": draw_phone(),
    }
    for name, img in parts.items():
        path = OUT / f"{name}.png"
        img.save(path, "PNG")
        print(f"  wrote {path}")
    REF.parent.mkdir(parents=True, exist_ok=True)
    build_reference(parts).save(REF, "PNG")
    print(f"  wrote {REF}")


if __name__ == "__main__":
    main()
