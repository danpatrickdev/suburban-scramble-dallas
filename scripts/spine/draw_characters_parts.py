#!/usr/bin/env python3
"""
draw_characters_parts.py — generate Spine body parts for the four remaining
playable characters (Charlie, Katie, Tia, Nancy). Each uses a top-down
3/4 view to match Rosie. Pajama-Sam-style flat saturated fills.

Outputs to: static/assets/spine/<id>/parts/<part>.png

Templates:
  - Charlie: same dog skeleton as Rosie, tri-color stocky build
  - Tia / Nancy: cat skeleton (rounder face, perky upright ears, no long
    muzzle); Tia is bigger/chunkier, Nancy is leaner with bigger eyes
  - Katie: humanoid skeleton (torso, head with ponytail, two arms, legs)
"""
from PIL import Image, ImageDraw
from pathlib import Path

W, H = 256, 256
# Pure-black ink line for the cel/Humongous look. Slightly off-black to read
# softer than #000.
OUTLINE = (12, 14, 20, 255)
# Default outline thickness for limbs/heads — chunky enough that even at
# spine scale 0.50 the line reads as a clean ink contour, not a pixel edge.
THICK = 6


def new_part() -> Image.Image:
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def ellipse(img, cx, cy, rx, ry, color):
    # Use a 4× supersampled ellipse + downsample so the edge anti-aliases
    # cleanly into the transparent alpha. Without this, PIL's default
    # ellipse leaves a stair-stepped edge that reads as "pixel sprite".
    ss = 4
    big = Image.new("RGBA", ((rx + 4) * 2 * ss, (ry + 4) * 2 * ss), (0, 0, 0, 0))
    ImageDraw.Draw(big).ellipse(
        [4 * ss, 4 * ss, (rx * 2 + 4) * ss, (ry * 2 + 4) * ss],
        fill=color,
    )
    small = big.resize(((rx + 4) * 2, (ry + 4) * 2), Image.LANCZOS)
    img.alpha_composite(small, (cx - rx - 4, cy - ry - 4))


def filled_outlined_ellipse(img, cx, cy, rx, ry, fill, outline=OUTLINE, thick=THICK):
    ellipse(img, cx, cy, rx + thick, ry + thick, outline)
    ellipse(img, cx, cy, rx, ry, fill)
    # Subtle cel highlight — flat-color "shine" on the upper-left of the form.
    if fill[3] == 255 and fill != outline:
        hl = (
            min(fill[0] + 40, 255),
            min(fill[1] + 40, 255),
            min(fill[2] + 40, 255),
            120,
        )
        ellipse(img, cx - rx // 3, cy - ry // 3, max(2, rx // 3), max(2, ry // 3), hl)


def rect(img, x, y, w, h, color):
    ImageDraw.Draw(img).rectangle([x, y, x + w - 1, y + h - 1], fill=color)


def filled_outlined_rect(img, x, y, w, h, fill, outline=OUTLINE, thick=THICK):
    rect(img, x - thick, y - thick, w + thick * 2, h + thick * 2, outline)
    rect(img, x, y, w, h, fill)


# ── Dog template (Charlie — tri-color stocky border collie) ───────────────

CHARLIE = {
    "black": (24, 24, 30, 255),
    "white": (252, 250, 244, 255),
    "tan": (164, 100, 48, 255),
    "tan_h": (200, 145, 88, 255),
    "amber": (255, 184, 0, 255),
    "pink": (240, 130, 158, 255),
    "nose": (24, 18, 24, 255),
}


def charlie_body():
    img = new_part()
    cx, cy = W // 2, H // 2
    # Stockier than Rosie — wider, slightly shorter
    filled_outlined_ellipse(img, cx, cy, 70, 76, CHARLIE["black"])
    # White chest blaze (broader)
    ellipse(img, cx, cy + 22, 24, 36, CHARLIE["white"])
    # Tan side highlights (Bernese-mix vibe)
    ellipse(img, cx - 50, cy + 24, 12, 20, CHARLIE["tan"])
    ellipse(img, cx + 50, cy + 24, 12, 20, CHARLIE["tan"])
    return img


def charlie_head():
    img = new_part()
    cx, cy = W // 2, H // 2
    # Big stocky head
    filled_outlined_ellipse(img, cx, cy + 6, 64, 70, CHARLIE["black"])
    # Snout (shorter than Rosie's)
    filled_outlined_ellipse(img, cx, cy - 48, 24, 30, CHARLIE["black"])
    # Wide white blaze
    rect(img, cx - 14, cy - 78, 28, 100, CHARLIE["white"])
    # Tan eyebrow markings ("kabuki face")
    ellipse(img, cx - 22, cy - 8, 8, 6, CHARLIE["tan"])
    ellipse(img, cx + 22, cy - 8, 8, 6, CHARLIE["tan"])
    # Eyes
    filled_outlined_ellipse(img, cx - 18, cy - 4, 4, 5, CHARLIE["amber"], OUTLINE, 2)
    filled_outlined_ellipse(img, cx + 18, cy - 4, 4, 5, CHARLIE["amber"], OUTLINE, 2)
    # Nose
    filled_outlined_ellipse(img, cx, cy - 60, 6, 5, CHARLIE["nose"], OUTLINE, 2)
    # Tongue
    rect(img, cx - 4, cy - 50, 8, 14, CHARLIE["pink"])
    return img


def charlie_ear_left():
    img = new_part()
    cx, cy = W // 2, H // 2
    filled_outlined_ellipse(img, cx + 8, cy + 16, 18, 26, CHARLIE["black"])
    ellipse(img, cx + 8, cy + 18, 10, 18, CHARLIE["pink"])
    return img


def charlie_ear_right():
    img = new_part()
    cx, cy = W // 2, H // 2
    filled_outlined_ellipse(img, cx - 8, cy + 16, 18, 26, CHARLIE["black"])
    ellipse(img, cx - 8, cy + 18, 10, 18, CHARLIE["pink"])
    return img


def charlie_tail():
    img = new_part()
    cx, cy = W // 2, H // 2
    filled_outlined_ellipse(img, cx, cy, 12, 38, CHARLIE["black"])
    ellipse(img, cx, cy + 24, 10, 14, CHARLIE["white"])
    return img


def charlie_leg(tan=False):
    img = new_part()
    cx, cy = W // 2, H // 2
    fill = CHARLIE["tan"] if tan else CHARLIE["black"]
    filled_outlined_ellipse(img, cx, cy, 16, 36, fill)
    # Sock highlight (white toes)
    ellipse(img, cx, cy + 28, 14, 8, CHARLIE["white"])
    return img


# ── Cat template (Tia / Nancy — earl-grey-and-white) ──────────────────────

CAT_GREY = (148, 152, 162, 255)
CAT_GREY_H = (192, 196, 204, 255)
CAT_WHITE = (252, 250, 244, 255)
CAT_PINK = (240, 130, 158, 255)
CAT_GREEN_EYE = (96, 210, 138, 255)
CAT_NOSE = (220, 110, 138, 255)


def cat_body(scale=1.0):
    img = new_part()
    cx, cy = W // 2, H // 2
    rx = int(54 * scale)
    ry = int(64 * scale)
    filled_outlined_ellipse(img, cx, cy, rx, ry, CAT_GREY)
    # White belly
    ellipse(img, cx, cy + int(20 * scale), int(20 * scale), int(28 * scale), CAT_WHITE)
    # Tabby stripe hints
    rect(img, cx - rx + 6, cy - 14, rx * 2 - 12, 2, CAT_GREY_H)
    rect(img, cx - rx + 6, cy + 4, rx * 2 - 12, 2, CAT_GREY_H)
    return img


def cat_head(big_eyes=False, chunky=False):
    img = new_part()
    cx, cy = W // 2, H // 2
    headR = 56 if chunky else 48
    # Round cat head (no long muzzle)
    filled_outlined_ellipse(img, cx, cy, headR, headR - 2, CAT_GREY)
    # White muzzle/chin patch
    ellipse(img, cx, cy + 12, 22, 16, CAT_WHITE)
    # Eyes
    eyeR = 8 if big_eyes else 6
    filled_outlined_ellipse(img, cx - 16, cy - 6, eyeR, eyeR + 1, CAT_GREEN_EYE, OUTLINE, 2)
    filled_outlined_ellipse(img, cx + 16, cy - 6, eyeR, eyeR + 1, CAT_GREEN_EYE, OUTLINE, 2)
    # Slit pupils
    rect(img, cx - 17, cy - 8, 2, eyeR, OUTLINE)
    rect(img, cx + 15, cy - 8, 2, eyeR, OUTLINE)
    # Nose
    filled_outlined_ellipse(img, cx, cy + 4, 4, 3, CAT_NOSE, OUTLINE, 1)
    # Mouth
    rect(img, cx - 4, cy + 8, 8, 1, OUTLINE)
    # Whisker dots
    for dx in (-22, -16, 16, 22):
        rect(img, cx + dx, cy + 12, 1, 1, OUTLINE)
    return img


def cat_ear_left(perked=True):
    img = new_part()
    cx, cy = W // 2, H // 2
    # Triangle-ish upright ear (use polygon)
    d = ImageDraw.Draw(img)
    pts = [(cx - 18, cy + 20), (cx + 18, cy + 20), (cx + 4, cy - 30)]
    # Outline
    d.polygon([(cx - 21, cy + 23), (cx + 21, cy + 23), (cx + 4, cy - 33)], fill=OUTLINE)
    d.polygon(pts, fill=CAT_GREY)
    # Inner pink
    inner = [(cx - 8, cy + 14), (cx + 8, cy + 14), (cx + 2, cy - 20)]
    d.polygon(inner, fill=CAT_PINK)
    return img


def cat_ear_right():
    img = new_part()
    cx, cy = W // 2, H // 2
    d = ImageDraw.Draw(img)
    d.polygon([(cx - 21, cy + 23), (cx + 21, cy + 23), (cx - 4, cy - 33)], fill=OUTLINE)
    d.polygon([(cx - 18, cy + 20), (cx + 18, cy + 20), (cx - 4, cy - 30)], fill=CAT_GREY)
    d.polygon([(cx - 8, cy + 14), (cx + 8, cy + 14), (cx - 2, cy - 20)], fill=CAT_PINK)
    return img


def cat_tail():
    img = new_part()
    cx, cy = W // 2, H // 2
    filled_outlined_ellipse(img, cx, cy, 10, 50, CAT_GREY)
    # White tip
    ellipse(img, cx, cy + 38, 8, 12, CAT_WHITE)
    # Tabby rings
    for ry in range(-30, 30, 12):
        rect(img, cx - 10, cy + ry, 20, 2, CAT_GREY_H)
    return img


def cat_leg(scale=1.0):
    img = new_part()
    cx, cy = W // 2, H // 2
    rx = int(14 * scale)
    ry = int(34 * scale)
    filled_outlined_ellipse(img, cx, cy, rx, ry, CAT_GREY)
    ellipse(img, cx, cy + int(24 * scale), int(12 * scale), int(8 * scale), CAT_WHITE)
    return img


# ── Human (Katie — pink Lululemon, brunette ponytail, Apple Watch) ────────

K_PINK = (255, 128, 178, 255)
K_PINK_S = (215, 80, 128, 255)
K_BLACK = (24, 24, 30, 255)
K_WHITE = (252, 252, 250, 255)
K_HAIR = (78, 44, 24, 255)
K_HAIR_H = (135, 88, 50, 255)
K_SKIN = (250, 215, 180, 255)
K_SKIN_S = (215, 175, 140, 255)
K_SCREEN = (140, 220, 255, 255)


def katie_body():
    img = new_part()
    cx, cy = W // 2, H // 2
    # Pink Lululemon torso — slim athletic SHAPE, but full overall size.
    # Tall + narrow ellipse: hourglass runner silhouette, not chubby.
    filled_outlined_ellipse(img, cx, cy, 38, 86, K_PINK)
    # Crop-top hem (lower)
    rect(img, cx - 34, cy + 70, 68, 5, K_PINK_S)
    # Subtle midline shading
    rect(img, cx - 1, cy - 50, 2, 90, K_PINK_S)
    # Waist tapering hint (lighter at the middle to suggest hourglass)
    ellipse(img, cx - 32, cy + 4, 4, 22, K_PINK_S)
    ellipse(img, cx + 32, cy + 4, 4, 22, K_PINK_S)
    # Apple Watch on the wrist (left side as we look down)
    filled_outlined_rect(img, cx - 48, cy - 6, 12, 18, K_BLACK, OUTLINE, 2)
    rect(img, cx - 46, cy - 4, 8, 14, K_SCREEN)
    return img


def katie_head():
    img = new_part()
    cx, cy = W // 2, H // 2
    # Crown of brunette hair (full size)
    filled_outlined_ellipse(img, cx, cy - 12, 50, 54, K_HAIR)
    # Face oval — slim cheekbones, not round
    filled_outlined_ellipse(img, cx, cy + 18, 28, 36, K_SKIN)
    # Bangs
    ellipse(img, cx, cy - 4, 38, 14, K_HAIR)
    rect(img, cx - 36, cy - 2, 72, 5, K_HAIR_H)
    # Eyes
    filled_outlined_ellipse(img, cx - 11, cy + 14, 5, 5, K_WHITE, OUTLINE, 1)
    filled_outlined_ellipse(img, cx + 11, cy + 14, 5, 5, K_WHITE, OUTLINE, 1)
    ellipse(img, cx - 11, cy + 14, 2, 3, K_BLACK)
    ellipse(img, cx + 11, cy + 14, 2, 3, K_BLACK)
    # Lips
    filled_outlined_ellipse(img, cx, cy + 32, 8, 4, K_PINK_S, OUTLINE, 1)
    # Highlight strands
    rect(img, cx - 26, cy - 28, 4, 22, K_HAIR_H)
    rect(img, cx + 22, cy - 32, 4, 16, K_HAIR_H)
    return img


def katie_ponytail():
    img = new_part()
    cx, cy = W // 2, H // 2
    # Long ponytail trailing toward bottom of frame, full length
    filled_outlined_ellipse(img, cx, cy + 36, 26, 70, K_HAIR)
    filled_outlined_ellipse(img, cx, cy + 100, 16, 22, K_HAIR)
    rect(img, cx - 6, cy, 2, 110, K_HAIR_H)
    rect(img, cx + 5, cy + 8, 2, 104, K_HAIR_H)
    # Hair tie
    filled_outlined_rect(img, cx - 18, cy + 76, 36, 7, K_PINK_S, OUTLINE, 2)
    return img


def katie_arm():
    img = new_part()
    cx, cy = W // 2, H // 2
    # Slim but full-length toned arm
    filled_outlined_ellipse(img, cx, cy, 11, 64, K_SKIN)
    return img


def katie_leg():
    img = new_part()
    cx, cy = W // 2, H // 2
    # Slim leggings, full-length
    filled_outlined_ellipse(img, cx, cy, 13, 70, K_BLACK)
    # White sneaker tip
    ellipse(img, cx, cy + 60, 12, 10, K_WHITE)
    rect(img, cx - 9, cy + 60, 18, 2, K_PINK)
    return img


# ── Wiring ────────────────────────────────────────────────────────────────

def write_parts(slug: str, parts: dict[str, Image.Image]):
    out = Path(f"static/assets/spine/{slug}/parts")
    out.mkdir(parents=True, exist_ok=True)
    for name, img in parts.items():
        path = out / f"{name}.png"
        img.save(path, "PNG")
        print(f"  wrote {path}")


def main():
    # Charlie — dog skeleton, tri-color stocky
    write_parts("charlie", {
        "body": charlie_body(),
        "head": charlie_head(),
        "ear-left": charlie_ear_left(),
        "ear-right": charlie_ear_right(),
        "tail": charlie_tail(),
        "leg-front-left": charlie_leg(tan=True),
        "leg-front-right": charlie_leg(tan=True),
        "leg-back-left": charlie_leg(tan=True),
        "leg-back-right": charlie_leg(tan=True),
    })
    # Tia — cat skeleton, larger chunkier
    write_parts("tia", {
        "body": cat_body(scale=1.1),
        "head": cat_head(chunky=True),
        "ear-left": cat_ear_left(),
        "ear-right": cat_ear_right(),
        "tail": cat_tail(),
        "leg-front-left": cat_leg(scale=1.0),
        "leg-front-right": cat_leg(scale=1.0),
        "leg-back-left": cat_leg(scale=1.0),
        "leg-back-right": cat_leg(scale=1.0),
    })
    # Nancy — cat skeleton, leaner with bigger eyes
    write_parts("nancy", {
        "body": cat_body(scale=0.9),
        "head": cat_head(big_eyes=True),
        "ear-left": cat_ear_left(),
        "ear-right": cat_ear_right(),
        "tail": cat_tail(),
        "leg-front-left": cat_leg(scale=0.85),
        "leg-front-right": cat_leg(scale=0.85),
        "leg-back-left": cat_leg(scale=0.85),
        "leg-back-right": cat_leg(scale=0.85),
    })
    # Katie — humanoid: torso, head, ponytail (back), 2 arms, 2 legs
    write_parts("katie", {
        "body": katie_body(),
        "head": katie_head(),
        "hair-back": katie_ponytail(),
        "arm-left": katie_arm(),
        "arm-right": katie_arm(),
        "leg-left": katie_leg(),
        "leg-right": katie_leg(),
    })


if __name__ == "__main__":
    main()
