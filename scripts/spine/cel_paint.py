"""
cel_paint.py — shared painting helpers for the Spine cel-animation pipeline.

Aim: Magic Design Studios-style hand-painted 2D — variable line weight,
multi-tone painted shading (base + shadow + highlight + rim light),
soft drop shadows for grounding, painterly textures.

Used by draw_characters_parts.py, draw_influencer_parts.py, draw_enemies.py
and draw_katy_trail_tile.py — the public API is small and consistent.

Color: pass an RGBA tuple. Helpers derive shadow/highlight from it
automatically unless you override.
"""
from __future__ import annotations
from PIL import Image, ImageDraw, ImageFilter
from math import cos, sin, radians

INK = (18, 22, 28, 255)
SS = 4  # supersample factor for AA


# ── Color math ────────────────────────────────────────────────────────────

def _clamp(v: int) -> int:
    return max(0, min(255, v))


def darken(c, amt=0.35):
    return (
        _clamp(int(c[0] * (1 - amt))),
        _clamp(int(c[1] * (1 - amt))),
        _clamp(int(c[2] * (1 - amt))),
        c[3] if len(c) > 3 else 255,
    )


def lighten(c, amt=0.30):
    return (
        _clamp(int(c[0] + (255 - c[0]) * amt)),
        _clamp(int(c[1] + (255 - c[1]) * amt)),
        _clamp(int(c[2] + (255 - c[2]) * amt)),
        c[3] if len(c) > 3 else 255,
    )


def saturate(c, amt=0.15):
    """Push a color toward higher saturation by enhancing the dominant
    channel."""
    r, g, b = c[:3]
    mx = max(r, g, b)
    if mx == 0:
        return c
    factor = 1 + amt
    nr = _clamp(int(r * factor)) if r == mx else r
    ng = _clamp(int(g * factor)) if g == mx else g
    nb = _clamp(int(b * factor)) if b == mx else b
    return (nr, ng, nb, c[3] if len(c) > 3 else 255)


# ── Anti-aliased shape primitives ────────────────────────────────────────

def aa_ellipse(img: Image.Image, cx: int, cy: int, rx: int, ry: int, color):
    if rx <= 0 or ry <= 0:
        return
    pad = 4
    big = Image.new("RGBA", ((rx + pad) * 2 * SS, (ry + pad) * 2 * SS), (0, 0, 0, 0))
    ImageDraw.Draw(big).ellipse(
        [pad * SS, pad * SS, (rx * 2 + pad) * SS, (ry * 2 + pad) * SS],
        fill=color,
    )
    small = big.resize(((rx + pad) * 2, (ry + pad) * 2), Image.LANCZOS)
    img.alpha_composite(small, (cx - rx - pad, cy - ry - pad))


def aa_polygon(img: Image.Image, points: list[tuple[float, float]], color):
    """Anti-aliased polygon by supersampling + LANCZOS downsample."""
    if not points:
        return
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    minx, maxx = int(min(xs)) - 4, int(max(xs)) + 4
    miny, maxy = int(min(ys)) - 4, int(max(ys)) + 4
    w = maxx - minx
    h = maxy - miny
    if w <= 0 or h <= 0:
        return
    big = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    shifted = [((p[0] - minx) * SS, (p[1] - miny) * SS) for p in points]
    ImageDraw.Draw(big).polygon(shifted, fill=color)
    small = big.resize((w, h), Image.LANCZOS)
    img.alpha_composite(small, (minx, miny))


def _catmull_rom(p0, p1, p2, p3, t):
    t2 = t * t
    t3 = t2 * t
    x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t +
               (2*p0[0] - 5*p1[0] + 4*p2[0] - p3[0]) * t2 +
               (-p0[0] + 3*p1[0] - 3*p2[0] + p3[0]) * t3)
    y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t +
               (2*p0[1] - 5*p1[1] + 4*p2[1] - p3[1]) * t2 +
               (-p0[1] + 3*p1[1] - 3*p2[1] + p3[1]) * t3)
    return (x, y)


def smooth_curve(control_points: list[tuple[float, float]], samples_per_segment: int = 12, closed: bool = True) -> list[tuple[float, float]]:
    """Catmull-Rom spline through the control points. Returns a dense
    list of (x, y) coords suitable for filling as a polygon. The curve
    passes THROUGH each control point with smooth tangents — so giving
    a few key points produces an organic, hand-drawn-feeling silhouette
    instead of a stiff ellipse."""
    n = len(control_points)
    if n < 3:
        return list(control_points)
    out: list[tuple[float, float]] = []
    if closed:
        # Wrap indices so the curve closes smoothly.
        for i in range(n):
            p0 = control_points[(i - 1) % n]
            p1 = control_points[i]
            p2 = control_points[(i + 1) % n]
            p3 = control_points[(i + 2) % n]
            for j in range(samples_per_segment):
                out.append(_catmull_rom(p0, p1, p2, p3, j / samples_per_segment))
    else:
        for i in range(n - 1):
            p0 = control_points[max(0, i - 1)]
            p1 = control_points[i]
            p2 = control_points[i + 1]
            p3 = control_points[min(n - 1, i + 2)]
            for j in range(samples_per_segment):
                out.append(_catmull_rom(p0, p1, p2, p3, j / samples_per_segment))
        out.append(control_points[-1])
    return out


def painted_blob(
    img: Image.Image,
    control_points: list[tuple[float, float]],
    base,
    *,
    shadow=None,
    highlight=None,
    outline_thick=6,
    light_dir=(-1, -1),
):
    """Paint an organic blob shape from control points (smoothed via
    Catmull-Rom). Same painted treatment as painted_ellipse: variable-
    weight ink, base, painted shadow, cel highlight, rim light."""
    sh = shadow or darken(base, 0.30)
    hl = highlight or lighten(base, 0.28)
    rm = lighten(base, 0.55)

    silhouette = smooth_curve(control_points, samples_per_segment=14)

    # Compute centroid for shading offsets
    cx = sum(p[0] for p in silhouette) / len(silhouette)
    cy = sum(p[1] for p in silhouette) / len(silhouette)
    rx = max(p[0] for p in silhouette) - min(p[0] for p in silhouette)
    ry = max(p[1] for p in silhouette) - min(p[1] for p in silhouette)
    rx /= 2; ry /= 2

    dx, dy = -light_dir[0], -light_dir[1]

    # Variable-weight ink: thicker shadow-side outline
    expanded = [
        (p[0] + (p[0] - cx) * (outline_thick + 2) / max(1, rx) + dx * 1,
         p[1] + (p[1] - cy) * (outline_thick + 2) / max(1, ry) + dy * 1)
        for p in silhouette
    ]
    aa_polygon(img, expanded, INK)
    expanded2 = [
        (p[0] + (p[0] - cx) * (outline_thick - 1) / max(1, rx),
         p[1] + (p[1] - cy) * (outline_thick - 1) / max(1, ry))
        for p in silhouette
    ]
    aa_polygon(img, expanded2, INK)

    # Base
    aa_polygon(img, silhouette, base)

    # Painted shadow on the side opposite the light
    sh_off_x = max(2, int(rx * 0.18)) * dx
    sh_off_y = max(2, int(ry * 0.18)) * dy
    sh_pts = [
        (cx + (p[0] - cx) * 0.82 + sh_off_x,
         cy + (p[1] - cy) * 0.82 + sh_off_y)
        for p in silhouette
    ]
    aa_polygon(img, sh_pts, (sh[0], sh[1], sh[2], 180))

    # Highlight on the lit side (smaller blob, offset toward light)
    hl_off_x = max(2, int(rx * 0.22)) * (-dx)
    hl_off_y = max(2, int(ry * 0.22)) * (-dy)
    hl_pts = [
        (cx + (p[0] - cx) * 0.45 + hl_off_x,
         cy + (p[1] - cy) * 0.45 + hl_off_y)
        for p in silhouette
    ]
    aa_polygon(img, hl_pts, (hl[0], hl[1], hl[2], 200))

    # Rim light: thin bright crescent along the upper edge
    rim_pts = [
        (cx + (p[0] - cx) * 0.95 + (-dx) * 1,
         cy + (p[1] - cy) * 0.95 + (-dy) * 1)
        for p in silhouette
        if p[1] < cy + ry * 0.1  # only the upper half
    ]
    if len(rim_pts) >= 3:
        aa_polygon(img, rim_pts, (rm[0], rm[1], rm[2], 90))


def aa_rounded_rect(img, x, y, w, h, color, radius=6):
    pad = 4
    big = Image.new("RGBA", ((w + pad * 2) * SS, (h + pad * 2) * SS), (0, 0, 0, 0))
    ImageDraw.Draw(big).rounded_rectangle(
        [pad * SS, pad * SS, (w + pad) * SS, (h + pad) * SS],
        radius=radius * SS,
        fill=color,
    )
    small = big.resize((w + pad * 2, h + pad * 2), Image.LANCZOS)
    img.alpha_composite(small, (x - pad, y - pad))


# ── Painted form (the workhorse) ─────────────────────────────────────────

def painted_ellipse(
    img: Image.Image,
    cx: int, cy: int, rx: int, ry: int,
    base,
    *,
    shadow=None,
    highlight=None,
    rim=None,
    outline_top=4,
    outline_bottom=7,
    light_dir=(-1, -1),  # upper-left light source
):
    """Paint an ellipse Magic-Design-style:
      1. Variable-thickness ink silhouette (thinner top, thicker bottom)
      2. Base color fill
      3. Painted shadow on the side away from the light
      4. Cel highlight on the side toward the light
      5. Subtle rim light along the lit silhouette edge
    """
    sh = shadow or darken(base, 0.30)
    hl = highlight or lighten(base, 0.28)
    rm = rim or lighten(base, 0.55)

    # Variable-thickness outline: paint a slightly bigger oval offset toward
    # the shadow side so the ink line reads thicker on the bottom-right.
    dx, dy = -light_dir[0], -light_dir[1]  # shadow direction
    aa_ellipse(img, cx + dx, cy + dy, rx + outline_bottom, ry + outline_bottom, INK)
    # And a thinner outline pass on the lit side
    aa_ellipse(img, cx, cy, rx + outline_top, ry + outline_top, INK)

    # Base fill
    aa_ellipse(img, cx, cy, rx, ry, base)

    # Painted shadow (offset toward shadow side, smaller, semi-transparent)
    sh_alpha = (sh[0], sh[1], sh[2], 180)
    sx = cx + max(2, rx // 5) * dx
    sy = cy + max(2, ry // 5) * dy
    aa_ellipse(img, sx, sy, int(rx * 0.78), int(ry * 0.78), sh_alpha)

    # Cel highlight (lit side)
    hx = cx - max(2, rx // 5) * dx
    hy = cy - max(2, ry // 5) * dy
    hl_alpha = (hl[0], hl[1], hl[2], 200)
    aa_ellipse(img, hx, hy, max(2, rx // 3), max(2, ry // 3), hl_alpha)

    # Rim light — small bright crescent on the upper edge
    rm_alpha = (rm[0], rm[1], rm[2], 160)
    aa_ellipse(img, hx, cy - ry + 3, max(2, rx // 4), 2, rm_alpha)


def painted_rounded_rect(img, x, y, w, h, base, *, shadow=None, highlight=None, radius=4):
    sh = shadow or darken(base, 0.30)
    hl = highlight or lighten(base, 0.28)
    # Variable-thickness outline (fudge: bigger box on shadow side)
    aa_rounded_rect(img, x - 4, y - 3, w + 8, h + 8, INK, radius=radius + 2)
    aa_rounded_rect(img, x - 3, y - 4, w + 6, h + 7, INK, radius=radius + 2)
    aa_rounded_rect(img, x, y, w, h, base, radius=radius)
    # Cel highlight at the top
    aa_rounded_rect(img, x + 2, y + 2, max(2, w // 2), max(2, h // 4), (hl[0], hl[1], hl[2], 180), radius=radius)
    # Shadow at the bottom
    aa_rounded_rect(img, x + w // 4, y + h - max(3, h // 3), max(2, w // 2), max(3, h // 3), (sh[0], sh[1], sh[2], 150), radius=radius)


# ── Drop shadow ──────────────────────────────────────────────────────────

def drop_shadow(img: Image.Image, cx: int, cy: int, rx: int, ry: int, alpha=120):
    """Soft elliptical drop shadow on the ground beneath a character."""
    pad = 8
    big = Image.new("RGBA", ((rx + pad) * 2, (ry + pad) * 2), (0, 0, 0, 0))
    ImageDraw.Draw(big).ellipse([pad, pad, rx * 2 + pad, ry * 2 + pad], fill=(0, 0, 0, alpha))
    big = big.filter(ImageFilter.GaussianBlur(4))
    img.alpha_composite(big, (cx - rx - pad, cy - ry - pad))


# ── Painterly background fill ────────────────────────────────────────────

def painterly_field(
    img: Image.Image,
    x0: int, x1: int, y0: int, y1: int,
    base,
    *,
    light=None,
    dark=None,
    light_band_y=0.18,
    dark_band_y=0.62,
    blur=18,
):
    """Fill a rectangle with a base color, then overlay soft horizontal
    light and shadow bands (gaussian-blurred) for painted depth."""
    light = light or lighten(base, 0.20)
    dark = dark or darken(base, 0.25)
    h = y1 - y0
    overlay_w = x1 - x0
    base_layer = Image.new("RGBA", (overlay_w, h), base)
    img.alpha_composite(base_layer, (x0, y0))

    # Light + dark band overlay
    band = Image.new("RGBA", (overlay_w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    ly = int(h * light_band_y)
    dy = int(h * dark_band_y)
    bd.rectangle([0, ly - 8, overlay_w, ly + 12], fill=(*light[:3], 90))
    bd.rectangle([0, dy - 8, overlay_w, dy + 14], fill=(*dark[:3], 90))
    band = band.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(band, (x0, y0))


# ── Painterly brushed accent (stippled but smooth) ───────────────────────

def brush_dabs(img: Image.Image, points: list[tuple[int, int]], color, sz=3, alpha=180):
    """Place soft dabs of color (not pixel scatter)."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    for x, y in points:
        ImageDraw.Draw(layer).ellipse([x - sz, y - sz, x + sz, y + sz], fill=(*color[:3], alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(2))
    img.alpha_composite(layer)
