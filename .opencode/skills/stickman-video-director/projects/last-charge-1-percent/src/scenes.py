"""The six scenes of the "last-charge-1-percent" episode.

Topic: one urgent message left, battery stuck at 1 %, racing a screen that is
already dimming.
Style: Cinematic neon — sharp black silhouettes edged with bold cyan, magenta
and amber rim light, wet-night street, dark hallway, puddle reflections and a
final outlet reach. Camera pushes, pans and shakes per beat.

Obstacle flow:
    hook_1pct       the hook — 1 % and one message that has to go out
    street_glare    obstacle 1 — neon streetlamp + convenience-store glare
    hallway_creak   obstacle 2 — dark hallway, creaking doorway, house corner
    puddle_neon     obstacle 3 — a puddle throws the neon sign back at you
    outlet_run      the charge — three steps to the outlet, charger on floor
    outlet_reach    dive, plug, 1 % comes back, message sent

Every visual beat is keyed to a caption chunk via beat(line, chunk), so the
picture lands on the spoken words even if the narration runs long or short.
"""
import math

from PIL import Image

from stick import Ctx, walk_pose
from common import (AMBER, BUILDING, CHARGER, CHALK, CREAM, CYAN, DOOR_WOOD,
                    GLARE, HALL_DARK, HALL_WALL, INK, MAGENTA, NEON_AMBER,
                    NEON_CYAN, NEON_MAGENTA, NEON_RED, OUTLET_METAL,
                    PUD_GLASS, ROAD, ROAD_WET, SCREEN_OFF, SCREEN_ON,
                    SIDEWALK, STORE_GLOW, SS, W, H, W2, H2, clamp, dim,
                    ease_in, ease_in_out, ease_out, ease_out_back, font,
                    lerp, mix, pulse, ramp, smoothstep)

# ------------------------------------------------------------------ poses
# Local units: feet / anchor at (0, 0), y negative = up. Poses face right.

POSE_PHONE = {                    # standing, both hands on the phone
    "head": (0, -88, 12),
    "spine": [(0, -76), (0, -44)],
    "armL": [(0, -72), (16, -64), (28, -58)],
    "armR": [(0, -72), (20, -68), (30, -60)],
    "legL": [(0, -44), (-12, -22), (-14, 0)],
    "legR": [(0, -44), (12, -22), (15, 0)],
}

POSE_PHONE_UP = {                 # phone held higher, urgent glance
    "head": (2, -90, 12),
    "spine": [(0, -76), (0, -44)],
    "armL": [(0, -72), (18, -70), (30, -66)],
    "armR": [(0, -72), (24, -76), (34, -72)],
    "legL": [(0, -44), (-14, -22), (-16, 0)],
    "legR": [(0, -44), (14, -22), (17, 0)],
}

POSE_SNEAK = {                    # crouched, slipping past a doorway
    "head": (6, -76, 12),
    "spine": [(2, -64), (-2, -36)],
    "armL": [(2, -62), (-6, -56), (-18, -52)],
    "armR": [(2, -62), (20, -58), (34, -56)],
    "legL": [(-2, -36), (-22, -22), (-34, 0)],
    "legR": [(-2, -36), (20, -20), (26, 0)],
}

POSE_GRAB = {                     # reaching up for the phone / charger
    "head": (0, -88, 12),
    "spine": [(0, -76), (0, -44)],
    "armL": [(0, -72), (-14, -60), (-24, -48)],
    "armR": [(0, -72), (26, -78), (46, -86)],
    "legL": [(0, -44), (-14, -22), (-17, 0)],
    "legR": [(0, -44), (16, -22), (20, 0)],
}

POSE_DIVE = {                     # horizontal dive, head + arms to the right
    "head": (76, -44, 12),
    "spine": [(58, -38), (12, -22)],
    "armR": [(58, -38), (78, -54), (98, -58)],
    "armL": [(58, -38), (76, -30), (96, -28)],
    "legL": [(12, -22), (-24, -30), (-54, -26)],
    "legR": [(12, -22), (-26, -14), (-56, -12)],
}

POSE_KNEEL = {                    # kneeling, arm out to the outlet
    "head": (8, -70, 12),
    "spine": [(4, -58), (0, -30)],
    "armL": [(4, -56), (14, -46), (26, -42)],
    "armR": [(4, -56), (26, -52), (48, -54)],
    "legL": [(0, -30), (-8, -8), (-20, 0)],
    "legR": [(0, -30), (26, -20), (34, 0)],
}

POSE_DONE = {                     # kneeling back, arm raised in success
    "head": (4, -72, 12),
    "spine": [(2, -60), (0, -30)],
    "armL": [(2, -58), (18, -50), (30, -46)],
    "armR": [(2, -58), (22, -74), (34, -90)],
    "legL": [(0, -30), (-8, -8), (-20, 0)],
    "legR": [(0, -30), (26, -20), (34, 0)],
}


def walk_phone(p):
    """Walk cycle with the phone held out in front."""
    pose = walk_pose(p)
    pose["armR"] = [(0, -72), (22, -76), (32, -66)]
    return pose


# ------------------------------------------------------------------ helpers

def gradient(w, h, top, bottom):
    img = Image.new("RGB", (w, h))
    px = img.load()
    tr, tg, tb = top
    br, bg, bb = bottom
    for y in range(h):
        p = y / max(1, h - 1)
        r = int(tr + (br - tr) * p)
        g = int(tg + (bg - tg) * p)
        b = int(tb + (bb - tb) * p)
        for x in range(w):
            px[x, y] = (r, g, b)
    return img


def make_bg(top, bottom):
    """Full-bleed supersampled night gradient."""
    return gradient(W, H, top, bottom).resize((W2, H2), Image.BILINEAR)


def blend_pose(a, b, t):
    t = clamp(t)
    res = {}
    for k in a:
        if k == "head":
            hx = a["head"][0] + (b["head"][0] - a["head"][0]) * t
            hy = a["head"][1] + (b["head"][1] - a["head"][1]) * t
            hr = a["head"][2] + (b["head"][2] - a["head"][2]) * t
            res["head"] = (hx, hy, hr)
        elif isinstance(a[k], list):
            pts = []
            for i in range(len(a[k])):
                p0 = a[k][i]
                p1 = b[k][i] if i < len(b[k]) else p0
                pts.append((p0[0] + (p1[0] - p0[0]) * t,
                            p0[1] + (p1[1] - p0[1]) * t))
            res[k] = pts
    return res


def sketchy(pts, jit=3.0, seed=0.0):
    out = []
    for i, (x, y) in enumerate(pts):
        out.append((x + jit * math.sin(seed + i * 2.3 + x * 0.1),
                    y + jit * math.cos(seed + i * 1.7 + y * 0.1)))
    return out


def nline(ctx, pts, color, w=6, a=255, halo=3.2, jit=3.0, seed=0.0):
    sp = sketchy(pts, jit=jit, seed=seed) if jit else pts
    if halo > 0:
        ctx.line(sp, fill=(0, 0, 0, int(a * 0.8)), w=w + int(halo * 2))
    ctx.line(sp, fill=tuple(color[:3]) + (a,), w=w)


def ncircle(ctx, c, r, color, w=6, a=255, fill=None, halo=3.2):
    if fill is not None:
        f = tuple(fill[:3]) + (int(fill[3] * (a / 255.0)) if len(fill) > 3 else a,)
        ctx.circle(c, r, fill=f)
    if halo > 0:
        ctx.circle(c, r, outline=(0, 0, 0, int(a * 0.8)), w=w + int(halo * 2))
    ctx.circle(c, r, outline=tuple(color[:3]) + (a,), w=w)


def nrrect(ctx, box, r, color, w=6, a=255, fill=None, halo=3.2):
    if fill is not None:
        f = tuple(fill[:3]) + (int(fill[3] * (a / 255.0)) if len(fill) > 3 else a,)
        ctx.rrect(box, r, fill=f)
    if halo > 0:
        ctx.rrect(box, r, outline=(0, 0, 0, int(a * 0.8)), w=w + int(halo * 2))
    ctx.rrect(box, r, outline=tuple(color[:3]) + (a,), w=w)


def ntext(ctx, xy, s, size=30, color=CREAM, a=255, anchor="mm", bold=True,
          halo=2.0):
    x, y = xy
    if halo > 0:
        for dx, dy in ((-halo, 0), (halo, 0), (0, -halo), (0, halo),
                       (-halo, -halo), (halo, halo), (-halo, halo), (halo, -halo)):
            ctx.text((x + dx, y + dy), s, size=size, bold=bold,
                     fill=(0, 0, 0, int(a * 0.9)), anchor=anchor)
    ctx.text(xy, s, size=size, bold=bold, fill=tuple(color[:3]) + (a,),
             anchor=anchor)


def motion_lines(ctx, cx, cy, ang, n=5, r0=30, r1=110, color=NEON_RED,
                 a=255, w=5):
    for i in range(n):
        rad = math.radians(ang + (i - n / 2.0) * 13.0)
        nline(ctx, [(cx + r0 * math.cos(rad), cy + r0 * math.sin(rad)),
                    (cx + r1 * math.cos(rad), cy + r1 * math.sin(rad))],
              color, w=w, a=a, halo=2.0, jit=0)


# ------------------------------------------------------------- neon silhouette

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


def silhouette(ctx, x, y, s, pose, rim=NEON_CYAN, rim2=NEON_AMBER,
               body=(5, 7, 14), w=8, flip=False, rot=0.0,
               off_a=(-8, -7), off_b=(7, 5), face=True, mouth="flat"):
    """Sharp dark silhouette with bold neon rim light on both edges.

    Two offset passes (cyan / magenta / amber) are drawn first, then the
    black body pass on top, so only a crescent of rim survives — the
    cinematic silhouette look.
    """
    passes = []
    if rim:
        passes.append((off_a, rim))
    if rim2:
        passes.append((off_b, rim2))
    for off, col in passes:
        T = _xf(pose, x, y, s, flip, rot, off)
        for key in ("spine", "armL", "armR", "legL", "legR"):
            if key in pose:
                ctx.line([T(p) for p in pose[key]], fill=tuple(col) + (255,), w=w)
        hx, hy, hr = pose["head"]
        ctx.circle(T((hx, hy)), hr * s, fill=tuple(col) + (255,))

    T = _xf(pose, x, y, s, flip, rot, (0.0, 0.0))
    for key in ("spine", "armL", "armR", "legL", "legR"):
        if key in pose:
            ctx.line([T(p) for p in pose[key]], fill=tuple(body) + (255,), w=w)
    hx, hy, hr = pose["head"]
    ctx.circle(T((hx, hy)), hr * s, fill=tuple(body) + (255,))

    if face:
        c = T((hx, hy))
        r = hr * s
        col = rim or CREAM
        for sx in (-1, 1):
            ctx.line([(c[0] + sx * 0.34 * r, c[1] - 0.2 * r),
                      (c[0] + sx * 0.34 * r, c[1] + 0.02 * r)],
                     fill=tuple(col) + (255,), w=max(2, int(w * 0.5)))
        mw = 0.3 * r
        my = c[1] + 0.42 * r
        if mouth == "o":
            ctx.circle((c[0], my), 0.15 * r, outline=tuple(col) + (255,), w=max(2, int(w * 0.5)))
        elif mouth == "grimace":
            ctx.line([(c[0] - mw, my), (c[0] + mw, my)],
                     fill=tuple(col) + (255,), w=max(2, int(w * 0.5)))
        else:
            ctx.line([(c[0] - mw, my), (c[0] + mw * 0.6, my)],
                     fill=tuple(col) + (255,), w=max(2, int(w * 0.5)))
    return T


# ------------------------------------------------------------------ devices

def phone_prop(ctx, box, level=1.0, rim=NEON_CYAN, body=(9, 13, 24),
               screen_text=None, text_color=None):
    """Phone with a screen whose brightness is level 0..1."""
    x0, y0, x1, y1 = box
    ctx.rrect(box, 10, fill=tuple(body) + (255,), outline=tuple(rim) + (255,), w=5)
    sx0, sy0, sx1, sy1 = x0 + 9, y0 + 9, x1 - 9, y1 - 9
    on = mix(SCREEN_OFF, SCREEN_ON, clamp(level))
    ctx.rrect([sx0, sy0, sx1, sy1], 5, fill=tuple(on) + (255,))
    if screen_text:
        ntext(ctx, ((sx0 + sx1) / 2, (sy0 + sy1) / 2), screen_text,
              size=int(min(34, (sx1 - sx0) / 7)),
              color=tuple(text_color) if text_color else INK,
              a=int(255 * clamp(level * 1.2)))
    return (sx0, sy0, sx1, sy1)


def battery_badge(ctx, x, y, w, h, pct=0.01, color=NEON_RED, label="1%",
                  on=True):
    col = color if on else dim(color, 0.5)
    ctx.rrect([x, y, x + w, y + h], 6, fill=(4, 6, 14, 235),
               outline=tuple(col) + (255,), w=3)
    ctx.rrect([x + w + 4, y + h * 0.3, x + w + 9, y + h * 0.7], 2,
              fill=tuple(col) + (255,))
    fw = max(7, (w - 10) * clamp(pct, 0.0, 1.0))
    ctx.rrect([x + 5, y + 5, x + 5 + fw, y + h - 5], 3, fill=tuple(col) + (255,))
    ntext(ctx, (x - 12, y + h / 2), label, size=int(h * 0.8), color=col,
          anchor="rm")


def battery_hud(ctx, t, color=NEON_RED, flash=True, at=(58, 44),
                pct=0.01, label="1%"):
    """Persistent low-battery readout, top-left, blinking alarm colour."""
    x, y = at
    bw, bh = 116, 46
    on = (not flash) or (int(t * 5) % 2 == 0)
    col = color if on else dim(color, 0.45)
    if on:
        ctx.glow((x + bw / 2, y + bh / 2), bw * 0.85, col, alpha=42)
    ctx.rrect([x, y, x + bw, y + bh], 10, fill=(3, 5, 12, 228),
               outline=tuple(col) + (255,), w=4)
    ctx.rrect([x + bw + 6, y + bh * 0.3, x + bw + 13, y + bh * 0.7], 3,
              fill=tuple(col) + (255,))
    fw = max(9, (bw - 16) * clamp(pct, 0.0, 1.0))
    ctx.rrect([x + 8, y + 8, x + 8 + fw, y + bh - 8], 4,
              fill=tuple(col) + (255,))
    ntext(ctx, (x + bw / 2, y + bh + 27), label, size=26, color=col, a=255)


# ------------------------------------------------------------------ scenes

class Scene:
    id = "base"
    zoom_range = (1.02, 1.05)

    def __init__(self, tl, script):
        self.tl = tl
        self.script = script
        self.t0 = 0.0
        self.t1 = tl["duration"]
        self.bg = None
        self.build()

    def L(self, i):
        return self.tl["lines"][i]

    def beat(self, i, j=0):
        return self.tl["lines"][i]["caps"][j]["start"] - self.t0

    def line_start(self, i):
        return self.tl["lines"][i]["start"]

    def line_end(self, i):
        return self.tl["lines"][i]["end"] - self.t0

    def span(self):
        return max(0.5, self.t1 - self.t0)

    def build(self):
        pass

    def draw(self, ctx, lt):
        pass

    def shake(self, lt):
        return (0.0, 0.0)

    def zoom(self, lt):
        p = clamp(lt / self.span())
        a, b = self.zoom_range
        return lerp(a, b, p)


# --------------------------------------------------------- 1 · the hook: 1 %

class HookOnePercent(Scene):
    id = "hook_1pct"
    zoom_range = (1.0, 1.06)

    def build(self):
        self.bg = make_bg((9, 11, 26), (2, 3, 8))
        ctx = Ctx(self.bg)
        ctx.glow((1180, 660), 320, NEON_MAGENTA, alpha=52)   # off-frame sign
        ctx.glow((90, 150), 300, NEON_CYAN, alpha=30)        # off-frame neon
        # wall panels behind
        for i in range(4):
            ctx.rrect([-40 + i * 340, 120, 260 + i * 340, 470], 8,
                      fill=(7, 9, 20, 255), outline=(14, 18, 34, 255), w=3)

    def draw(self, ctx, lt):
        t = lt
        b1 = self.beat(0, 1)
        b2 = self.beat(0, 2)

        # hero, silhouette rimmed cyan + magenta, staring at the phone
        silhouette(ctx, 330, 700, 3.4, POSE_PHONE_UP, rim=NEON_CYAN,
                   rim2=NEON_MAGENTA, w=9, mouth="grimace")
        hand = phone_prop(ctx, [418, 452, 522, 596], level=0.85,
                          rim=NEON_CYAN)
        ctx.glow(((hand[0] + hand[2]) / 2, (hand[1] + hand[3]) / 2), 96,
                 NEON_CYAN, alpha=60)

        # ---- the big close-up phone: the hook prop
        box = [740, 90, 1170, 640]
        level = 1.0 - 0.82 * clamp(ramp(t, b2, b2 + 1.6))
        sx0, sy0, sx1, sy1 = phone_prop(ctx, box, level=level, rim=NEON_CYAN,
                                        body=(8, 11, 22))
        # top status bar: battery + clock
        battery_badge(ctx, sx1 - 108, sy0 + 14, 74, 34, pct=0.01,
                      color=NEON_RED, label="1%",
                      on=int(t * 5) % 2 == 0)
        ntext(ctx, (sx0 + 20, sy0 + 31), "11:58 PM", size=22, color=INK,
              a=int(255 * level), anchor="lm")

        # message draft panel
        panel = [sx0 + 18, sy0 + 76, sx1 - 18, sy0 + 340]
        ctx.rrect(panel, 12, fill=(6, 10, 20, int(235 * level)),
                  outline=NEON_CYAN + (int(160 * level),), w=3)
        ntext(ctx, (panel[0] + 20, panel[1] + 30), "TO: EVERYONE",
              size=22, color=CHALK, a=int(255 * level), anchor="lm")
        ctx.line([(panel[0] + 16, panel[1] + 54), (panel[2] - 16, panel[1] + 54)],
                 fill=NEON_CYAN + (int(120 * level),), w=2)
        msg = "I'M ON MY WAY —"
        n_chars = int(clamp(ramp(t, b1, b1 + 1.4)) * len(msg))
        if n_chars:
            ntext(ctx, (panel[0] + 20, panel[1] + 100), msg[:n_chars],
                  size=32, color=SCREEN_ON, a=int(255 * level), anchor="lm")
        if int(t * 2.4) % 2 == 0 and level > 0.35:
            ntext(ctx, (panel[0] + 24 + n_chars * 17, panel[1] + 100), "|",
                  size=32, color=SCREEN_ON, a=int(255 * level), anchor="lm")

        # send button (dies with the dimming)
        btn = [sx1 - 250, sy0 + 380, sx1 - 24, sy0 + 448]
        nrrect(ctx, btn, 12, NEON_CYAN, w=4,
               fill=(0, 90, 120, int(255 * level)), halo=2.0)
        ntext(ctx, ((btn[0] + btn[2]) / 2, (btn[1] + btn[3]) / 2), "SEND",
              size=30, color=CREAM if level > 0.5 else (60, 80, 96),
              a=255 if level > 0.35 else 140)

        # dimming scanlines + falling brightness caption
        if level < 0.995:
            a = int(150 * (1.0 - level))
            for yy in range(int(sy0), int(sy1), 16):
                ctx.line([(sx0, yy), (sx1, yy)], fill=(0, 0, 0, a // 2), w=6)
            ntext(ctx, ((sx0 + sx1) / 2, sy1 - 46), "DIMMING", size=26,
                  color=NEON_RED, a=int(220 * (1 - level)))

        battery_hud(ctx, t, color=NEON_RED, flash=True)

    def shake(self, lt):
        # tiny hand tremble under the urgency
        return (1.6 * math.sin(lt * 9.0), 1.4 * math.cos(lt * 7.3))


# ------------------------------------------- 2 · obstacle: streetlamp + glare

class StreetGlare(Scene):
    id = "street_glare"
    zoom_range = (1.03, 1.11)

    def build(self):
        self.bg = make_bg((10, 12, 30), (3, 4, 10))
        ctx = Ctx(self.bg)
        ctx.glow((640, 120), 420, NEON_MAGENTA, alpha=44)

        # far building silhouettes with sparse amber windows
        skyline = [(0, 210, 150), (140, 150, 300), (280, 190, 240),
                   (460, 170, 340), (620, 240, 210), (850, 200, 320),
                   (1040, 240, 260)]
        for i, (bx, bw, bh) in enumerate(skyline):
            ctx.poly([(bx, 560), (bx + bw, 560), (bx + bw, 560 - bh),
                      (bx, 560 - bh)], fill=BUILDING + (255,))
            for wy in range(3):
                for wx in range(2):
                    if (i + wx + wy) % 3 == 0:
                        ctx.rrect([bx + 26 + wx * 62, 560 - bh + 40 + wy * 74,
                                   bx + 52 + wx * 62, 560 - bh + 70 + wy * 74],
                                  2, fill=(255, 196, 96, 190))

        # convenience store: magenta sign + warm window glare
        ctx.rrect([830, 296, 1210, 600], 6, fill=(7, 9, 18, 255),
                  outline=INK + (255,), w=5)
        for k in range(3):
            ctx.rrect([856 + k * 116, 336, 956 + k * 116, 540], 4,
                      fill=STORE_GLOW + (215,))
            ctx.glow((906 + k * 116, 440), 96, NEON_AMBER, alpha=44)
        ctx.rrect([830, 232, 1210, 292], 6, fill=(18, 6, 24, 255),
                  outline=NEON_MAGENTA + (255,), w=4)
        ctx.glow((1020, 262), 150, NEON_MAGENTA, alpha=64)
        ntext(ctx, (1020, 262), "NEON MART", size=34, color=NEON_MAGENTA)
        ctx.line([(846, 276), (1194, 276)], fill=(255, 255, 255, 120), w=2)

        # sidewalk + wet road
        ctx.poly([(0, 560), (W, 560), (W, 646), (0, 646)],
                 fill=SIDEWALK + (255,))
        ctx.line([(0, 560), (W, 560)], fill=INK + (255,), w=5)
        ctx.poly([(0, 646), (W, 646), (W, H), (0, H)], fill=ROAD + (255,))
        for k in range(9):
            ctx.rrect([40 + k * 150, 668, 150 + k * 150, 684], 8,
                      fill=ROAD_WET + (170,))

        # neon streetlamp — obstacle 1
        ctx.line([(430, 600), (430, 196)], fill=(70, 84, 110, 255), w=10)
        ctx.rrect([378, 160, 482, 208], 8, fill=(18, 22, 38, 255),
                  outline=NEON_AMBER + (255,), w=4)
        ctx.glow((430, 200), 190, NEON_AMBER, alpha=110)
        ctx.circle((430, 196), 22, fill=GLARE + (255,))
        ctx.poly([(384, 206), (476, 206), (650, 646), (206, 646)],
                 fill=NEON_AMBER + (58,))

    def draw(self, ctx, lt):
        t = lt
        p = clamp(lt / self.span())
        b0 = self.beat(1, 0)
        b1 = self.beat(1, 1)
        b2 = self.beat(1, 2)

        x = 250 + 260 * ease_out(p)
        pose = walk_phone((t * 0.95) % 1.0)
        T = silhouette(ctx, x, 646, 3.0, pose, rim=NEON_CYAN,
                       rim2=NEON_AMBER, w=8, mouth="flat")
        hx, hy = T((32, -66))                    # hand holding the phone
        phone = phone_prop(ctx, [hx - 34, hy - 46, hx + 34, hy + 46],
                           level=0.9, rim=NEON_CYAN)
        ctx.glow(((phone[0] + phone[2]) / 2, (phone[1] + phone[3]) / 2), 74,
                 NEON_CYAN, alpha=70)

        # lamp glare wedge striking the glass (obstacle 1)
        if t >= b0:
            gl = 0.55 + 0.45 * pulse(t, 3.0)
            ctx.poly([(404, 204), (462, 204), (phone[2] + 26, phone[1] - 18),
                      (phone[0] - 18, phone[3] + 12)],
                     fill=GLARE + (int(120 * gl),))
            ctx.poly([(416, 204), (450, 204), (phone[2], phone[1]),
                      (phone[0], phone[3])],
                     fill=(255, 255, 255, int(160 * gl)))
            ntext(ctx, ((430 + phone[0]) / 2, 300), "GLARE", size=24,
                  color=NEON_AMBER, a=int(150 * gl))

        # the screen blows out to white (chunk 3 of line 1)
        if t >= b2:
            w = clamp(ramp(t, b2, b2 + 0.5))
            ctx.rrect([phone[0], phone[1], phone[2], phone[3]], 5,
                      fill=GLARE + (int(255 * w),))
            ctx.glow(((phone[0] + phone[2]) / 2, (phone[1] + phone[3]) / 2),
                     110 * w + 40, GLARE, alpha=int(120 * w))

        # neon sign flicker + store-window pulse
        if int(t * 11) % 7 == 0:
            ctx.glow((1020, 262), 170, NEON_MAGENTA, alpha=80)

        battery_hud(ctx, t, color=NEON_RED, flash=True)

    def shake(self, lt):
        # slow lateral track with the walk
        return (-26 * clamp(lt / self.span()), 1.5 * math.sin(lt * 6.0))


# ------------------------------ 3 · obstacle: dark hallway / creaking corner

class HallwayCreak(Scene):
    id = "hallway_creak"
    zoom_range = (1.04, 1.13)

    def build(self):
        self.bg = make_bg((8, 9, 20), (3, 4, 10))
        ctx = Ctx(self.bg)
        # one-point corridor
        fx0, fx1, fy0, fy1 = 560, 860, 120, 600
        ctx.poly([(0, 0), (W, 0), (fx1, fy0), (fx0, fy0)], fill=(9, 10, 22, 255))
        ctx.poly([(0, H), (W, H), (fx1, fy1), (fx0, fy1)], fill=(14, 12, 26, 255))
        ctx.poly([(0, 0), (fx0, fy0), (fx0, fy1), (0, H)],
                 fill=HALL_WALL + (255,))
        ctx.poly([(W, 0), (fx1, fy0), (fx1, fy1), (W, H)],
                 fill=mix(HALL_WALL, HALL_DARK, 0.55) + (255,))
        ctx.poly([(fx0, fy0), (fx1, fy0), (fx1, fy1), (fx0, fy1)],
                 fill=HALL_DARK + (255,))
        # far doorway: the way out, cyan rim
        ctx.rrect([648, 226, 772, fy1], 4, fill=(4, 5, 12, 255),
                  outline=NEON_CYAN + (255,), w=5)
        ctx.glow((710, 430), 150, NEON_CYAN, alpha=54)
        # wall trim + floor boards
        for k in range(6):
            ctx.line([(0, 90 + k * 100), (fx0, fy0 + k * 80)],
                     fill=(18, 20, 38, 255), w=3)
        for k in range(5):
            ctx.line([(fx0 + 20 + k * 60, fy1), (200 + k * 240, H)],
                     fill=(22, 18, 34, 255), w=4)
        # the creaking door on the right wall (house corner)
        ctx.poly([(900, 150), (1246, 66), (1250, 662), (904, 604)],
                 fill=(6, 7, 16, 255), outline=INK + (255,), w=6)

    def draw(self, ctx, lt):
        t = lt
        p = clamp(lt / self.span())
        b1 = self.beat(2, 1)          # "The door creaks open"
        creak = clamp(ramp(t, b1, b1 + 1.1))
        open_p = ease_out(clamp(ramp(t, b1, b1 + 1.6)))

        # amber light escaping the opening door
        if open_p > 0.01:
            gap = 190 * open_p
            ctx.poly([(904, 152), (904 + gap, 168), (904 + gap, 596), (906, 602)],
                     fill=NEON_AMBER + (int(210 * open_p),))
            ctx.poly([(904, 602), (904 + gap, 596), (760, H), (520, H)],
                     fill=NEON_AMBER + (int(90 * open_p),))
            ctx.glow((904 + gap / 2, 380), 150 * open_p, NEON_AMBER,
                     alpha=int(90 * open_p))
            # door panel rotating inward
            ctx.poly([(904 + gap, 152), (1246, 66), (1250, 662),
                      (904 + gap, 596)], fill=DOOR_WOOD + (255,),
                     outline=INK + (255,), w=5)
            ctx.circle((904 + gap + 42, 380), 9, fill=NEON_AMBER + (255,))

        # creak: magenta shock arcs + sound text at the corner
        if creak > 0.01 and creak < 1.0:
            for k in range(3):
                rr = 40 + k * 34 + 40 * creak
                ctx.arc([940 - rr, 330 - rr, 940 + rr, 330 + rr], 200, 340,
                        fill=NEON_MAGENTA + (int(200 * (1 - creak)),), w=5)
            ntext(ctx, (946, 268), "creeeak", size=30, color=NEON_MAGENTA,
                  a=int(255 * (1 - creak * 0.5)))

        # hero slipping past the corner, crouched
        x = 300 + 210 * ease_out(p)
        pose = POSE_SNEAK if t < b1 else blend_pose(POSE_SNEAK, POSE_PHONE,
                                                    0.35 + 0.4 * open_p)
        silhouette(ctx, x, 686, 2.9, pose, rim=NEON_AMBER, rim2=NEON_CYAN,
                   w=8, mouth="o")
        hx = x + 34 * 2.9
        phone = phone_prop(ctx, [hx - 26, 686 - 58 * 2.9, hx + 30,
                                 686 - 40 * 2.9], level=0.7, rim=NEON_CYAN)
        ctx.glow(((phone[0] + phone[2]) / 2, (phone[1] + phone[3]) / 2), 66,
                 NEON_CYAN, alpha=56)

        battery_hud(ctx, t, color=NEON_RED, flash=True)

    def shake(self, lt):
        b1 = self.beat(2, 1)
        k = max(0.0, 1.0 - abs(lt - b1) / 1.2)
        a = 7.0 * k * k
        return (a * math.sin(lt * 46), a * math.cos(lt * 39))


# -------------------------------- 4 · obstacle: puddle + neon sign reflection

class PuddleNeon(Scene):
    id = "puddle_neon"
    zoom_range = (1.02, 1.12)

    def build(self):
        self.bg = make_bg((7, 9, 22), (2, 3, 8))
        ctx = Ctx(self.bg)
        # shopfront block
        ctx.poly([(0, 0), (W, 0), (W, 430), (0, 430)], fill=(9, 11, 24, 255))
        ctx.rrect([300, 40, 700, 380], 6, fill=(6, 8, 18, 255),
                  outline=(16, 20, 38, 255), w=4)
        # the neon sign that keeps catching you
        ctx.rrect([92, 56, 236, 404], 8, fill=(16, 6, 22, 255),
                  outline=NEON_MAGENTA + (255,), w=5)
        ctx.glow((164, 230), 200, NEON_MAGENTA, alpha=76)
        for i, ch in enumerate("NEON"):
            ntext(ctx, (164, 108 + i * 78), ch, size=54,
                  color=NEON_MAGENTA if i % 2 == 0 else NEON_CYAN)
        # sidewalk / road
        ctx.poly([(0, 430), (W, 430), (W, 520), (0, 520)],
                 fill=SIDEWALK + (255,))
        ctx.line([(0, 430), (W, 430)], fill=INK + (255,), w=5)
        ctx.poly([(0, 520), (W, 520), (W, H), (0, H)], fill=ROAD + (255,))
        for k in range(8):
            ctx.rrect([20 + k * 170, 690, 150 + k * 170, 706], 8,
                      fill=ROAD_WET + (150,))
        # the puddle
        ctx.glow((770, 640), 300, NEON_MAGENTA, alpha=44)
        ctx.ellipse([430, 578, 1110, 702], fill=PUD_GLASS + (255,),
                    outline=NEON_MAGENTA + (170,), w=4)

    def draw(self, ctx, lt):
        t = lt
        p = clamp(lt / self.span())
        b0 = self.beat(4, 0)      # "A puddle throws the neon sign..."
        b1 = self.beat(4, 1)
        c0 = self.beat(5, 0)      # "You snatch the phone up."
        c1 = self.beat(5, 1)      # "The battery icon turns red."

        # mirrored sign inside the puddle, wobbling; worse after the splash
        hit = clamp(ramp(t, b1, b1 + 1.4))
        wob = 6 + 26 * hit
        for i, ch in enumerate("NEON"):
            yy = 604 + i * 24
            dx = wob * math.sin(t * 5.0 + i * 1.1)
            ntext(ctx, (164 + dx * 2.6, yy), ch, size=30,
                  color=NEON_MAGENTA if i % 2 == 0 else NEON_CYAN,
                  a=int(150 - 60 * hit))
        ctx.poly([(60, 600), (270, 600), (330, 690), (40, 690)],
                 fill=NEON_MAGENTA + (int(70 - 30 * hit),))

        # hero walking, then snatching the phone back
        x = 250 + 300 * ease_out(clamp(ramp(t, 0.0, c0)))
        if t >= c0:
            pose = blend_pose(walk_phone(0.25), POSE_PHONE_UP,
                              ease_out(clamp(ramp(t, c0, c0 + 0.45))))
        else:
            pose = walk_phone((t * 0.95) % 1.0)
        T = silhouette(ctx, x, 560, 3.0, pose, rim=NEON_CYAN,
                       rim2=NEON_MAGENTA, w=8,
                       mouth="o" if t >= c1 else "flat")
        hx, hy = T((32, -66))
        # phone dips low over the puddle while the reflection breaks up
        dip = 60 * clamp(ramp(t, b0, b1))
        phone = phone_prop(ctx, [hx - 34, hy - 46 + dip, hx + 34,
                                 hy + 46 + dip], level=0.85, rim=NEON_CYAN)
        ctx.glow(((phone[0] + phone[2]) / 2, (phone[1] + phone[3]) / 2), 78,
                 NEON_CYAN, alpha=64)

        # splash + ripple rings
        if b1 <= t < b1 + 1.8:
            k = clamp((t - b1) / 1.5)
            for i in range(3):
                kk = clamp(k * 1.4 - i * 0.18)
                if kk <= 0:
                    continue
                rx, ry = 700 + i * 40, 646
                ctx.ellipse([rx - 300 * kk, ry - 62 * kk,
                             rx + 300 * kk, ry + 62 * kk],
                            outline=NEON_MAGENTA + (int(220 * (1 - kk)),), w=5)
            for i in range(7):
                a = -1.4 + i * 0.3
                rr = 120 * k
                ddx = 700 + rr * math.cos(a)
                ddy = 646 + rr * math.sin(a) - 90 * k * (1 - k)
                ctx.circle((ddx, ddy), 6 + 3 * (1 - k),
                           fill=NEON_CYAN + (int(220 * (1 - k)),))

        # the battery turns red
        if t >= c1:
            hot = 0.6 + 0.4 * pulse(t, 4.0)
            battery_badge(ctx, hx + 30, hy - 150, 84, 40, pct=0.01,
                          color=NEON_RED, label="1%",
                          on=int(t * 6) % 2 == 0)
            ctx.glow((hx + 70, hy - 130), 110, NEON_RED, alpha=int(70 * hot))

        battery_hud(ctx, t, color=NEON_RED, flash=True)

    def shake(self, lt):
        b1 = self.beat(4, 1)
        k = max(0.0, 1.0 - abs(lt - b1) / 0.9)
        return (11.0 * k * math.sin(lt * 40), 8.0 * k * math.cos(lt * 33))


# -------------------------------------------- 5 · the charge: three steps out

class OutletRun(Scene):
    id = "outlet_run"
    zoom_range = (1.0, 1.14)

    def build(self):
        self.bg = make_bg((16, 12, 30), (4, 4, 12))
        ctx = Ctx(self.bg)
        ctx.poly([(0, 0), (W, 0), (W, 560), (0, 560)], fill=(17, 15, 32, 255))
        ctx.poly([(0, 560), (W, 560), (W, H), (0, H)], fill=(26, 20, 36, 255))
        ctx.line([(0, 560), (W, 560)], fill=NEON_AMBER + (150,), w=6)
        for k in range(6):
            ctx.line([(90 + k * 240, 560), (20 + k * 300, H)],
                     fill=(36, 27, 46, 255), w=5)

        # the goal: wall outlet, glowing amber
        ctx.glow((1128, 462), 190, NEON_AMBER, alpha=96)
        nrrect(ctx, [1064, 400, 1192, 524], 14, NEON_AMBER, w=6,
               fill=OUTLET_METAL + (255,))
        for sx in (1104, 1152):
            ctx.rrect([sx - 12, 434, sx + 12, 470], 4, fill=(6, 7, 14, 255))
        ctx.rrect([1114, 486, 1142, 506], 4, fill=(6, 7, 14, 255))

        # the charger you left on the floor, cable trailing to the wall
        ctx.rrect([930, 612, 1030, 678], 12, fill=CHARGER + (255,),
                  outline=NEON_AMBER + (255,), w=5)
        ctx.circle((1010, 645), 7, fill=NEON_MAGENTA + (255,))
        ctx.glow((1010, 645), 34, NEON_MAGENTA, alpha=90)
        nline(ctx, [(1030, 660), (1080, 600), (1140, 560), (1176, 526)],
              NEON_AMBER, w=8, a=210, jit=1.2)

        # three step markers on the floor
        for i, cx in enumerate((560, 760, 950)):
            ctx.poly([(cx - 34, 706), (cx, 676), (cx + 34, 706), (cx, 690)],
                     fill=(70, 40, 90, 255))

    def draw(self, ctx, lt):
        t = lt
        p = clamp(lt / self.span())
        b0 = self.beat(6, 0)

        # running hard, phone out front, rim lit amber by the outlet
        pose = walk_phone((t * 1.9) % 1.0)
        x = 300 + 470 * ease_in_out(p)
        T = silhouette(ctx, x, 690, 3.0, pose, rim=NEON_AMBER,
                       rim2=NEON_CYAN, w=8, mouth="grimace")
        hx, hy = T((32, -66))
        phone = phone_prop(ctx, [hx - 32, hy - 44, hx + 34, hy + 44],
                           level=0.55 - 0.3 * p, rim=NEON_CYAN)
        ctx.glow(((phone[0] + phone[2]) / 2, (phone[1] + phone[3]) / 2), 70,
                 NEON_CYAN, alpha=int(60 * (1 - p)))

        # step markers light up as he passes them
        for i, cx in enumerate((560, 760, 950)):
            lit = x > cx - 40
            col = NEON_CYAN if lit else (70, 40, 90)
            ctx.poly([(cx - 34, 706), (cx, 676), (cx + 34, 706), (cx, 690)],
                     fill=col + (255,))
            if lit:
                ctx.glow((cx, 692), 70, NEON_CYAN, alpha=70)
            ntext(ctx, (cx, 640), str(3 - i), size=30,
                  color=NEON_CYAN if lit else (90, 74, 118))

        # the outlet pulses harder as he closes in
        k = 0.5 + 0.5 * pulse(t * (1 + 2 * p), 2.0)
        ctx.glow((1128, 462), 200, NEON_AMBER, alpha=int(70 + 60 * k))
        if t >= b0:
            ntext(ctx, (1128, 350), "OUTLET", size=26, color=NEON_AMBER,
                  a=int(160 + 90 * pulse(t, 3.0)))

        # speed streaks behind him
        for i in range(5):
            yy = 470 + i * 44
            ctx.line([(x - 260 - i * 40, yy), (x - 120 - i * 30, yy)],
                     fill=NEON_CYAN + (110,), w=4)

        battery_hud(ctx, t, color=NEON_RED, flash=True)

    def shake(self, lt):
        return (4.0 * math.sin(lt * 30), 3.0 * math.cos(lt * 24))


# ------------------------------- 6 · the plug: 1 % comes back, message sent

class OutletReach(Scene):
    id = "outlet_reach"
    zoom_range = (1.14, 1.02)

    def build(self):
        self.bg = make_bg((18, 14, 34), (4, 4, 12))
        ctx = Ctx(self.bg)
        ctx.poly([(0, 0), (W, 0), (W, 540), (0, 540)], fill=(20, 17, 38, 255))
        ctx.poly([(0, 540), (W, 540), (W, H), (0, H)], fill=(28, 21, 38, 255))
        ctx.line([(0, 540), (W, 540)], fill=NEON_AMBER + (140,), w=6)
        for k in range(5):
            ctx.line([(140 + k * 300, 540), (40 + k * 360, H)],
                     fill=(38, 28, 48, 255), w=5)
        # big hero outlet
        ctx.glow((866, 402), 240, NEON_AMBER, alpha=110)
        nrrect(ctx, [760, 300, 972, 504], 20, NEON_AMBER, w=8,
               fill=OUTLET_METAL + (255,))
        for sx in (826, 906):
            ctx.rrect([sx - 16, 350, sx + 16, 404], 6, fill=(6, 7, 14, 255))
        ctx.rrect([846, 434, 886, 466], 6, fill=(6, 7, 14, 255))
        ntext(ctx, (866, 262), "OUTLET", size=26, color=NEON_AMBER)

    def draw(self, ctx, lt):
        t = lt
        p = clamp(lt / self.span())
        d0 = self.beat(7, 0)       # "You dive."
        d1 = self.beat(7, 1)       # "The screen dims to nothing"
        g0 = self.beat(8, 0)       # "Plug."
        g1 = self.beat(8, 1)       # "One percent comes back"
        g2 = self.beat(8, 2)       # "and the message sends"

        dive = ease_in(clamp(ramp(t, d0 - 0.3, d0 + 1.2)))
        plugged = t >= g0

        if not plugged:
            # ---- the dive, screen dying mid-air
            x = 260 + 300 * dive
            y = 560 + 60 * (1 - dive)
            silhouette(ctx, x, y, 3.1, POSE_DIVE, rim=NEON_CYAN,
                       rim2=NEON_MAGENTA, w=9, mouth="o")
            hx, hy = x + 98 * 3.1, y - 58 * 3.1
            lvl = 1.0 - clamp(ramp(t, d1, d1 + 1.1))
            phone = phone_prop(ctx, [hx - 40, hy - 56, hx + 40, hy + 40],
                               level=lvl * 0.9, rim=NEON_CYAN)
            if lvl > 0.05:
                ctx.glow(((phone[0] + phone[2]) / 2,
                          (phone[1] + phone[3]) / 2), 84 * lvl, NEON_CYAN,
                         alpha=int(70 * lvl))
            # trail
            for i in range(4):
                ctx.line([(x - 300 - i * 60, y - 60 + i * 34),
                          (x - 120 - i * 40, y - 30 + i * 30)],
                         fill=NEON_CYAN + (150 - i * 28,), w=6)
            motion_lines(ctx, x - 40, y - 60, 200, n=4, r0=60, r1=180,
                         color=NEON_MAGENTA, a=180, w=5)
            # the charger brick flying ahead of him
            ctx.rrect([640 + 150 * dive, 420, 730 + 150 * dive, 484], 12,
                      fill=CHARGER + (255,), outline=NEON_AMBER + (255,), w=5)
            nline(ctx, [(730 + 150 * dive, 470), (790 + 120 * dive, 440)],
                  NEON_AMBER, w=7, a=220, jit=2.0)
        else:
            # ---- plugged in: kneel, power handshake, then the send
            k = clamp((t - g0) / 0.8)
            silhouette(ctx, 560, 690, 3.0,
                       blend_pose(POSE_KNEEL, POSE_DONE,
                                  ease_out(clamp(ramp(t, g1 + 0.3, g2 + 0.6)))),
                       rim=NEON_CYAN, rim2=NEON_AMBER, w=9, mouth="o")
            # cable snapped into the socket
            nline(ctx, [(600, 640), (700, 560), (800, 500), (856, 448)],
                  NEON_AMBER, w=9, a=235, jit=1.5)
            ctx.rrect([826, 420, 906, 476], 10, fill=CHARGER + (255,),
                      outline=NEON_AMBER + (255,), w=5)
            # spark / handshake rings
            for i in range(3):
                kk = clamp((t - g0 - i * 0.16) / 0.9)
                if 0 < kk < 1:
                    rr = 40 + 260 * kk
                    ctx.circle((866, 402), rr,
                               outline=NEON_CYAN + (int(230 * (1 - kk)),), w=6)
            ctx.glow((866, 402), 240 * k, NEON_CYAN, alpha=int(120 * k))
            if t >= g1:
                ctx.glow((866, 402), 300, SCREEN_ON, alpha=90)

            # ---- the send banner
            if t >= g2:
                bp = ease_out_back(clamp(ramp(t, g2, g2 + 0.7)))
                y0 = -140 + 230 * bp
                nrrect(ctx, [300, y0, 980, y0 + 118], 18, NEON_CYAN, w=5,
                       fill=(6, 10, 20, 244))
                ntext(ctx, (640, y0 + 44), "MESSAGE SENT", size=40,
                      color=NEON_CYAN)
                ntext(ctx, (640, y0 + 90), "to: yourself  ·  battery 1%",
                      size=24, color=NEON_MAGENTA)

        # the HUD flips from alarm red back to cyan at 1 %
        if t >= g1:
            battery_hud(ctx, t, color=NEON_CYAN, flash=int(t * 3) % 2 == 0)
        else:
            battery_hud(ctx, t, color=NEON_RED, flash=True)

    def shake(self, lt):
        d0 = self.beat(7, 0)
        g0 = self.beat(8, 0)
        a = 13.0 * max(0.0, 1.0 - abs(lt - d0) / 1.0)
        b = 9.0 * max(0.0, 1.0 - abs(lt - g0) / 0.7)
        amp = a + b
        return (amp * math.sin(lt * 52), amp * math.cos(lt * 47))


# ------------------------------------------------------------------ registry

SCENES = {cls.id: cls for cls in
          (HookOnePercent, StreetGlare, HallwayCreak, PuddleNeon,
           OutletRun, OutletReach)}
