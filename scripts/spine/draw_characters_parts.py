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
import sys
from PIL import Image, ImageDraw
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cel_paint import (
    INK as OUTLINE,
    aa_ellipse as ellipse,
    aa_polygon,
    smooth_curve,
    painted_ellipse,
    painted_blob,
    painted_rounded_rect,
    drop_shadow,
    darken,
    lighten,
)

W, H = 256, 256


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


# ── Expressive face details (shared across characters) ────────────────────

def expressive_eye(img, cx, cy, *, size=5, iris_color=(40, 90, 30, 255),
                   pupil_color=OUTLINE, look=(0, 0), eyelid=False):
    """Multi-layer cartoon eye: sclera (white), iris (colored), pupil
    (dark), tiny shine highlight. `look` shifts iris+pupil toward a
    direction for character expression. If eyelid=True, draw a curved
    upper-lid line for sleepy/half-lid look."""
    sclera = (252, 250, 244, 255)
    # Sclera with subtle outline
    painted_ellipse(img, cx, cy, size, size, sclera, outline_top=2, outline_bottom=3)
    # Iris
    ix, iy = cx + look[0], cy + look[1]
    aa_polygon(img, [
        (ix - size + 2, iy),
        (ix, iy - size + 2),
        (ix + size - 2, iy),
        (ix, iy + size - 2),
    ], iris_color)
    ellipse(img, ix, iy, max(2, size - 2), max(2, size - 2), iris_color)
    # Pupil
    ellipse(img, ix, iy, max(1, size - 4), max(1, size - 4), pupil_color)
    # Shine
    ellipse(img, ix - 1, iy - 1, 1, 1, (255, 255, 255, 230))
    if eyelid:
        d = ImageDraw.Draw(img)
        d.arc([cx - size, cy - size - 2, cx + size, cy + size - 2],
              start=200, end=340, fill=OUTLINE, width=2)


def whiskers(img, cx, cy, *, span=18, count=3, color=OUTLINE):
    d = ImageDraw.Draw(img)
    for side in (-1, 1):
        for i in range(count):
            y = cy - (count - 1) * 2 + i * 4
            x0 = cx + 4 * side
            x1 = cx + (span + i * 2) * side
            d.line([(x0, y), (x1, y + (i - 1))], fill=color, width=1)


def fur_tuft(img, cx, cy, color, *, length=8, dir_x=0, dir_y=-1):
    """A small triangle fur wisp pointing in a direction."""
    base = (cx, cy)
    tip = (cx + dir_x * length, cy + dir_y * length)
    side = (cx + dir_y * 3 - dir_x * 3, cy - dir_x * 3 - dir_y * 3)
    side2 = (cx - dir_y * 3 - dir_x * 3, cy + dir_x * 3 - dir_y * 3)
    aa_polygon(img, [base, side, tip, side2], color)


# ── Dog template (Rosie — classic black/white border collie, lean) ───────

ROSIE = {
    "black": (24, 24, 30, 255),
    "white": (252, 250, 244, 255),
    "amber": (255, 184, 0, 255),
    "pink": (240, 130, 158, 255),
    "nose": (24, 18, 24, 255),
}


def rosie_body():
    """SIDE-VIEW border collie body. Dog faces RIGHT (+x). Black saddle
    over a long sloping back, white chest peeking out below + behind
    front legs. Bone anchor (0,0 in part canvas) is the center of the
    torso; head attaches off the front (right side), tail off the back."""
    img = new_part()
    cx, cy = W // 2, H // 2
    # Body silhouette — long horizontal oval-ish profile, with shoulder
    # rise toward front (right side) and croup slope toward back (left).
    body_pts = [
        (cx + 50,  cy - 30),  # front shoulder peak (right side)
        (cx + 70,  cy + 0),   # chest forward
        (cx + 56,  cy + 30),  # belly front
        (cx + 20,  cy + 36),
        (cx - 20,  cy + 32),
        (cx - 56,  cy + 26),  # belly back
        (cx - 72,  cy + 0),   # rump back
        (cx - 64,  cy - 26),  # croup
        (cx - 30,  cy - 38),
        (cx + 16,  cy - 38),
        (cx + 38,  cy - 36),
    ]
    painted_blob(img, body_pts, ROSIE["black"], outline_thick=5)
    # White chest patch (visible on the underside-front)
    chest_pts = [
        (cx + 56,  cy + 6),
        (cx + 60,  cy + 28),
        (cx + 30,  cy + 36),
        (cx + 6,   cy + 32),
        (cx + 4,   cy + 14),
        (cx + 30,  cy + 8),
    ]
    painted_blob(img, chest_pts, ROSIE["white"], outline_thick=2)
    # White belly stripe (thin, runs along the underside)
    belly_pts = [
        (cx + 40,  cy + 32),
        (cx + 12,  cy + 36),
        (cx - 26,  cy + 32),
        (cx - 40,  cy + 24),
        (cx - 18,  cy + 26),
        (cx + 18,  cy + 28),
    ]
    painted_blob(img, belly_pts, ROSIE["white"], outline_thick=1)
    # Subtle fur tuft on the shoulder ridge
    fur_tuft(img, cx + 46, cy - 32, ROSIE["black"], length=10, dir_x=0, dir_y=-1)
    fur_tuft(img, cx + 38, cy - 36, ROSIE["black"], length=8, dir_x=1, dir_y=-1)
    fur_tuft(img, cx - 46, cy - 26, ROSIE["black"], length=8, dir_x=-1, dir_y=-1)
    return img


def rosie_head():
    """SIDE-3/4 view dog head. Snout points RIGHT, eyes turned slightly
    toward the camera (3/4 angle). White blaze runs down the muzzle."""
    img = new_part()
    cx, cy = W // 2, H // 2
    # Skull + cheek silhouette
    skull_pts = [
        (cx - 30,  cy - 50),  # top-back of skull
        (cx + 8,   cy - 56),  # top of skull
        (cx + 28,  cy - 42),
        (cx + 36,  cy - 14),  # forehead/brow
        (cx + 20,  cy + 8),   # cheek (where snout meets head)
        (cx + 4,   cy + 20),  # under-jaw
        (cx - 18,  cy + 26),  # throat
        (cx - 38,  cy + 20),
        (cx - 44,  cy - 4),
        (cx - 42,  cy - 30),
    ]
    painted_blob(img, skull_pts, ROSIE["black"], outline_thick=5)
    # Long pointed snout extending RIGHT
    snout_pts = [
        (cx + 20,  cy - 14),
        (cx + 80,  cy - 8),   # snout tip
        (cx + 90,  cy + 6),   # nose tip
        (cx + 76,  cy + 18),
        (cx + 28,  cy + 22),
        (cx + 12,  cy + 14),
    ]
    painted_blob(img, snout_pts, ROSIE["black"], outline_thick=4)
    # White blaze running from forehead down the snout
    blaze_pts = [
        (cx + 4,   cy - 50),
        (cx + 22,  cy - 30),
        (cx + 60,  cy - 4),
        (cx + 80,  cy + 4),
        (cx + 70,  cy + 14),
        (cx + 32,  cy + 12),
        (cx + 14,  cy - 4),
        (cx,       cy - 24),
        (cx - 4,   cy - 44),
    ]
    painted_blob(img, blaze_pts, ROSIE["white"], outline_thick=1)
    # Expressive amber eye — single (3/4 view shows mainly one eye, the
    # other is hinted faintly near the back of the skull).
    expressive_eye(img, cx + 18, cy - 18, size=7, iris_color=ROSIE["amber"], look=(1, 1))
    # Tiny back-eye hint
    ellipse(img, cx - 4, cy - 24, 2, 3, OUTLINE)
    # Brow line for personality
    d = ImageDraw.Draw(img)
    d.line([(cx + 8, cy - 28), (cx + 28, cy - 26)], fill=OUTLINE, width=2)
    # Heart-ish black nose at snout tip
    nose_pts = [
        (cx + 80,  cy - 4),
        (cx + 92,  cy + 0),
        (cx + 90,  cy + 12),
        (cx + 80,  cy + 14),
        (cx + 72,  cy + 6),
    ]
    painted_blob(img, nose_pts, ROSIE["nose"], outline_thick=2)
    # Mouth line — slight smile, tongue peeking
    d.arc([cx + 36, cy + 10, cx + 70, cy + 26], start=20, end=160, fill=OUTLINE, width=2)
    # Pink tongue lolling
    tongue_pts = [
        (cx + 50, cy + 18),
        (cx + 62, cy + 18),
        (cx + 60, cy + 30),
        (cx + 52, cy + 32),
    ]
    painted_blob(img, tongue_pts, ROSIE["pink"], outline_thick=1)
    return img


def rosie_ear():
    """Two alert ears on top of the head, side-view. Front ear larger
    (closer to camera), back ear smaller and partially hidden."""
    img = new_part()
    cx, cy = W // 2, H // 2
    # Front (camera-facing) ear
    front_pts = [
        (cx + 8,   cy - 56),  # tip
        (cx + 24,  cy - 40),
        (cx + 26,  cy - 12),
        (cx + 14,  cy + 4),
        (cx,       cy - 4),
        (cx - 4,   cy - 22),
    ]
    painted_blob(img, front_pts, ROSIE["black"], outline_thick=4)
    # Front ear inner pink
    front_inner = [
        (cx + 8,   cy - 44),
        (cx + 18,  cy - 30),
        (cx + 16,  cy - 8),
        (cx + 4,   cy - 4),
        (cx - 2,   cy - 22),
    ]
    painted_blob(img, front_inner, ROSIE["pink"], outline_thick=1)
    # Back ear (smaller, behind/up)
    back_pts = [
        (cx - 16,  cy - 50),  # tip (behind front ear)
        (cx - 4,   cy - 38),
        (cx - 4,   cy - 20),
        (cx - 14,  cy - 14),
        (cx - 22,  cy - 26),
    ]
    painted_blob(img, back_pts, ROSIE["black"], outline_thick=3)
    return img


def rosie_tail():
    """Long fluffy BC tail extending behind (left) the body, curving up
    slightly with a white tip."""
    img = new_part()
    cx, cy = W // 2, H // 2
    tail_pts = [
        (cx + 8,   cy - 4),    # base (attaches to back of torso)
        (cx + 4,   cy - 16),
        (cx - 14,  cy - 28),
        (cx - 36,  cy - 32),   # mid curve
        (cx - 60,  cy - 24),
        (cx - 76,  cy - 4),    # tip end
        (cx - 70,  cy + 10),
        (cx - 50,  cy + 4),
        (cx - 28,  cy - 4),
        (cx - 4,   cy + 4),
    ]
    painted_blob(img, tail_pts, ROSIE["black"], outline_thick=4)
    # White tip (the famous BC tail tip)
    tip_pts = [
        (cx - 56,  cy - 20),
        (cx - 76,  cy - 4),
        (cx - 66,  cy + 8),
        (cx - 50,  cy + 0),
    ]
    painted_blob(img, tip_pts, ROSIE["white"], outline_thick=1)
    return img


def rosie_legs(front: bool = True):
    """Two legs viewed from the side. front=True draws the visible front
    pair (closer to camera, larger). front=False draws the back pair
    (smaller, partially behind, slightly different stance)."""
    img = new_part()
    cx, cy = W // 2, H // 2
    # Closer leg (the one we see most of)
    closer_pts = [
        (cx - 8,   cy - 40),
        (cx + 6,   cy - 38),
        (cx + 10,  cy + 10),
        (cx + 8,   cy + 40),
        (cx - 4,   cy + 50),
        (cx - 12,  cy + 48),
        (cx - 14,  cy + 10),
        (cx - 14,  cy - 28),
    ]
    painted_blob(img, closer_pts, ROSIE["black"], outline_thick=4)
    # White paw
    paw_pts = [
        (cx - 12,  cy + 36),
        (cx + 8,   cy + 36),
        (cx + 6,   cy + 50),
        (cx - 4,   cy + 52),
        (cx - 12,  cy + 48),
    ]
    painted_blob(img, paw_pts, ROSIE["white"], outline_thick=1)
    # Toe pads
    for dx in (-6, 0, 4):
        ellipse(img, cx + dx, cy + 44, 1, 1, ROSIE["nose"])

    if front:
        # Second visible leg slightly behind, smaller silhouette
        second_x = cx + 16
        second_pts = [
            (second_x - 6, cy - 30),
            (second_x + 4, cy - 28),
            (second_x + 6, cy + 8),
            (second_x + 4, cy + 36),
            (second_x - 4, cy + 40),
            (second_x - 8, cy + 8),
            (second_x - 10, cy - 18),
        ]
        painted_blob(img, second_pts, ROSIE["black"], outline_thick=3)
        # White paw
        sp_pts = [
            (second_x - 8, cy + 28),
            (second_x + 4, cy + 28),
            (second_x + 2, cy + 38),
            (second_x - 6, cy + 38),
        ]
        painted_blob(img, sp_pts, ROSIE["white"], outline_thick=1)
    return img


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
    """Stocky tri-color border collie body, top-down. Organic blob
    silhouette (broad shoulders, narrowing toward hips) instead of
    a perfect ellipse."""
    img = new_part()
    cx, cy = W // 2, H // 2
    # Body silhouette control points (clockwise from 12 o'clock).
    # Asymmetric — left shoulder slightly broader than right, hips narrower.
    body_pts = [
        (cx,        cy - 80),  # top (neck)
        (cx + 38,   cy - 62),  # right shoulder
        (cx + 70,   cy - 18),  # right side
        (cx + 64,   cy + 30),  # right hip
        (cx + 32,   cy + 70),  # right rear
        (cx,        cy + 78),  # tail base
        (cx - 32,   cy + 68),  # left rear
        (cx - 64,   cy + 28),  # left hip
        (cx - 72,   cy - 16),  # left side
        (cx - 40,   cy - 64),  # left shoulder
    ]
    painted_blob(img, body_pts, CHARLIE["black"], outline_thick=5)
    # White chest blaze — broader, organic
    blaze = [
        (cx,      cy - 28),
        (cx + 16, cy - 8),
        (cx + 22, cy + 30),
        (cx + 12, cy + 60),
        (cx,      cy + 66),
        (cx - 12, cy + 60),
        (cx - 22, cy + 30),
        (cx - 16, cy - 8),
    ]
    painted_blob(img, blaze, CHARLIE["white"], outline_thick=2)
    # Tan side markings (Bernese mix vibe)
    painted_ellipse(img, cx - 52, cy + 30, 10, 18, CHARLIE["tan"], outline_top=2, outline_bottom=3)
    painted_ellipse(img, cx + 52, cy + 30, 10, 18, CHARLIE["tan"], outline_top=2, outline_bottom=3)
    # Subtle fur tufts at the shoulder ridges
    fur_tuft(img, cx - 56, cy - 50, CHARLIE["black"], length=8, dir_x=-1, dir_y=-1)
    fur_tuft(img, cx + 56, cy - 50, CHARLIE["black"], length=8, dir_x=1, dir_y=-1)
    return img


def charlie_head():
    """Stocky tri-color BC head — broad cranium, defined snout,
    expressive face."""
    img = new_part()
    cx, cy = W // 2, H // 2
    # Head silhouette: broad rounded skull + protruding snout
    head_pts = [
        (cx,      cy - 40),  # top of skull
        (cx + 36, cy - 28),  # right cheek
        (cx + 56, cy + 8),   # right jaw
        (cx + 48, cy + 38),  # right lower jaw
        (cx + 22, cy + 56),  # right neck join
        (cx,      cy + 60),  # chin tip (we put snout below)
        (cx - 22, cy + 56),
        (cx - 48, cy + 38),
        (cx - 56, cy + 8),
        (cx - 36, cy - 28),
    ]
    painted_blob(img, head_pts, CHARLIE["black"], outline_thick=5)
    # Snout protrusion (cone-ish blob extending below)
    snout_pts = [
        (cx - 22, cy + 38),
        (cx - 16, cy + 70),
        (cx - 8,  cy + 90),
        (cx,      cy + 96),
        (cx + 8,  cy + 90),
        (cx + 16, cy + 70),
        (cx + 22, cy + 38),
    ]
    painted_blob(img, snout_pts, CHARLIE["black"], outline_thick=3)
    # White blaze — wavy, hand-drawn feel
    blaze_pts = [
        (cx,       cy - 36),
        (cx + 12,  cy - 18),
        (cx + 14,  cy + 30),
        (cx + 10,  cy + 60),
        (cx + 6,   cy + 88),
        (cx,       cy + 94),
        (cx - 6,   cy + 88),
        (cx - 10,  cy + 60),
        (cx - 14,  cy + 30),
        (cx - 12,  cy - 18),
    ]
    painted_blob(img, blaze_pts, CHARLIE["white"], outline_thick=1)
    # Tan eyebrow markings ("kabuki face") — asymmetric for character
    painted_ellipse(img, cx - 22, cy - 6, 9, 6, CHARLIE["tan"], outline_top=1, outline_bottom=2)
    painted_ellipse(img, cx + 24, cy - 8, 9, 6, CHARLIE["tan"], outline_top=1, outline_bottom=2)
    # Expressive eyes — looking slightly forward (at player)
    expressive_eye(img, cx - 18, cy + 4, size=6, iris_color=CHARLIE["amber"], look=(0, 1))
    expressive_eye(img, cx + 18, cy + 4, size=6, iris_color=CHARLIE["amber"], look=(0, 1))
    # Nose (heart-ish shape, hand-drawn)
    nose_pts = [
        (cx,      cy + 70),
        (cx + 8,  cy + 64),
        (cx + 7,  cy + 76),
        (cx,      cy + 82),
        (cx - 7,  cy + 76),
        (cx - 8,  cy + 64),
    ]
    painted_blob(img, nose_pts, CHARLIE["nose"], outline_thick=2)
    # Tongue (cute pink lolling)
    tongue_pts = [
        (cx - 5, cy + 86),
        (cx + 5, cy + 86),
        (cx + 4, cy + 100),
        (cx,     cy + 104),
        (cx - 4, cy + 100),
    ]
    painted_blob(img, tongue_pts, CHARLIE["pink"], outline_thick=2)
    # Mouth line (small, expressive)
    d = ImageDraw.Draw(img)
    d.arc([cx - 12, cy + 80, cx + 12, cy + 96], start=20, end=160, fill=OUTLINE, width=2)
    return img


def charlie_ear_left():
    img = new_part()
    cx, cy = W // 2, H // 2
    ear_pts = [
        (cx + 4,  cy - 30),  # tip (slightly forward — alert)
        (cx + 16, cy - 12),
        (cx + 18, cy + 10),
        (cx + 10, cy + 22),
        (cx,      cy + 18),
        (cx - 6,  cy + 10),
        (cx - 8,  cy - 8),
    ]
    painted_blob(img, ear_pts, CHARLIE["black"], outline_thick=4)
    inner_pts = [
        (cx + 4,  cy - 18),
        (cx + 10, cy - 4),
        (cx + 8,  cy + 12),
        (cx,      cy + 10),
        (cx - 2,  cy + 0),
    ]
    painted_blob(img, inner_pts, CHARLIE["pink"], outline_thick=1)
    return img


def charlie_ear_right():
    img = new_part()
    cx, cy = W // 2, H // 2
    ear_pts = [
        (cx - 4,  cy - 30),
        (cx - 16, cy - 12),
        (cx - 18, cy + 10),
        (cx - 10, cy + 22),
        (cx,      cy + 18),
        (cx + 6,  cy + 10),
        (cx + 8,  cy - 8),
    ]
    painted_blob(img, ear_pts, CHARLIE["black"], outline_thick=4)
    inner_pts = [
        (cx - 4,  cy - 18),
        (cx - 10, cy - 4),
        (cx - 8,  cy + 12),
        (cx,      cy + 10),
        (cx + 2,  cy + 0),
    ]
    painted_blob(img, inner_pts, CHARLIE["pink"], outline_thick=1)
    return img


def charlie_tail():
    img = new_part()
    cx, cy = W // 2, H // 2
    tail_pts = [
        (cx - 4,  cy - 36),
        (cx + 8,  cy - 18),
        (cx + 14, cy + 6),
        (cx + 10, cy + 36),
        (cx + 2,  cy + 56),
        (cx - 6,  cy + 60),
        (cx - 14, cy + 44),
        (cx - 18, cy + 16),
        (cx - 14, cy - 12),
        (cx - 8,  cy - 28),
    ]
    painted_blob(img, tail_pts, CHARLIE["black"], outline_thick=4)
    # White tip
    tip_pts = [
        (cx - 8,  cy + 40),
        (cx + 4,  cy + 46),
        (cx,      cy + 60),
        (cx - 8,  cy + 60),
        (cx - 14, cy + 50),
    ]
    painted_blob(img, tip_pts, CHARLIE["white"], outline_thick=1)
    return img


def charlie_leg(tan=False):
    img = new_part()
    cx, cy = W // 2, H // 2
    fill = CHARLIE["tan"] if tan else CHARLIE["black"]
    leg_pts = [
        (cx - 14, cy - 32),
        (cx + 14, cy - 32),
        (cx + 16, cy + 4),
        (cx + 12, cy + 28),
        (cx,      cy + 36),
        (cx - 12, cy + 28),
        (cx - 16, cy + 4),
    ]
    painted_blob(img, leg_pts, fill, outline_thick=4)
    # White paw
    paw_pts = [
        (cx - 10, cy + 18),
        (cx + 10, cy + 18),
        (cx + 8,  cy + 32),
        (cx,      cy + 36),
        (cx - 8,  cy + 32),
    ]
    painted_blob(img, paw_pts, CHARLIE["white"], outline_thick=1)
    # Toe pad dots
    for dx in (-5, 0, 5):
        ellipse(img, cx + dx, cy + 28, 1, 1, CHARLIE["nose"])
    return img


# ── Cat template (Tia / Nancy — earl-grey-and-white) ──────────────────────

CAT_GREY = (148, 152, 162, 255)
CAT_GREY_H = (192, 196, 204, 255)
CAT_WHITE = (252, 250, 244, 255)
CAT_PINK = (240, 130, 158, 255)
CAT_GREEN_EYE = (96, 210, 138, 255)
CAT_NOSE = (220, 110, 138, 255)


def cat_body(scale=1.0):
    """Cat body silhouette — narrower waist, broader chest+haunches.
    Painted blob with white belly + soft tabby stripe accents."""
    img = new_part()
    cx, cy = W // 2, H // 2
    s = scale
    body_pts = [
        (cx,                cy - int(70 * s)),  # neck
        (cx + int(28 * s),  cy - int(56 * s)),
        (cx + int(54 * s),  cy - int(20 * s)),
        (cx + int(48 * s),  cy + int(8 * s)),   # waist taper (cats are leaner mid-body)
        (cx + int(56 * s),  cy + int(38 * s)),
        (cx + int(28 * s),  cy + int(64 * s)),
        (cx,                cy + int(70 * s)),
        (cx - int(28 * s),  cy + int(64 * s)),
        (cx - int(56 * s),  cy + int(38 * s)),
        (cx - int(48 * s),  cy + int(8 * s)),
        (cx - int(54 * s),  cy - int(20 * s)),
        (cx - int(28 * s),  cy - int(56 * s)),
    ]
    painted_blob(img, body_pts, CAT_GREY, outline_thick=5)
    # White belly — organic teardrop
    belly_pts = [
        (cx,             cy + int(2 * s)),
        (cx + int(18 * s), cy + int(28 * s)),
        (cx + int(12 * s), cy + int(58 * s)),
        (cx,             cy + int(64 * s)),
        (cx - int(12 * s), cy + int(58 * s)),
        (cx - int(18 * s), cy + int(28 * s)),
    ]
    painted_blob(img, belly_pts, CAT_WHITE, outline_thick=1)
    # Tabby stripe hints — soft painted dabs, not pixel rectangles
    for dy in (-int(28 * s), -int(8 * s), int(14 * s)):
        ellipse(img, cx - int(38 * s), cy + dy, int(10 * s), 2, CAT_GREY_H)
        ellipse(img, cx + int(38 * s), cy + dy, int(10 * s), 2, CAT_GREY_H)
    return img


def cat_head(big_eyes=False, chunky=False):
    """Cat head — round skull, defined cheek tufts, expressive eyes,
    whiskers, pink triangle nose."""
    img = new_part()
    cx, cy = W // 2, H // 2
    r = 56 if chunky else 48
    # Head silhouette with cheek tufts at the sides
    head_pts = [
        (cx,            cy - r + 4),       # top
        (cx + r // 2,   cy - r * 3 // 4),
        (cx + r,        cy - r // 4),
        (cx + r + 4,    cy + r // 4),       # cheek tuft poking out
        (cx + r * 3 // 4, cy + r * 3 // 4),
        (cx + r // 4,   cy + r),
        (cx,            cy + r + 4),        # chin
        (cx - r // 4,   cy + r),
        (cx - r * 3 // 4, cy + r * 3 // 4),
        (cx - r - 4,    cy + r // 4),       # left cheek tuft
        (cx - r,        cy - r // 4),
        (cx - r // 2,   cy - r * 3 // 4),
    ]
    painted_blob(img, head_pts, CAT_GREY, outline_thick=5)
    # White muzzle/chin patch — heart-ish painted blob
    muzzle_pts = [
        (cx - 16, cy + 4),
        (cx - 18, cy + 18),
        (cx - 8,  cy + 30),
        (cx,      cy + r),
        (cx + 8,  cy + 30),
        (cx + 18, cy + 18),
        (cx + 16, cy + 4),
    ]
    painted_blob(img, muzzle_pts, CAT_WHITE, outline_thick=1)
    # Cheek tuft fur wisps
    fur_tuft(img, cx - r - 2, cy + r // 4, CAT_GREY, length=10, dir_x=-1, dir_y=0)
    fur_tuft(img, cx + r + 2, cy + r // 4, CAT_GREY, length=10, dir_x=1, dir_y=0)
    fur_tuft(img, cx - r // 3, cy - r + 2, CAT_GREY, length=8, dir_x=0, dir_y=-1)
    fur_tuft(img, cx + r // 3, cy - r + 2, CAT_GREY, length=8, dir_x=0, dir_y=-1)
    # Expressive eyes — bigger if Nancy, with slit pupils
    eye_size = 8 if big_eyes else 7
    expressive_eye(img, cx - 16, cy - 4, size=eye_size, iris_color=CAT_GREEN_EYE, look=(0, 1))
    expressive_eye(img, cx + 16, cy - 4, size=eye_size, iris_color=CAT_GREEN_EYE, look=(0, 1))
    # Slit pupils on top of round pupils
    d = ImageDraw.Draw(img)
    d.line([(cx - 16, cy - 4 - eye_size + 2), (cx - 16, cy - 4 + eye_size - 2)], fill=OUTLINE, width=2)
    d.line([(cx + 16, cy - 4 - eye_size + 2), (cx + 16, cy - 4 + eye_size - 2)], fill=OUTLINE, width=2)
    # Triangle pink nose
    nose_pts = [(cx - 5, cy + 6), (cx + 5, cy + 6), (cx, cy + 14)]
    painted_blob(img, nose_pts, CAT_NOSE, outline_thick=2)
    # Mouth — cute "w" shape
    d.arc([cx - 8, cy + 14, cx, cy + 22], start=0, end=180, fill=OUTLINE, width=2)
    d.arc([cx, cy + 14, cx + 8, cy + 22], start=0, end=180, fill=OUTLINE, width=2)
    # Whiskers — actual lines, not just dots
    whiskers(img, cx, cy + 10, span=22, count=3)
    return img


def cat_ear_left(perked=True):
    """Triangle ear with rounded tip + pink inner + tuft fur on the
    outer edge (like real cat ear feathering)."""
    img = new_part()
    cx, cy = W // 2, H // 2
    ear_pts = [
        (cx + 4,  cy - 32),  # tip (slightly inward — toward the center)
        (cx + 16, cy - 8),
        (cx + 20, cy + 14),
        (cx + 6,  cy + 22),
        (cx - 12, cy + 18),
        (cx - 18, cy + 4),
        (cx - 14, cy - 14),
    ]
    painted_blob(img, ear_pts, CAT_GREY, outline_thick=4)
    inner_pts = [
        (cx + 4,  cy - 22),
        (cx + 10, cy - 4),
        (cx + 8,  cy + 14),
        (cx - 6,  cy + 14),
        (cx - 10, cy + 0),
    ]
    painted_blob(img, inner_pts, CAT_PINK, outline_thick=1)
    # Outer edge fur tuft
    fur_tuft(img, cx + 12, cy - 18, CAT_GREY, length=6, dir_x=1, dir_y=-1)
    return img


def cat_ear_right():
    img = new_part()
    cx, cy = W // 2, H // 2
    ear_pts = [
        (cx - 4,  cy - 32),
        (cx - 16, cy - 8),
        (cx - 20, cy + 14),
        (cx - 6,  cy + 22),
        (cx + 12, cy + 18),
        (cx + 18, cy + 4),
        (cx + 14, cy - 14),
    ]
    painted_blob(img, ear_pts, CAT_GREY, outline_thick=4)
    inner_pts = [
        (cx - 4,  cy - 22),
        (cx - 10, cy - 4),
        (cx - 8,  cy + 14),
        (cx + 6,  cy + 14),
        (cx + 10, cy + 0),
    ]
    painted_blob(img, inner_pts, CAT_PINK, outline_thick=1)
    fur_tuft(img, cx - 12, cy - 18, CAT_GREY, length=6, dir_x=-1, dir_y=-1)
    return img


def cat_tail():
    """S-curved cat tail with white tip and faint tabby rings."""
    img = new_part()
    cx, cy = W // 2, H // 2
    tail_pts = [
        (cx - 2,  cy - 50),
        (cx + 8,  cy - 28),
        (cx + 10, cy + 0),
        (cx + 4,  cy + 28),
        (cx - 4,  cy + 50),
        (cx - 8,  cy + 56),
        (cx - 14, cy + 42),
        (cx - 12, cy + 14),
        (cx - 14, cy - 14),
        (cx - 12, cy - 36),
    ]
    painted_blob(img, tail_pts, CAT_GREY, outline_thick=4)
    # White tip
    tip_pts = [
        (cx - 6, cy + 36),
        (cx + 2, cy + 42),
        (cx - 2, cy + 56),
        (cx - 8, cy + 56),
        (cx - 12, cy + 46),
    ]
    painted_blob(img, tip_pts, CAT_WHITE, outline_thick=1)
    # Tabby rings (subtle painted strokes)
    for dy in (-30, -10, 18):
        ellipse(img, cx, cy + dy, 9, 1, CAT_GREY_H)
    return img


def cat_leg(scale=1.0):
    """Cat leg with paw + toe pads."""
    img = new_part()
    cx, cy = W // 2, H // 2
    s = scale
    leg_pts = [
        (cx - int(12 * s), cy - int(28 * s)),
        (cx + int(12 * s), cy - int(28 * s)),
        (cx + int(13 * s), cy),
        (cx + int(10 * s), cy + int(24 * s)),
        (cx,               cy + int(32 * s)),
        (cx - int(10 * s), cy + int(24 * s)),
        (cx - int(13 * s), cy),
    ]
    painted_blob(img, leg_pts, CAT_GREY, outline_thick=4)
    # White paw
    paw_pts = [
        (cx - int(9 * s),  cy + int(14 * s)),
        (cx + int(9 * s),  cy + int(14 * s)),
        (cx + int(8 * s),  cy + int(28 * s)),
        (cx,               cy + int(32 * s)),
        (cx - int(8 * s),  cy + int(28 * s)),
    ]
    painted_blob(img, paw_pts, CAT_WHITE, outline_thick=1)
    # Toe pad dots
    for dx in (-int(4 * s), 0, int(4 * s)):
        ellipse(img, cx + dx, cy + int(24 * s), 1, 1, CAT_PINK)
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
    """Hourglass runner silhouette — broader shoulders/chest, narrower
    waist, broader hips. Asymmetric for lifelike feel."""
    img = new_part()
    cx, cy = W // 2, H // 2
    body_pts = [
        (cx - 4,  cy - 88),  # neck (slightly off-center)
        (cx + 38, cy - 74),  # right shoulder
        (cx + 44, cy - 30),  # right ribcage
        (cx + 30, cy + 0),   # right waist (narrowest)
        (cx + 42, cy + 32),  # right hip
        (cx + 36, cy + 70),  # right thigh
        (cx,      cy + 84),  # crotch
        (cx - 36, cy + 70),
        (cx - 42, cy + 32),
        (cx - 30, cy + 0),
        (cx - 44, cy - 30),
        (cx - 38, cy - 74),
    ]
    painted_blob(img, body_pts, K_PINK, outline_thick=5)
    # Crop-top hem line
    d = ImageDraw.Draw(img)
    d.line([(cx - 38, cy + 36), (cx + 38, cy + 36)], fill=K_PINK_S, width=3)
    # Sports-bra cut-line accent (athletic detail)
    d.arc([cx - 30, cy - 50, cx + 30, cy - 8], start=20, end=160, fill=K_PINK_S, width=2)
    # Apple Watch
    painted_rounded_rect(img, cx - 48, cy - 6, 14, 20, K_BLACK, radius=3)
    ellipse(img, cx - 41, cy + 4, 4, 6, K_SCREEN)
    return img


def katie_head():
    """Brunette athlete head — heart-shaped face, layered hair with
    side bangs, expressive eyes with eyelashes, defined lips."""
    img = new_part()
    cx, cy = W // 2, H // 2
    # Hair crown — organic blob with a side-swept silhouette
    hair_pts = [
        (cx - 4,  cy - 60),  # top peak (slightly off-center for side-sweep)
        (cx + 32, cy - 50),
        (cx + 50, cy - 18),
        (cx + 46, cy + 16),
        (cx + 24, cy + 24),
        (cx,      cy + 18),
        (cx - 24, cy + 24),
        (cx - 46, cy + 16),
        (cx - 50, cy - 18),
        (cx - 28, cy - 52),
    ]
    painted_blob(img, hair_pts, K_HAIR, outline_thick=5)
    # Heart-shaped face below the hair
    face_pts = [
        (cx - 26, cy + 4),    # left temple
        (cx - 22, cy + 24),
        (cx - 14, cy + 44),
        (cx,      cy + 56),   # chin point
        (cx + 14, cy + 44),
        (cx + 22, cy + 24),
        (cx + 26, cy + 4),
        (cx + 14, cy - 6),
        (cx,      cy - 8),
        (cx - 14, cy - 6),
    ]
    painted_blob(img, face_pts, K_SKIN, outline_thick=2)
    # Side-swept bangs — sweeps to one side (cartoon expression)
    bangs_pts = [
        (cx - 24, cy - 4),
        (cx - 8,  cy + 6),
        (cx + 18, cy + 4),
        (cx + 26, cy - 4),
        (cx + 22, cy - 12),
        (cx,      cy - 6),
        (cx - 18, cy - 8),
    ]
    painted_blob(img, bangs_pts, K_HAIR, outline_thick=2)
    # Hair highlight strands (lighter brown, thin lines)
    d = ImageDraw.Draw(img)
    d.line([(cx - 22, cy - 38), (cx - 14, cy - 12)], fill=K_HAIR_H, width=2)
    d.line([(cx + 16, cy - 42), (cx + 26, cy - 8)], fill=K_HAIR_H, width=2)
    d.line([(cx - 6, cy - 50), (cx - 4, cy - 24)], fill=K_HAIR_H, width=1)
    # Expressive eyes — Katie has hazel eyes
    expressive_eye(img, cx - 11, cy + 18, size=5, iris_color=(140, 90, 40, 255), look=(0, 0))
    expressive_eye(img, cx + 11, cy + 18, size=5, iris_color=(140, 90, 40, 255), look=(0, 0))
    # Eyelashes (top)
    for dx in (-15, -12, -9):
        d.line([(cx + dx, cy + 14), (cx + dx - 1, cy + 11)], fill=OUTLINE, width=1)
    for dx in (9, 12, 15):
        d.line([(cx + dx, cy + 14), (cx + dx + 1, cy + 11)], fill=OUTLINE, width=1)
    # Eyebrows (slightly raised — "ugh, can everyone..." vibe)
    d.line([(cx - 16, cy + 6), (cx - 6, cy + 4)], fill=K_HAIR, width=2)
    d.line([(cx + 6, cy + 4), (cx + 16, cy + 6)], fill=K_HAIR, width=2)
    # Nose (subtle, just a soft shadow + tip dot)
    ellipse(img, cx, cy + 30, 3, 2, K_SKIN_S)
    d.arc([cx - 4, cy + 28, cx + 4, cy + 36], start=200, end=340, fill=K_SKIN_S, width=1)
    # Lips — defined cupid's bow
    lip_pts = [
        (cx - 10, cy + 40),
        (cx - 4,  cy + 38),  # upper-left peak
        (cx,      cy + 40),  # cupid bow dip
        (cx + 4,  cy + 38),  # upper-right peak
        (cx + 10, cy + 40),
        (cx + 6,  cy + 46),
        (cx,      cy + 48),
        (cx - 6,  cy + 46),
    ]
    painted_blob(img, lip_pts, K_PINK_S, outline_thick=1)
    # Lip shine
    ellipse(img, cx, cy + 42, 4, 1, lighten(K_PINK_S, 0.4))
    # Tiny earrings (gold studs)
    ellipse(img, cx - 28, cy + 16, 2, 2, (255, 200, 70, 255))
    ellipse(img, cx + 28, cy + 16, 2, 2, (255, 200, 70, 255))
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
    # Rosie — SIDE-3/4 view border collie. Six parts matching the new
    # rosie_config.json rig (body, head, ear, tail, legs-front, legs-back).
    write_parts("rosie", {
        "body": rosie_body(),
        "head": rosie_head(),
        "ear": rosie_ear(),
        "tail": rosie_tail(),
        "legs-front": rosie_legs(front=True),
        "legs-back": rosie_legs(front=False),
    })
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
