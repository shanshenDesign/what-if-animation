"""Canvas, stickman figure rig and face helpers.

Everything is authored in 1x design space (1280x720); the Canvas scales to
SS (2x) internally so the final downscale gives smooth anti-aliased strokes.
Figure poses are dicts of polylines in local units: feet at (0, 0), head top
near (0, -100), y negative = up.
"""
import math

from PIL import Image, ImageDraw

from common import CREAM, INK, SS, font

# ------------------------------------------------------------------ poses

POSE_STAND = {
    "head": (0, -88, 12),
    "spine": [(0, -76), (0, -44)],
    "armL": [(0, -72), (-15, -57), (-21, -40)],
    "armR": [(0, -72), (15, -57), (21, -40)],
    "legL": [(0, -44), (-13, -22), (-15, 0)],
    "legR": [(0, -44), (13, -22), (15, 0)],
}

POSE_SIT = {                       # sitting up on the bed, legs out on the blanket
    "head": (0, -88, 12),
    "spine": [(0, -76), (0, -44)],
    "armL": [(0, -72), (-14, -58), (-17, -44)],
    "armR": [(0, -72), (14, -58), (17, -44)],
    "legL": [(0, -44), (-34, -46), (-64, -45)],
    "legR": [(0, -44), (-30, -42), (-58, -43)],
}

POSE_REACH = {                     # sitting, reaching right toward the phone
    "head": (2, -88, 12),
    "spine": [(2, -76), (0, -44)],
    "armL": [(0, -72), (-14, -58), (-17, -44)],
    "armR": [(0, -72), (24, -62), (30, -48)],
    "legL": [(0, -44), (-34, -46), (-64, -45)],
    "legR": [(0, -44), (-30, -42), (-58, -43)],
}

POSE_CHEST = {                     # sitting calm, hand on chest
    "head": (0, -88, 12),
    "spine": [(0, -76), (0, -44)],
    "armL": [(0, -72), (-14, -58), (-17, -44)],
    "armR": [(0, -72), (28, -66), (8, -57)],
    "legL": [(0, -44), (-34, -46), (-64, -45)],
    "legR": [(0, -44), (-30, -42), (-58, -43)],
}


def walk_pose(p):
    """Walk cycle phase p in [0,1) — legs and arms swing in opposition."""
    a = math.sin(2 * math.pi * p)
    b = math.sin(2 * math.pi * p + math.pi)

    def leg(swing):
        foot_y = -max(0.0, swing) * 7.0
        return [(0, -44), (13 * swing, -24 + abs(swing) * 2), (25 * swing, foot_y)]

    def arm(swing):
        return [(0, -72), (13 * swing, -58), (22 * swing, -46)]

    return {
        "head": (2 * a, -88, 12),
        "spine": [(0, -76), (0, -44)],
        "armL": arm(b), "armR": arm(a),
        "legL": leg(a), "legR": leg(b),
    }


POSE_WAVE = {                      # standing, right arm up waving
    "head": (0, -88, 12),
    "spine": [(0, -76), (0, -44)],
    "armL": [(0, -72), (-15, -57), (-21, -40)],
    "armR": [(0, -72), (17, -84), (30, -95)],
    "legL": [(0, -44), (-13, -22), (-15, 0)],
    "legR": [(0, -44), (13, -22), (15, 0)],
}

POSE_WAVE_DOWN = {                 # wave failed: arm dropped, head tilted
    "head": (2, -86, 12),
    "spine": [(0, -76), (0, -44)],
    "armL": [(0, -72), (-15, -57), (-21, -40)],
    "armR": [(0, -72), (15, -56), (18, -38)],
    "legL": [(0, -44), (-13, -22), (-15, 0)],
    "legR": [(0, -44), (13, -22), (15, 0)],
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


# ------------------------------------------------------------------ figure

def figure(ctx, x, y, s, pose, w=6, color=CREAM, flip=False, rot=0.0):
    """Draw a stickman. (x, y) = ground anchor, s = local units -> px scale."""
    ca, sa = math.cos(rot), math.sin(rot)

    def T(p):
        lx, ly = p
        if flip:
            lx = -lx
        rx = lx * ca - ly * sa
        ry = lx * sa + ly * ca
        return (x + rx * s, y + ry * s)

    for key in ("spine", "armL", "armR", "legL", "legR"):
        if key in pose:
            ctx.line([T(p) for p in pose[key]], fill=color, w=w)
    if "head" in pose:
        hx, hy, hr = pose["head"]
        ctx.circle(T((hx, hy)), hr * s, fill=None, outline=color, w=w)
    for prop in pose.get("props", []):
        kind = prop[0]
        if kind == "poly":
            ctx.poly([T(p) for p in prop[1]], fill=prop[2])
        elif kind == "circle":
            ctx.circle(T(prop[1]), prop[2] * s, fill=prop[3])
        elif kind == "rrect":
            box = prop[1]
            p1, p2 = T((box[0], box[1])), T((box[2], box[3]))
            ctx.rrect([p1[0], p1[1], p2[0], p2[1]], prop[2], fill=prop[3])
    return T  # anchor transform so callers can place props/faces


# ------------------------------------------------------------------ face

def face(ctx, c, r, look=(0.0, 0.0), closed=False, brow=None, mouth=None,
         color=CREAM, w=3.5):
    """Stickman face inside a head circle of radius r centred at c.

    Design 02 (neon-on-black): features default to the ice-white neon stroke
    so they read on the black canvas; pass INK only over bright fills.

    brow: None | 'up' | 'flat' | 'angry' | 'sad'
    mouth: None | 'smile' | 'frown' | 'o' | 'flat' | 'grimace'
    look: -1..1 gaze offset (x, y) in head-radius fractions.
    """
    ex = 0.36 * r
    ey = -0.06 * r
    er = max(1.6, 0.1 * r)
    for sx in (-1, 1):
        ecx, ecy = c[0] + sx * ex, c[1] + ey
        if closed:
            ctx.line([(ecx - 0.14 * r, ecy), (ecx + 0.14 * r, ecy)], fill=color, w=w)
        else:
            ctx.dot((ecx + look[0] * 0.07 * r, ecy + look[1] * 0.07 * r),
                    er * 2, fill=color)
    if brow:
        by = c[1] - 0.34 * r
        for sx in (-1, 1):
            bx = c[0] + sx * ex
            if brow == "up":          # raised, worried
                ctx.line([(bx - 0.16 * r, by - 0.1 * r), (bx + 0.16 * r, by - 0.12 * r)],
                         fill=color, w=w)
            elif brow == "flat":
                ctx.line([(bx - 0.16 * r, by), (bx + 0.16 * r, by)], fill=color, w=w)
            elif brow == "angry":     # inner ends point down toward the nose
                ctx.line([(bx - 0.16 * r, by + 0.09 * r * sx),
                          (bx + 0.16 * r, by - 0.09 * r * sx)], fill=color, w=w)
            elif brow == "sad":       # inner ends lift up
                ctx.line([(bx - 0.16 * r, by - 0.09 * r * sx),
                          (bx + 0.16 * r, by + 0.09 * r * sx)], fill=color, w=w)
    if mouth:
        mw = 0.34 * r
        my = c[1] + 0.36 * r
        if mouth == "smile":
            ctx.arc([c[0] - mw, my - 0.18 * r, c[0] + mw, my + 0.18 * r], 20, 160,
                    fill=color, w=w)
        elif mouth == "frown":
            ctx.arc([c[0] - mw, my - 0.14 * r, c[0] + mw, my + 0.22 * r], 200, 340,
                    fill=color, w=w)
        elif mouth == "o":
            ctx.circle((c[0], my), 0.13 * r, outline=color, w=w)
        elif mouth == "flat":
            ctx.line([(c[0] - mw * 0.6, my), (c[0] + mw * 0.6, my)], fill=color, w=w)
        elif mouth == "grimace":
            ctx.line([(c[0] - mw, my), (c[0] + mw, my)], fill=color, w=w)
            for k in range(4):
                x0 = c[0] - mw + k * (2 * mw / 4)
                ctx.line([(x0, my), (x0, my + 0.12 * r)], fill=color, w=w * 0.7)


def sweat(ctx, c, size, color=(150, 210, 255)):
    """Sweat drop above-left of a head."""
    ctx.poly([(c[0], c[1] - size), (c[0] + size * 0.55, c[1] + size * 0.35),
              (c[0], c[1] + size * 0.6), (c[0] - size * 0.55, c[1] + size * 0.35)],
             fill=color)
    ctx.circle((c[0], c[1] + size * 0.3), size * 0.5, fill=color)


def sparkle(ctx, c, r, color=(255, 230, 150)):
    k = r * 0.24
    ctx.poly([(c[0], c[1] - r), (c[0] + k, c[1] - k), (c[0] + r, c[1]),
              (c[0] + k, c[1] + k), (c[0], c[1] + r), (c[0] - k, c[1] + k),
              (c[0] - r, c[1]), (c[0] - k, c[1] - k)], fill=color)
