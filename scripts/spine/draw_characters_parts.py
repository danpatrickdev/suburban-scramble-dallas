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
OUTLINE = (15, 15, 18, 255)


def new_part() -> Image.Image:
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def ellipse(img, cx, cy, rx, ry, color):
    ImageDraw.Draw(img).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=color)


def filled_outlined_ellipse(img, cx, cy, rx, ry, fill, outline=OUTLINE, thick=3):
    ellipse(img, cx, cy, rx + thick, ry + thick, outline)
    ellipse(img, cx, cy, rx, ry, fill)


def rect(img, x, y, w, h, color):
    ImageDraw.Draw(img).rectangle([x, y, x + w - 1, y + h - 1], fill=color)


def filled_outlined_rect(img, x, y, w, h, fill, outline=OUTLINE, thick=3):
    rect(img, x - thick, y - thick, w + thick * 2, h + thick * 2, outline)
    rect(img, x, y, w, h, fill)


# ── Dog template (Charlie — tri-color stocky border collie) ───────────────

CHARLIE = {
    "black": (28, 28, 32, 255),
    "white": (248, 246, 240, 255),
    "tan": (148, 96, 50, 255),
    "tan_h": (180, 130, 80, 255),
    "amber": (255, 176, 0, 255),
    "pink": (228, 130, 152, 255),
    "nose": (28, 22, 28, 255),
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

CAT_GREY = (140, 143, 149, 255)
CAT_GREY_H = (180, 183, 189, 255)
CAT_WHITE = (248, 246, 240, 255)
CAT_PINK = (228, 130, 152, 255)
CAT_GREEN_EYE = (96, 200, 130, 255)
CAT_NOSE = (200, 110, 130, 255)


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

K_PINK = (248, 130, 168, 255)
K_PINK_S = (210, 90, 130, 255)
K_BLACK = (28, 28, 32, 255)
K_WHITE = (250, 250, 248, 255)
K_HAIR = (74, 44, 28, 255)
K_HAIR_H = (110, 70, 44, 255)
K_SKIN = (245, 210, 178, 255)
K_SKIN_S = (215, 178, 148, 255)
K_SCREEN = (140, 215, 255, 255)


def katie_body():
    img = new_part()
    cx, cy = W // 2, H // 2
    # Pink Lululemon torso — slim athletic build (narrower than v1)
    filled_outlined_ellipse(img, cx, cy, 34, 62, K_PINK)
    # Crop top hem
    rect(img, cx - 30, cy + 48, 60, 4, K_PINK_S)
    # Subtle midline shading
    rect(img, cx - 1, cy - 32, 2, 58, K_PINK_S)
    # Apple Watch tucked just outside the torso silhouette
    filled_outlined_rect(img, cx - 42, cy - 4, 10, 14, K_BLACK, OUTLINE, 2)
    rect(img, cx - 40, cy - 2, 6, 10, K_SCREEN)
    return img


def katie_head():
    img = new_part()
    cx, cy = W // 2, H // 2
    # Crown of brunette hair — narrower
    filled_outlined_ellipse(img, cx, cy - 8, 40, 44, K_HAIR)
    # Face oval — slimmer
    filled_outlined_ellipse(img, cx, cy + 16, 24, 28, K_SKIN)
    # Bangs
    ellipse(img, cx, cy - 4, 30, 12, K_HAIR)
    rect(img, cx - 28, cy - 2, 56, 4, K_HAIR_H)
    # Eyes
    filled_outlined_ellipse(img, cx - 9, cy + 12, 4, 4, K_WHITE, OUTLINE, 1)
    filled_outlined_ellipse(img, cx + 9, cy + 12, 4, 4, K_WHITE, OUTLINE, 1)
    ellipse(img, cx - 9, cy + 12, 2, 2, K_BLACK)
    ellipse(img, cx + 9, cy + 12, 2, 2, K_BLACK)
    # Lips
    filled_outlined_ellipse(img, cx, cy + 28, 6, 3, K_PINK_S, OUTLINE, 1)
    # Hair highlights
    rect(img, cx - 20, cy - 22, 3, 18, K_HAIR_H)
    rect(img, cx + 16, cy - 26, 3, 14, K_HAIR_H)
    return img


def katie_ponytail():
    img = new_part()
    cx, cy = W // 2, H // 2
    # Long ponytail trailing toward bottom of frame
    filled_outlined_ellipse(img, cx, cy + 30, 22, 56, K_HAIR)
    filled_outlined_ellipse(img, cx, cy + 84, 14, 18, K_HAIR)
    rect(img, cx - 5, cy, 2, 90, K_HAIR_H)
    rect(img, cx + 4, cy + 8, 2, 86, K_HAIR_H)
    # Hair tie
    filled_outlined_rect(img, cx - 14, cy + 64, 28, 6, K_PINK_S, OUTLINE, 2)
    return img


def katie_arm():
    img = new_part()
    cx, cy = W // 2, H // 2
    # Slim toned arm
    filled_outlined_ellipse(img, cx, cy, 9, 50, K_SKIN)
    return img


def katie_leg():
    img = new_part()
    cx, cy = W // 2, H // 2
    # Slim leggings
    filled_outlined_ellipse(img, cx, cy, 11, 54, K_BLACK)
    # White sneaker tip
    ellipse(img, cx, cy + 46, 10, 8, K_WHITE)
    rect(img, cx - 7, cy + 46, 14, 2, K_PINK)
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
