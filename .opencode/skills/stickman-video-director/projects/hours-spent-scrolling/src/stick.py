"""Canvas, female stick figure rig and face helpers.

Everything is authored in 1x design space (1280x720); the Canvas scales to
SS (2x) internally so the final downscale gives smooth anti-aliased strokes.
Figure poses are dicts of polylines in local units: feet at (0, 0), head
centre near (0, -88) with radius 12, y negative = up.

Design 07 — the girl behind your screen: a sleek ponytail silhouette with
secondary motion (the tail lags every head move), almond eyes with lid
closure and pupil tracking, brows that tilt curious / skeptical / empathetic
and a multi-shape mouth driven by the speech envelope.
"""
import math

from PIL import Image, ImageDraw

from common import (CREAM, INK, NEON_AMBER, NEON_CYAN, NEON_MAGENTA, SS,
                    clamp, font)

# ------------------------------------------------------------------ poses
# Local units: feet / anchor at (0, 0), y negative = up. Poses face right.

POSE_TAP = {                      # close-up: knuckles up, knocking on glass
    "head": (3, -88, 12),
    "spine": [(2, -76), (0, -44)],
    "armL": [(2, -72), (-13, -58), (-19, -43)],
    "armR": [(2, -72), (21, -78), (33, -93)],
    "legL": [(0, -44), (-13, -22), (-15, 0)],
    "legR": [(0, -44), (13, -22), (16, 0)],
}

POSE_POINT = {                     # arm out, calling out the viewer
    "head": (3, -88, 12),
    "spine": [(2, -76), (0, -44)],
    "armL": [(2, -72), (-13, -58), (-19, -43)],
    "armR": [(2, -72), (26, -70), (47, -75)],
    "legL": [(0, -44), (-13, -22), (-15, 0)],
    "legR": [(0, -44), (13, -22), (16, 0)],
}

POSE_SWIPE_UP = {                  # thumb flicking the feed upward
    "head": (1, -88, 12),
    "spine": [(1, -76), (0, -44)],
    "armL": [(1, -72), (-14, -58), (-19, -44)],
    "armR": [(1, -72), (20, -66), (31, -85)],
    "legL": [(0, -44), (-13, -22), (-15, 0)],
    "legR": [(0, -44), (13, -22), (16, 0)],
}

POSE_SWIPE_DOWN = {                # ...and pulling the next one down
    "head": (1, -87, 12),
    "spine": [(1, -76), (0, -44)],
    "armL": [(1, -72), (-14, -58), (-19, -44)],
    "armR": [(1, -72), (22, -64), (33, -49)],
    "legL": [(0, -44), (-13, -22), (-15, 0)],
    "legR": [(0, -44), (13, -22), (16, 0)],
}

POSE_HIP = {                       # hands on hips, deadpan at the counter
    "head": (0, -88, 12),
    "spine": [(0, -76), (0, -44)],
    "armL": [(0, -72), (-19, -60), (-14, -46)],
    "armR": [(0, -72), (19, -60), (14, -46)],
    "legL": [(0, -44), (-14, -22), (-17, 0)],
    "legR": [(0, -44), (14, -22), (17, 0)],
}

POSE_CALM = {                      # relaxed stand, one hand loose
    "head": (1, -88, 12),
    "spine": [(1, -76), (0, -44)],
    "armL": [(1, -72), (-14, -58), (-18, -42)],
    "armR": [(1, -72), (15, -57), (20, -40)],
    "legL": [(0, -44), (-13, -22), (-15, 0)],
    "legR": [(0, -44), (13, -22), (16, 0)],
}

POSE_SOFT = {                      # hand up near the chin, listening
    "head": (2, -88, 12),
    "spine": [(1, -76), (0, -44)],
    "armL": [(1, -72), (-14, -58), (-18, -43)],
    "armR": [(1, -72), (22, -64), (10, -74)],
    "legL": [(0, -44), (-13, -22), (-15, 0)],
    "legR": [(0, -44), (13, -22), (16, 0)],
}

POSE_GESTURE_OPEN = {              # open palm offered toward the camera
    "head": (2, -88, 12),
    "spine": [(1, -76), (0, -44)],
    "armL": [(1, -72), (-14, -58), (-18, -43)],
    "armR": [(1, -72), (24, -68), (42, -72)],
    "legL": [(0, -44), (-13, -22), (-15, 0)],
    "legR": [(0, -44), (13, -22), (16, 0)],
}

POSE_REACH = {                     # leaning in, arm out to the switch
    "head": (5, -89, 12),
    "spine": [(3, -77), (0, -44)],
    "armL": [(3, -73), (-12, -58), (-18, -43)],
    "armR": [(3, -73), (30, -74), (54, -70)],
    "legL": [(0, -44), (-15, -22), (-19, 0)],
    "legR": [(0, -44), (15, -22), (20, 0)],
}


# ------------------------------------------------------------------ canvas

class Ctx:
    def __init__(self, img):
        self.img = img
        self.d = ImageDraw.Draw(img, "RGBA")
        self.w = img.width / SS
        self.h = img.height / SS

    # -- internals -----------------------------------------------------
    def _s(self, p):
        return (p[0] * SS, p[1] * SS)

    def _box(self, box):
        return [box[0] * SS, box[1] * SS, box[2] * SS, box[3] * SS]

    # -- shapes --------------------------------------------------------
    def line(self, pts, fill=CREAM, w=6):
        if len(pts) == 1:
            self.dot(pts[0], w, fill)
            return
        pts2 = [self._s(p) for p in pts]
        w2 = max(1, int(round(w * SS)))
        self.d.line(pts2, fill=fill, width=w2, joint="curve")
        r = w2 / 2.0
        for p in (pts2[0], pts2[-1]):
            self.d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=fill)

    def dot(self, c, d, fill=CREAM):
        r = d / 2.0 * SS
        x, y = self._s(c)
        self.d.ellipse([x - r, y - r, x + r, y + r], fill=fill)

    def circle(self, c, r, fill=None, outline=None, w=6):
        box = [c[0] - r, c[1] - r, c[0] + r, c[1] + r]
        self.d.ellipse(self._box(box), fill=fill, outline=outline,
                       width=max(1, int(round(w * SS))) if outline else 0)

    def ellipse(self, box, fill=None, outline=None, w=6):
        self.d.ellipse(self._box(box), fill=fill, outline=outline,
                       width=max(1, int(round(w * SS))) if outline else 0)

    def rrect(self, box, r, fill=None, outline=None, w=6):
        self.d.rounded_rectangle(self._box(box), radius=r * SS, fill=fill,
                                 outline=outline,
                                 width=max(1, int(round(w * SS))) if outline else 0)

    def poly(self, pts, fill=None, outline=None, w=6):
        pts2 = [self._s(p) for p in pts]
        self.d.polygon(pts2, fill=fill, outline=outline,
                       width=max(1, int(round(w * SS))) if outline else 0)

    def arc(self, box, a0, a1, fill=CREAM, w=6):
        self.d.arc(self._box(box), a0, a1, fill=fill,
                   width=max(1, int(round(w * SS))))

    def text(self, xy, s, size=30, fill=(255, 255, 255), anchor="la",
             bold=True, stroke=0, stroke_fill=INK, spacing=4):
        self.d.text(self._s(xy), s, font=font(size, bold), fill=fill,
                    anchor=anchor, stroke_width=int(stroke * SS),
                    stroke_fill=stroke_fill, spacing=int(spacing * SS))

    def glow(self, c, r, color, alpha=70, rings=6):
        a = max(1, alpha // rings)
        for i in range(rings, 0, -1):
            rr = r * i / rings
            self.circle(c, rr, fill=tuple(color[:3]) + (a,))

    def paste(self, img2x):
        self.img.paste(img2x, (0, 0))

    def layer(self):
        return Image.new("RGBA", self.img.size, (0, 0, 0, 0))


# ------------------------------------------------------------------ blink

def blink_closed(lt, seed=0.0, period=3.05):
    """Eyelid closure 0..1 (0 open, 1 shut): a crisp blink on a loose period
    with an occasional double blink, so the eyes never look mechanical."""
    if lt < 0:
        return 0.0
    u = lt + seed
    cyc = int(u // period)
    ph = (u % period) / period
    if ph < 0.050:                                   # main blink
        return math.sin(math.pi * (ph / 0.050))
    if cyc % 3 == 1 and 0.082 <= ph < 0.120:         # double blink
        return 0.92 * math.sin(math.pi * ((ph - 0.082) / 0.038))
    return 0.0


# ------------------------------------------------------------------ brows
# (inner-left, outer-left, inner-right, outer-right) in head-radius units,
# negative = raised (y is up).

BROWS = {
    "neutral":    (0.00, 0.01, 0.00, 0.01),
    "curious":    (-0.10, -0.03, -0.15, -0.05),
    "skeptical":  (-0.03, 0.02, -0.16, -0.07),
    "deadpan":    (0.04, 0.04, 0.04, 0.04),
    "surprised":  (-0.17, -0.13, -0.17, -0.13),
    "empathetic": (-0.11, 0.05, -0.11, 0.05),
    "soft":       (-0.05, -0.01, -0.05, -0.01),
}


# ------------------------------------------------------------------ face

def _mouth(P, r, shape, openness, color, fw, ctx):
    """Multi-shape mouth. `openness` 0..1 stretches the open shapes so the
    lips track the speech envelope instead of popping between symbols."""
    o = clamp(openness)
    mx, my = P(0.0, 0.40)
    if shape == "smile":
        ctx.arc([mx - 0.30 * r, my - 0.20 * r, mx + 0.30 * r, my + 0.16 * r],
                25, 155, fill=color, w=fw)
        return
    if shape == "press":
        ctx.line([(mx - 0.20 * r, my), (mx + 0.20 * r, my)],
                 fill=color, w=fw)
        ctx.line([(mx - 0.20 * r, my), (mx - 0.16 * r, my + 0.05 * r)],
                 fill=color, w=fw * 0.8)
        ctx.line([(mx + 0.20 * r, my), (mx + 0.16 * r, my + 0.05 * r)],
                 fill=color, w=fw * 0.8)
        return
    if shape == "flat" or o < 0.16:
        ctx.line([(mx - 0.24 * r, my), (mx + 0.22 * r, my)],
                 fill=color, w=fw)
        return
    if shape == "o":
        rx, ry = 0.13 * r, (0.07 + 0.13 * o) * r
    elif shape == "wide":
        rx, ry = (0.20 + 0.09 * o) * r, (0.05 + 0.11 * o) * r
    elif shape == "u":
        rx, ry = (0.15 + 0.05 * o) * r, (0.06 + 0.12 * o) * r
    else:                                              # "open"
        rx, ry = (0.14 + 0.06 * o) * r, (0.05 + 0.15 * o) * r
    ctx.ellipse([mx - rx, my - ry, mx + rx, my + ry], fill=color)
    if shape == "u":
        ctx.arc([mx - rx, my - ry, mx + rx, my + ry], 20, 160,
                fill=color, w=fw)


def _almond(cx, cy, hw, hh):
    """Eye outline: shallow upper lid, flatter lower lid."""
    pts = []
    n = 10
    for i in range(n + 1):
        u = i / n
        pts.append((cx - hw + 2 * hw * u,
                    cy - hh * math.sin(math.pi * u) ** 0.8))
    for i in range(n + 1):
        u = 1 - i / n
        pts.append((cx - hw + 2 * hw * u,
                    cy + hh * 0.62 * math.sin(math.pi * u) ** 1.25))
    return pts


def girl_face(ctx, T, hx, hy, hr, s, look=(0.0, 0.0), lid=0.0,
              brow="neutral", mouth="flat", openness=0.0,
              color=CREAM, w=8, a=255):
    """Face inside the head of a girl silhouette.

    All geometry is authored in head-local fractions (1.0 = head radius) and
    pushed through T, so flip / rotation / tilt carry the face with them.
    look:  -1..1 gaze offset (x, y) in head-radius fractions
    lid:   0 open .. 1 closed (blink)
    """
    col = tuple(color[:3]) + (a,)
    r = hr * s                                    # world head radius
    fw = max(2.0, w * 0.5 * min(1.7, 0.62 + s * 0.16))

    def P(dx, dy):
        return T((hx + dx * hr, hy + dy * hr))

    # ---- eyes: almond + pupil + lash ticks
    ex, ey, ew, eh = 0.36, -0.07, 0.205, 0.14
    open_k = 1.0 - 0.94 * clamp(lid)
    for sx in (-1, 1):
        cx, cy = P(sx * ex, ey)
        hw = ew * r
        hh = eh * r * open_k
        if hh < r * 0.035:                        # closed: lash line
            ctx.arc([cx - hw, cy - hw * 0.55, cx + hw, cy + hw * 0.55],
                    20, 160, fill=col, w=fw)
        else:
            ctx.poly(_almond(cx, cy, hw, hh), fill=col)
            # pupil tracks the camera / floating cards
            pr = max(1.5, 0.062 * r)
            px = cx + clamp(look[0]) * 0.075 * r
            py = cy + clamp(look[1]) * 0.06 * r
            py = max(cy - hh * 0.5, min(cy + hh * 0.45, py))
            ctx.circle((px, py), pr, fill=INK + (a,))
            if hh > r * 0.07:
                ctx.circle((px + pr * 0.34, py - pr * 0.34), pr * 0.30,
                           fill=col)
            # upper lash line + outer flick
            ctx.line([(cx - hw, cy - hh * 0.1),
                      (cx, cy - hh * 1.02),
                      (cx + hw, cy - hh * 0.05)],
                     fill=col, w=fw * 1.15)
            fx, fy = cx + sx * hw, cy - hh * 0.1
            ctx.line([(fx, fy), (fx + sx * hw * 0.34, fy - hh * 0.55)],
                     fill=col, w=fw * 0.85)

    # ---- brows
    lifts = BROWS.get(brow, BROWS["neutral"])
    by = -0.34
    for i, sx in enumerate((-1, 1)):
        li, lo = lifts[2 * i], lifts[2 * i + 1]
        p0 = P(sx * 0.14, by + li)
        p1 = P(sx * 0.35, by + (li + lo) * 0.5 - 0.025)
        p2 = P(sx * 0.57, by + lo)
        ctx.line([p0, p1, p2], fill=col, w=fw)

    # ---- mouth
    _mouth(P, r, mouth, openness, col, fw, ctx)


# --------------------------------------------------------- hair + silhouette

def _hair_poly(hx, hy, hr):
    """Hair cap: outer skull arc over the top, inner hairline sweep back."""
    outer = []
    n = 16
    for i in range(n + 1):
        ang = math.pi * (1.0 + i / n)             # 180 -> 360 deg, y-down
        outer.append((hx + hr * 1.05 * math.cos(ang),
                      hy + hr * 1.05 * math.sin(ang)))
    inner = [
        (hx + 0.97 * hr, hy - 0.14 * hr),
        (hx + 0.55 * hr, hy - 0.50 * hr),
        (hx + 0.05 * hr, hy - 0.58 * hr),
        (hx - 0.48 * hr, hy - 0.47 * hr),
        (hx - 0.93 * hr, hy - 0.12 * hr),
    ]
    return outer + inner


def _lock_poly(hx, hy, hr):
    """Side lock falling in front of the ear (her leading side)."""
    return [(hx + 0.93 * hr, hy - 0.20 * hr),
            (hx + 1.07 * hr, hy - 0.04 * hr),
            (hx + 1.01 * hr, hy + 0.40 * hr),
            (hx + 0.85 * hr, hy + 0.64 * hr),
            (hx + 0.76 * hr, hy + 0.30 * hr),
            (hx + 0.82 * hr, hy - 0.06 * hr)]


def _pony_pts(hx, hy, hr, sway):
    """Ponytail polyline — `sway` is the secondary-motion lag in head radii
    (the tip lags 1.7x the root, so every head move whips the tail)."""
    k = sway * hr
    return [(hx - 0.66 * hr, hy - 0.74 * hr),
            (hx - 1.10 * hr, hy - 0.66 * hr + k * 0.25),
            (hx - 1.52 * hr, hy - 0.40 * hr + k * 0.60),
            (hx - 1.76 * hr, hy - 0.02 * hr + k * 1.00),
            (hx - 1.70 * hr, hy + 0.44 * hr + k * 1.45),
            (hx - 1.44 * hr, hy + 0.72 * hr + k * 1.70)]


def _xf(pose, x, y, s, flip, rot, off=(0.0, 0.0)):
    ca, sa = math.cos(rot), math.sin(rot)

    def T(p):
        lx, ly = p
        if flip:
            lx = -lx
        rx = lx * ca - ly * sa
        ry = lx * sa + ly * ca
        return (x + off[0] + rx * s, y + off[1] + ry * s)
    return T


def girl_silhouette(ctx, x, y, s, pose, rim=NEON_CYAN, rim2=NEON_MAGENTA,
                    body=(5, 7, 14), w=8, flip=False, rot=0.0,
                    off_a=(-8, -7), off_b=(7, 5), sway=0.0,
                    look=(0.0, 0.0), lid=0.0, brow="neutral",
                    mouth="flat", openness=0.0, face=True, a=255,
                    tie=NEON_AMBER):
    """Sharp dark silhouette with double-offset neon rim light.

    Two offset passes (cyan / magenta) are drawn first — including hair and
    ponytail — then the black body pass on top, so only a crescent of rim
    survives along the silhouette edge: the cinematic look. The face is
    drawn last, inside the black pass, in the leading rim colour.
    """
    hx, hy, hr = pose["head"]
    passes = []
    if rim:
        passes.append((off_a, rim))
    if rim2:
        passes.append((off_b, rim2))

    def draw_pass(off, col):
        T = _xf(pose, x, y, s, flip, rot, off)
        c = tuple(col[:3]) + (a,)
        for key in ("spine", "armL", "armR", "legL", "legR"):
            if key in pose:
                ctx.line([T(p) for p in pose[key]], fill=c, w=w)
        ctx.line([T(p) for p in _pony_pts(hx, hy, hr, sway)],
                 fill=c, w=int(round(w * 1.25)))
        ctx.circle(T((hx, hy)), hr * s, fill=c)
        ctx.poly([T(p) for p in _hair_poly(hx, hy, hr)], fill=c)
        ctx.poly([T(p) for p in _lock_poly(hx, hy, hr)], fill=c)
        return T

    for off, col in passes:
        draw_pass(off, col)
    T = draw_pass((0.0, 0.0), body)

    # amber hair tie at the tail base
    if tie:
        tx, ty = _pony_pts(hx, hy, hr, sway)[1]
        p0 = T((tx, ty - 0.16 * hr))
        p1 = T((tx, ty + 0.16 * hr))
        ctx.line([p0, p1], fill=tuple(tie[:3]) + (a,), w=max(2, int(w * 0.8)))

    if face:
        girl_face(ctx, T, hx, hy, hr, s, look=look, lid=lid, brow=brow,
                  mouth=mouth, openness=openness, color=rim or CREAM,
                  w=w, a=a)
    return T
