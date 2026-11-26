"""The six scenes of the "forgotten-key-on-the-counter" episode.

Topic: you get home late, the front door is locked, and the brass key is
sitting on the kitchen counter behind the glass — out of reach.
Style: cinematic neon — sharp black silhouettes edged with double-offset
cyan, magenta and amber rim light, pitch-dark interiors cut by street neon,
warm glints on the key and lock cylinder. Camera pushes, tracks and shakes
on every beat.

Obstacle flow:
    door_lock_panic   the hook — latch clicks, empty pockets, the distant glint
    hallway_shadow    slip into the dark hallway, deep shadows stretch
    floorboard_creak  a sharp creak freezes you mid-step
    window_neon_glare cyan + magenta street neon blinds your reflection
    counter_dash      crouch-sprint past table and chairs to the counter edge
    key_grab_unlock   snatch the key, slide back, one clean click, step through

Every visual beat is keyed to a caption chunk via beat(line, chunk), so the
picture lands on the spoken words even if the narration runs long or short.
"""
import math

from PIL import Image

from stick import Ctx, walk_pose
from common import (CHAIR_SIL, COUNTER_BODY, COUNTER_TOP, CREAM,
                    DUST, DOOR_FRAME, DOOR_GAP, DOOR_PANEL,
                    HALL_FLOOR, HALL_SHADOW, INK, INTERIOR_DARK, KEY_BRASS,
                    KEY_GLOW, LOCK_RING, NEON_AMBER, NEON_CYAN, NEON_MAGENTA,
                    NEON_RED, NIGHT_WALL, PANE, PANE_CYAN,
                    PANE_MAGENTA, REFLECT_WHITE, STEEL, TABLE_SIL, WALL_DEEP,
                    W, H, clamp, dim, ease_in_out, ease_out,
                    lerp, pulse, ramp,
                    SS, W2, H2)

# ------------------------------------------------------------------ poses
# Local units: feet / anchor at (0, 0), y negative = up. Poses face right.

POSE_DOOR = {                     # standing at the door, hand on the handle
    "head": (4, -88, 12),
    "spine": [(2, -76), (0, -44)],
    "armL": [(2, -72), (-12, -58), (-19, -42)],
    "armR": [(2, -72), (24, -66), (44, -62)],
    "legL": [(0, -44), (-13, -22), (-16, 0)],
    "legR": [(0, -44), (13, -22), (16, 0)],
}

POSE_PAT_A = {                    # patting the left pocket, rising panic
    "head": (3, -87, 12),
    "spine": [(2, -76), (0, -44)],
    "armL": [(2, -72), (17, -58), (13, -40)],
    "armR": [(2, -72), (-11, -60), (-21, -46)],
    "legL": [(0, -44), (-13, -22), (-16, 0)],
    "legR": [(0, -44), (13, -22), (16, 0)],
}

POSE_PAT_B = {                    # ...then the right pocket
    "head": (3, -87, 12),
    "spine": [(2, -76), (0, -44)],
    "armL": [(2, -72), (-13, -58), (-23, -44)],
    "armR": [(2, -72), (17, -56), (15, -38)],
    "legL": [(0, -44), (-13, -22), (-16, 0)],
    "legR": [(0, -44), (13, -22), (16, 0)],
}

POSE_SIGHT = {                    # arm out, staring at the glint through glass
    "head": (5, -89, 12),
    "spine": [(3, -76), (0, -44)],
    "armL": [(3, -72), (-12, -58), (-20, -44)],
    "armR": [(3, -72), (27, -74), (47, -80)],
    "legL": [(0, -44), (-13, -22), (-16, 0)],
    "legR": [(0, -44), (14, -22), (18, 0)],
}

POSE_SLIP = {                      # low, slipping into the dark hallway
    "head": (8, -74, 12),
    "spine": [(4, -62), (-2, -34)],
    "armL": [(4, -60), (-4, -54), (-16, -50)],
    "armR": [(4, -60), (22, -58), (36, -54)],
    "legL": [(-2, -34), (-24, -20), (-36, 0)],
    "legR": [(-2, -34), (22, -18), (28, 0)],
}

POSE_FREEZE = {                    # frozen mid-step over the bad board
    "head": (2, -88, 12),
    "spine": [(1, -76), (0, -44)],
    "armL": [(1, -72), (-17, -60), (-27, -47)],
    "armR": [(1, -72), (18, -63), (29, -51)],
    "legL": [(0, -44), (-11, -24), (-16, -3)],
    "legR": [(0, -44), (22, -30), (38, -16)],
}

POSE_SHIELD = {                    # arm up, blocking the neon glare
    "head": (3, -87, 12),
    "spine": [(2, -76), (0, -44)],
    "armL": [(2, -72), (-13, -58), (-21, -44)],
    "armR": [(2, -72), (19, -82), (33, -90)],
    "legL": [(0, -44), (-13, -22), (-16, 0)],
    "legR": [(0, -44), (14, -22), (17, 0)],
}

POSE_GRAB = {                      # up on the toes, closing on the key
    "head": (4, -90, 12),
    "spine": [(3, -78), (0, -46)],
    "armL": [(3, -74), (-12, -62), (-22, -50)],
    "armR": [(3, -74), (31, -84), (55, -92)],
    "legL": [(0, -46), (-14, -24), (-18, 0)],
    "legR": [(0, -46), (16, -24), (23, 0)],
}

POSE_TURN = {                      # hand on the lock cylinder, turning
    "head": (4, -88, 12),
    "spine": [(2, -76), (0, -44)],
    "armL": [(2, -72), (-13, -58), (-21, -44)],
    "armR": [(2, -72), (27, -70), (49, -66)],
    "legL": [(0, -44), (-13, -22), (-17, 0)],
    "legR": [(0, -44), (15, -22), (19, 0)],
}


def crouch_walk(p, k=0.62):
    """Low, hurried run: a walk cycle bent down toward the sneak pose."""
    return blend_pose(POSE_SLIP, walk_pose(p), k)


def walk_through(p):
    """Walking out through the doorway, front arm leading."""
    pose = walk_pose(p)
    pose["armR"] = [(0, -72), (24, -70), (41, -66)]
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


def safe_shake(zoom, dx, dy):
    """Clamp a camera offset to the crop slack available at this zoom.

    Keeps the supersampled crop box inside the frame, so a pan or a micro
    shake can never pull black edges into the shot.
    """
    z = max(1.0001, float(zoom))
    sx = 640.0 * (1.0 - 1.0 / z) - 2.0
    sy = 360.0 * (1.0 - 1.0 / z) - 2.0
    return (max(-sx, min(sx, dx)), max(-sy, min(sy, dy)))


def nline(ctx, pts, color, w=6, a=255, halo=3.2, jit=2.0, seed=0.0):
    out = []
    for i, (x, y) in enumerate(pts):
        out.append((x + jit * math.sin(seed + i * 2.3 + x * 0.1),
                    y + jit * math.cos(seed + i * 1.7 + y * 0.1)))
    if halo > 0:
        ctx.line(out, fill=(0, 0, 0, int(a * 0.8)), w=w + int(halo * 2))
    ctx.line(out, fill=tuple(color[:3]) + (a,), w=w)


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
    """Radial speed streaks behind a moving figure."""
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
               off_a=(-8, -7), off_b=(7, 5), face=True, mouth="flat", a=255):
    """Sharp dark silhouette with double-offset neon rim light.

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
                ctx.line([T(p) for p in pose[key]], fill=tuple(col) + (a,), w=w)
        hx, hy, hr = pose["head"]
        ctx.circle(T((hx, hy)), hr * s, fill=tuple(col) + (a,))

    T = _xf(pose, x, y, s, flip, rot, (0.0, 0.0))
    for key in ("spine", "armL", "armR", "legL", "legR"):
        if key in pose:
            ctx.line([T(p) for p in pose[key]], fill=tuple(body) + (a,), w=w)
    hx, hy, hr = pose["head"]
    ctx.circle(T((hx, hy)), hr * s, fill=tuple(body) + (a,))

    if face:
        c = T((hx, hy))
        r = hr * s
        col = rim or CREAM
        for sx in (-1, 1):
            ctx.line([(c[0] + sx * 0.34 * r, c[1] - 0.2 * r),
                      (c[0] + sx * 0.34 * r, c[1] + 0.02 * r)],
                     fill=tuple(col) + (a,), w=max(2, int(w * 0.5)))
        mw = 0.3 * r
        my = c[1] + 0.42 * r
        if mouth == "o":
            ctx.circle((c[0], my), 0.15 * r, outline=tuple(col) + (a,),
                       w=max(2, int(w * 0.5)))
        elif mouth == "grimace":
            ctx.line([(c[0] - mw, my), (c[0] + mw, my)],
                     fill=tuple(col) + (a,), w=max(2, int(w * 0.5)))
        else:
            ctx.line([(c[0] - mw, my), (c[0] + mw * 0.6, my)],
                     fill=tuple(col) + (a,), w=max(2, int(w * 0.5)))
    return T


# ------------------------------------------------------------------ props

def key_prop(ctx, x, y, s=1.0, a=255, color=KEY_BRASS, rot=0.0):
    """A brass key: ring bow, shaft, two teeth."""
    ca, sa = math.cos(rot), math.sin(rot)

    def T(p):
        lx, ly = p[0] * s, p[1] * s
        return (x + lx * ca - ly * sa, y + lx * sa + ly * ca)

    w = max(3, int(round(5 * s)))
    ctx.circle(T((0, 0)), 11 * s, outline=tuple(color) + (a,), w=w)
    ctx.circle(T((0, 0)), 4 * s, fill=(8, 8, 14, a))
    ctx.line([T((11, 0)), T((47, 0))], fill=tuple(color) + (a,), w=w)
    ctx.line([T((38, 0)), T((38, 11))], fill=tuple(color) + (a,), w=w)
    ctx.line([T((47, 0)), T((47, 8))], fill=tuple(color) + (a,), w=w)


def key_hud(ctx, t, held=False, unlocked=False, at=(52, 40)):
    """Persistent readout: is the key in your pocket yet?"""
    x, y = at
    bw, bh = 232, 44
    col = NEON_CYAN if unlocked else (KEY_BRASS if held else NEON_RED)
    label = "UNLOCKED" if unlocked else ("KEY: HELD" if held else "KEY: MISSING")
    blink = (not held) and (not unlocked)
    on = (not blink) or (int(t * 5) % 2 == 0)
    col = col if on else dim(col, 0.45)
    if on:
        ctx.glow((x + bw / 2, y + bh / 2), bw * 0.8, col, alpha=38)
    ctx.rrect([x, y, x + bw, y + bh], 10, fill=(3, 5, 12, 228),
              outline=tuple(col) + (255,), w=4)
    # little key glyph on the left
    gx, gy = x + 28, y + bh / 2
    ctx.circle((gx, gy), 9, outline=tuple(col) + (255,), w=3)
    ctx.line([(gx + 9, gy), (gx + 30, gy)], fill=tuple(col) + (255,), w=3)
    ctx.line([(gx + 24, gy), (gx + 24, gy + 7)], fill=tuple(col) + (255,), w=3)
    ntext(ctx, (x + 70, y + bh / 2 + 1), label, size=20, color=col,
          anchor="lm", halo=1.5)


# ------------------------------------------------------------------ scenes

class Scene:
    id = "base"
    zoom_range = (1.06, 1.10)

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

    def hud(self, ctx, lt, held=False, unlocked=False):
        """Draw the key HUD pinned to the frame, undoing pan + zoom."""
        z = self.zoom(lt)
        dx, dy = self.shake(lt)
        left = 640.0 * (1.0 - 1.0 / z) + dx
        top = 360.0 * (1.0 - 1.0 / z) + dy
        key_hud(ctx, lt, held=held, unlocked=unlocked,
                at=(52.0 / z + left, 40.0 / z + top))

    def zoom(self, lt):
        p = clamp(lt / self.span())
        a, b = self.zoom_range
        return lerp(a, b, p)


# --------------------------------------------- 1 · the hook: locked out

class DoorLockPanic(Scene):
    id = "door_lock_panic"
    zoom_range = (1.06, 1.16)

    KEY_AT = (700, 366)      # the key on the counter, far behind the glass

    def build(self):
        self.bg = make_bg((12, 14, 30), (3, 4, 10))
        ctx = Ctx(self.bg)
        ctx.glow((30, 170), 360, NEON_CYAN, alpha=46)        # street neon, off-frame
        ctx.glow((1255, 610), 380, NEON_MAGENTA, alpha=44)   # shopfront spill
        # exterior wall with brick courses
        ctx.poly([(0, 30), (W, 30), (W, 706), (0, 706)], fill=NIGHT_WALL + (255,))
        for k in range(9):
            ctx.line([(0, 52 + k * 74), (W, 52 + k * 74)], fill=(17, 19, 38, 255), w=3)
        # the heavy front door
        nrrect(ctx, [452, 46, 878, 708], 12, DOOR_FRAME, w=7,
               fill=DOOR_PANEL + (255,))
        # glass panel: the dark room and the counter behind it
        ctx.rrect([500, 92, 834, 404], 8, fill=INTERIOR_DARK + (255,),
                  outline=NEON_CYAN + (150,), w=4)
        ctx.poly([(516, 356), (820, 356), (820, 400), (516, 400)],
                 fill=COUNTER_BODY + (255,))
        ctx.line([(516, 356), (820, 356)], fill=NEON_AMBER + (150,), w=4)
        ctx.line([(667, 96), (667, 400)], fill=(30, 44, 66, 255), w=5)
        ctx.line([(504, 250), (830, 250)], fill=(30, 44, 66, 255), w=5)
        # handle + lock cylinder
        ctx.line([(560, 556), (712, 556)], fill=NEON_AMBER + (235,), w=12)
        ctx.line([(562, 528), (562, 556)], fill=NEON_AMBER + (200,), w=10)
        ctx.circle((772, 496), 30, fill=LOCK_RING + (255,))
        ctx.circle((772, 496), 15, fill=(9, 8, 14, 255))
        # doorstep + mat
        ctx.poly([(420, 708), (910, 708), (952, 720), (378, 720)],
                 fill=(21, 21, 36, 255))
        ctx.line([(420, 708), (910, 708)], fill=INK + (255,), w=4)

    def draw(self, ctx, lt):
        t = lt
        b0 = self.beat(0, 0)
        b1 = self.beat(0, 1)          # latch click / "will not turn"
        c0 = self.beat(1, 0)          # patting pockets
        c1 = self.beat(1, 1)          # the glint
        c2 = self.beat(1, 2)          # behind the glass

        rate = 2.6 + 2.6 * clamp(ramp(t, c0, c2))
        ph = 0.5 + 0.5 * math.sin(2 * math.pi * rate * lt)

        # ---- the key on the counter, far behind the glass
        kx, ky = self.KEY_AT
        g = 0.55 + 0.45 * pulse(t, 1.7)
        ctx.glow((kx, ky), 58 * g, NEON_AMBER, alpha=int(64 * g))
        key_prop(ctx, kx, ky, 1.15, a=int(210 + 45 * g), rot=-0.35)
        if t >= c1:
            for i in range(4):
                ang = lt * 1.3 + i * math.pi / 2
                rr = 36 + 9 * math.sin(lt * 3 + i)
                px, py = kx + rr * math.cos(ang), ky + rr * math.sin(ang) * 0.7
                ctx.circle((px, py), 3.4, fill=KEY_GLOW + (int(205 * g),))

        # ---- pose: handle -> empty pockets -> spotting the key
        x, y, s = 356.0, 706.0, 3.0
        mouth = "flat"
        if t < c0:
            panic = clamp(ramp(t, b0, c0))
            pose = POSE_DOOR
            rot = 0.030 * math.sin(lt * 15) * (0.35 + panic)
            if t >= b1:
                mouth = "o"
        elif t < c1:
            pose = blend_pose(POSE_PAT_A, POSE_PAT_B, ph)
            rot = 0.0
            mouth = "grimace"
        else:
            pose = POSE_SIGHT
            rot = 0.0
            mouth = "o"

        T = silhouette(ctx, x, y, s, pose, rim=NEON_CYAN, rim2=NEON_MAGENTA,
                       w=9, rot=rot, mouth=mouth)
        head = T((0, -88))

        # ---- pat marks at the pockets
        if c0 <= t < c1:
            for side in (-1, 1):
                hot = (ph < 0.5) if side < 0 else (ph >= 0.5)
                if not hot:
                    continue
                px, py = x + side * 46, y - 118
                for k in range(2):
                    rr = 15 + k * 13
                    ctx.arc([px - rr, py - rr * 0.7, px + rr, py + rr * 0.7],
                            300, 60 if side > 0 else 120,
                            fill=NEON_RED + (210,), w=4)

        # ---- sweat while the panic climbs
        if t >= c0:
            for i in range(3):
                k = (lt * 1.3 + i * 0.33) % 1.0
                sx = head[0] - 34 - i * 17
                sy = head[1] - 32 + 74 * k
                ctx.poly([(sx, sy - 9), (sx + 6, sy + 3), (sx, sy + 9), (sx - 6, sy + 3)],
                         fill=NEON_CYAN + (int(200 * (1 - k)),))

        # ---- sight line from the hero to the key
        if t >= c1:
            seg = 9
            a = int(150 * (0.55 + 0.45 * pulse(t, 2.4)))
            for k in range(seg):
                f0, f1 = k / seg, (k + 0.55) / seg
                ctx.line([(lerp(head[0] + 20, kx, f0), lerp(head[1] - 6, ky, f0)),
                          (lerp(head[0] + 20, kx, f1), lerp(head[1] - 6, ky, f1))],
                         fill=NEON_CYAN + (a,), w=3)

        # ---- labels
        if t >= b1:
            ntext(ctx, (772, 442), "LOCKED", size=26, color=NEON_RED,
                  a=int(210 + 45 * pulse(t, 3.2)))
        if t >= c1:
            ntext(ctx, (kx, ky - 64), "THE KEY", size=26, color=KEY_BRASS,
                  a=int(200 + 55 * pulse(t, 2.0)))
        if t >= c2:
            ntext(ctx, (667, 434), "OUT OF REACH", size=24, color=NEON_CYAN,
                  a=int(175 + 60 * pulse(t, 2.6)))

        self.hud(ctx, lt)

    def shake(self, lt):
        b1 = self.beat(0, 1)
        c0 = self.beat(1, 0)
        k = max(0.0, 1.0 - abs(lt - b1) / 0.9)
        amp = 11.0 * k * k
        tremble = 0.0 if lt < c0 else 2.6 * clamp((lt - c0) / 3.0)
        dx = amp * math.sin(lt * 55) + tremble * math.sin(lt * 13)
        dy = amp * 0.7 * math.cos(lt * 47) + tremble * math.cos(lt * 11)
        return safe_shake(self.zoom(lt), dx, dy)


# --------------------------------------- 2 · obstacle: the dark hallway

class HallwayShadow(Scene):
    id = "hallway_shadow"
    zoom_range = (1.06, 1.14)

    def build(self):
        self.bg = make_bg((11, 13, 27), (4, 5, 12))
        ctx = Ctx(self.bg)
        ctx.glow((170, 250), 300, NEON_MAGENTA, alpha=52)   # window spill
        ctx.glow((1180, 380), 300, NEON_CYAN, alpha=44)     # the way back out
        # floor + wall
        ctx.poly([(0, 0), (W, 0), (W, 548), (0, 548)], fill=WALL_DEEP + (255,))
        ctx.poly([(0, 548), (W, 548), (W, H), (0, H)], fill=HALL_FLOOR + (255,))
        ctx.line([(0, 548), (W, 548)], fill=INK + (255,), w=5)
        for k in range(4):
            ctx.line([(0, 120 + k * 110), (W, 120 + k * 110)],
                     fill=(18, 20, 38, 255), w=3)
        # window with magenta street neon
        nrrect(ctx, [70, 118, 300, 430], 8, NEON_MAGENTA, w=5,
               fill=PANE_MAGENTA + (255,))
        ctx.glow((185, 274), 230, NEON_MAGENTA, alpha=70)
        ctx.line([(185, 122), (185, 426)], fill=(10, 8, 18, 255), w=6)
        ctx.line([(74, 274), (296, 274)], fill=(10, 8, 18, 255), w=6)
        # far doorway: the way back to the front door
        nrrect(ctx, [1096, 168, 1252, 646], 6, NEON_CYAN, w=5,
               fill=(4, 5, 12, 255))
        ctx.glow((1174, 410), 190, NEON_CYAN, alpha=64)
        # skirting board
        ctx.line([(0, 500), (W, 500)], fill=(26, 24, 44, 255), w=6)
        # deep shadow wedges already lying across the hall
        for x0, w0 in ((330, 150), (620, 120), (860, 170)):
            ctx.poly([(x0, 548), (x0 + w0, 548), (x0 + w0 + 300, H), (x0 + 150, H)],
                     fill=HALL_SHADOW + (255,))
        for x0, w0 in ((380, 130), (700, 110)):
            ctx.poly([(x0, 0), (x0 + w0, 0), (x0 + w0 + 210, 548), (x0 + 90, 548)],
                     fill=HALL_SHADOW + (235,))

    def draw(self, ctx, lt):
        t = lt
        p = clamp(lt / self.span())
        b1 = self.beat(2, 1)          # "the shadows stretch"
        b2 = self.beat(2, 2)          # "longer than the hall"

        x = 250 + 420 * ease_out(p)
        y, s = 646.0, 2.9
        pose = crouch_walk((lt * 1.25) % 1.0)
        T = silhouette(ctx, x, y, s, pose, rim=NEON_CYAN, rim2=NEON_MAGENTA,
                       w=8, mouth="o")

        # the shadow he throws, stretching with the beat
        grow = ease_out(clamp(ramp(t, b1, b1 + 2.2)))
        sh = 210 + 300 * grow
        ctx.poly([(x - 34, y + 4), (x + 34, y + 4), (x + sh, H - 4),
                  (x + sh * 0.62, H - 4)], fill=(3, 4, 10, 225))
        ctx.poly([(x - 26, y - 150), (x + 20, y - 150),
                  (x + 60 + sh * 0.5, 250), (x + 10 + sh * 0.5, 250)],
                 fill=(4, 5, 12, 150))

        # hushed footstep: a soft cyan puff where the foot lands
        ph = (lt * 1.25) % 1.0
        d = min(ph, abs(ph - 0.5), abs(ph - 1.0))
        if d < 0.16:
            a = int(130 * (1 - d / 0.16))
            fx = x + (22 if ph < 0.5 or ph > 0.9 else -22)
            ctx.ellipse([fx - 34, y - 8, fx + 34, y + 10], fill=NEON_CYAN + (a,))

        # the far doorway dims as the shadows take the hall
        if t >= b2:
            k = clamp(ramp(t, b2, b2 + 1.6))
            ctx.poly([(1100, 172), (1248, 172), (1248, 642), (1100, 642)],
                     fill=INTERIOR_DARK + (int(170 * k),))
            ntext(ctx, (1174, 130), "NO LIGHT", size=22, color=NEON_MAGENTA,
                  a=int(150 * k + 60 * pulse(t, 2.2)))

        self.hud(ctx, lt)

    def shake(self, lt):
        p = clamp(lt / self.span())
        dx = 34 * p
        dy = 3.0 * math.sin(lt * 5.2) + 2.0 * math.sin(lt * 2.1)
        return safe_shake(self.zoom(lt), dx, dy)


# ---------------------------- 3 · obstacle: the floorboard that creaks

class FloorboardCreak(Scene):
    id = "floorboard_creak"
    zoom_range = (1.08, 1.18)

    BOARD = (300, 566, 596, 716)     # the board that gives underfoot

    def build(self):
        self.bg = make_bg((12, 13, 28), (5, 6, 14))
        ctx = Ctx(self.bg)
        ctx.glow((90, 300), 340, NEON_MAGENTA, alpha=46)
        ctx.glow((1200, 200), 300, NEON_CYAN, alpha=34)
        # wall + skirting
        ctx.poly([(0, 0), (W, 0), (W, 470), (0, 470)], fill=WALL_DEEP + (255,))
        ctx.line([(0, 470), (W, 470)], fill=(28, 26, 46, 255), w=7)
        # floor with boards running toward camera
        ctx.poly([(0, 470), (W, 470), (W, H), (0, H)], fill=HALL_FLOOR + (255,))
        for k in range(7):
            yy = 486 + k * 40
            ctx.line([(0, yy), (W, yy)], fill=(10, 11, 22, 255), w=4)
        for k in range(8):
            xx = -80 + k * 220
            ctx.line([(xx + 40, 470), (xx - 60, H)], fill=(9, 10, 20, 255), w=4)
        # doorway edge on the right, magenta sliver on the left
        ctx.poly([(1120, 60), (W, 30), (W, 660), (1120, 620)],
                 fill=(7, 8, 17, 255), outline=INK + (255,), w=5)
        # dust motes hanging in the light
        for i in range(26):
            px = (i * 173) % W
            py = 60 + (i * 97) % 560
            ctx.circle((px, py), 1.6 + (i % 3) * 0.7, fill=DUST + (90,))

    def draw(self, ctx, lt):
        t = lt
        b0 = self.beat(3, 0)          # "One floorboard creaks"
        b1 = self.beat(3, 1)          # "you freeze mid-step"
        b2 = self.beat(3, 2)          # "listening"

        # ---- the board dips, then settles
        dip = 10 * math.sin(math.pi * clamp((t - b0) / 0.9)) if t >= b0 else 0.0
        creak = clamp(ramp(t, b0, b0 + 0.5))
        x0, y0, x1, y1 = self.BOARD
        ctx.poly([(x0, y0 + dip), (x1, y0 + dip), (x1 + 40, y1 + dip),
                  (x0 - 30, y1 + dip)], fill=(34, 31, 52, 255),
                 outline=(78, 68, 104, 255), w=5)
        ctx.line([(x0 - 10, y0 + 6 + dip), (x1 + 20, y0 + 6 + dip)],
                 fill=NEON_AMBER + (90,), w=3)
        crack = [(x0 + 40, y0 + 30), (x0 + 90, y0 + 74),
                 (x0 + 60, y1 - 30), (x0 + 130, y1 - 6)]
        nline(ctx, crack, NEON_MAGENTA if creak > 0.05 else (64, 44, 74), w=4,
              a=int(120 + 135 * creak), halo=2.0, jit=1.2, seed=lt * 0.4)

        # ---- frozen mid-step, one foot still over the board
        x, y, s = 470.0, 716.0, 3.2
        tremble = 0.010 * math.sin(lt * 26) * (0.4 + 0.6 * clamp(ramp(t, b0, b0 + 1.5)))
        T = silhouette(ctx, x, y, s, POSE_FREEZE, rim=NEON_CYAN,
                       rim2=NEON_MAGENTA, w=9, rot=tremble, mouth="o")
        head = T((0, -88))

        # ---- the creak shock: magenta arcs + the word
        if b0 <= t < b0 + 1.7:
            k = clamp((t - b0) / 1.7)
            for i in range(3):
                rr = 46 + i * 40 + 90 * k
                ctx.arc([448 - rr, 640 - rr * 0.7, 448 + rr, 640 + rr * 0.7],
                        200, 340, fill=NEON_MAGENTA + (int(230 * (1 - k)),), w=5)
            ntext(ctx, (760, 520), "CREEEAK", size=36, color=NEON_MAGENTA,
                  a=int(255 * (1 - 0.6 * k)))

        # ---- dust shaken loose by the creak
        if t >= b0:
            for i in range(5):
                k = ((lt - b0) * 0.5 + i * 0.2) % 1.0
                px = 360 + i * 60 + 10 * math.sin(lt * 2 + i)
                py = 430 + 250 * k
                ctx.circle((px, py), 2.4, fill=DUST + (int(150 * (1 - k)),))

        # ---- listening: a cyan pulse off the ear
        if t >= b2:
            for i in range(3):
                k = ((lt - b2) * 0.9 + i / 3.0) % 1.0
                rr = 26 + 90 * k
                ctx.arc([head[0] - rr, head[1] - rr, head[0] + rr, head[1] + rr],
                        -62, 62, fill=NEON_CYAN + (int(170 * (1 - k)),), w=4)
            ntext(ctx, (head[0] + 6, head[1] - 74), "…", size=44, color=NEON_CYAN,
                  a=int(190 + 60 * pulse(t, 2.0)))

        self.hud(ctx, lt)

    def shake(self, lt):
        b0 = self.beat(3, 0)
        k = max(0.0, 1.0 - abs(lt - b0) / 0.55)
        a = 13.0 * k * k
        dx = a * math.sin(lt * 62) + 1.6 * math.sin(lt * 1.7)
        dy = a * 0.6 * math.cos(lt * 54) + 1.2 * math.cos(lt * 1.3)
        return safe_shake(self.zoom(lt), dx, dy)


# --------------------- 4 · obstacle: neon through the glass door

class WindowNeonGlare(Scene):
    id = "window_neon_glare"
    zoom_range = (1.06, 1.15)

    PANE = (612, 64, 1252, 636)

    def build(self):
        self.bg = make_bg((11, 13, 28), (4, 5, 12))
        ctx = Ctx(self.bg)
        # interior wall + floor
        ctx.poly([(0, 0), (W, 0), (W, 600), (0, 600)], fill=WALL_DEEP + (255,))
        ctx.poly([(0, 600), (W, 600), (W, H), (0, H)], fill=HALL_FLOOR + (255,))
        ctx.line([(0, 600), (W, 600)], fill=INK + (255,), w=5)
        # wide glass door
        nrrect(ctx, [600, 52, 1264, 648], 8, DOOR_FRAME, w=7, fill=PANE + (255,))
        ctx.rrect(self.PANE, 6, fill=(9, 14, 26, 255),
                  outline=(36, 54, 78, 255), w=4)
        # street neon outside the glass
        ctx.poly([(648, 74), (712, 74), (742, 626), (664, 626)],
                 fill=PANE_CYAN + (255,))
        ctx.glow((692, 350), 260, NEON_CYAN, alpha=76)
        ctx.poly([(1108, 74), (1180, 74), (1160, 626), (1096, 626)],
                 fill=PANE_MAGENTA + (255,))
        ctx.glow((1140, 350), 250, NEON_MAGENTA, alpha=74)
        # mullions + handle
        ctx.line([(930, 74), (930, 626)], fill=(30, 46, 70, 255), w=7)
        ctx.line([(616, 350), (1248, 350)], fill=(30, 46, 70, 255), w=7)
        ctx.line([(886, 380), (886, 520)], fill=STEEL + (255,), w=9)
        # left wall detail
        ctx.line([(0, 540), (600, 540)], fill=(26, 24, 44, 255), w=6)
        nrrect(ctx, [96, 150, 340, 400], 6, (44, 40, 66), w=5,
               fill=(14, 14, 26, 255))

    def draw(self, ctx, lt):
        t = lt
        p = clamp(lt / self.span())
        b1 = self.beat(4, 1)          # "slices across the room"
        b2 = self.beat(4, 2)          # "blinds your reflection"

        x = 170 + 520 * ease_in_out(p)
        y, s = 664.0, 3.0
        stride = (lt * 1.3) % 1.0

        # ---- his reflection in the glass, parallaxing behind him
        rx = 660 + (x - 170) * 0.62
        ref_pose = POSE_SHIELD if t >= b2 else walk_pose(stride)
        silhouette(ctx, rx, y, s * 0.94, ref_pose, rim=REFLECT_WHITE,
                   rim2=NEON_CYAN, body=(16, 22, 38), w=8, flip=True,
                   face=False, a=175)

        # ---- neon slices across the floor and wall
        slice_a = int(88 + 70 * clamp(ramp(t, b1 - 0.4, b1 + 0.8)))
        ctx.poly([(648, 626), (742, 626), (300, H), (60, H)],
                 fill=NEON_CYAN + (slice_a,))
        ctx.poly([(1096, 626), (1170, 626), (980, H), (760, H)],
                 fill=NEON_MAGENTA + (slice_a,))
        ctx.poly([(660, 74), (716, 74), (470, 600), (360, 600)],
                 fill=NEON_CYAN + (slice_a // 3,))

        # ---- the hero, arm up against the glare
        if t >= b2:
            pose = blend_pose(walk_pose(stride), POSE_SHIELD,
                              ease_out(clamp(ramp(t, b2, b2 + 0.5))))
        else:
            pose = walk_pose(stride)
        silhouette(ctx, x, y, s, pose, rim=NEON_CYAN, rim2=NEON_MAGENTA,
                   w=9, mouth="o" if t >= b2 else "flat")

        # ---- the flash that blows out the reflection
        if t >= b2:
            k = clamp((t - b2) / 1.6)
            flash = (1 - k) * (0.5 + 0.5 * pulse(t, 6.0))
            ctx.poly([(rx - 92, 84), (rx + 58, 84), (rx + 118, 618), (rx - 42, 618)],
                     fill=REFLECT_WHITE + (int(150 * flash),))
            ntext(ctx, (rx, 214), "GLARE", size=30, color=REFLECT_WHITE,
                  a=int(235 * flash))

        self.hud(ctx, lt)

    def shake(self, lt):
        p = clamp(lt / self.span())
        b2 = self.beat(4, 2)
        k = max(0.0, 1.0 - abs(lt - b2) / 0.8)
        dx = 30 * p + 7.0 * k * k * math.sin(lt * 58)
        dy = 3.0 * math.sin(lt * 4.4) + 4.5 * k * k * math.cos(lt * 50)
        return safe_shake(self.zoom(lt), dx, dy)


# --------------------------------------- 5 · the dash: table -> counter

class CounterDash(Scene):
    id = "counter_dash"
    zoom_range = (1.06, 1.18)

    KEY_AT = (1075, 406)

    def build(self):
        self.bg = make_bg((13, 13, 28), (5, 6, 13))
        ctx = Ctx(self.bg)
        ctx.glow((1140, 350), 340, NEON_AMBER, alpha=64)   # the key's light
        ctx.glow((70, 430), 300, NEON_CYAN, alpha=40)      # street behind you
        # back wall + floor
        ctx.poly([(0, 0), (W, 0), (W, 596), (0, 596)], fill=WALL_DEEP + (255,))
        ctx.poly([(0, 596), (W, 596), (W, H), (0, H)], fill=HALL_FLOOR + (255,))
        ctx.line([(0, 596), (W, 596)], fill=INK + (255,), w=5)
        # kitchen counter on the right
        ctx.poly([(880, 452), (W, 452), (W, H), (880, H)],
                 fill=COUNTER_BODY + (255,))
        ctx.poly([(856, 424), (W, 424), (W, 464), (856, 464)],
                 fill=COUNTER_TOP + (255,))
        ctx.line([(856, 424), (W, 424)], fill=NEON_AMBER + (210,), w=5)
        for k in range(3):
            ctx.line([(960 + k * 110, 470), (960 + k * 110, H)],
                     fill=(12, 10, 20, 255), w=5)
        # table silhouette on the left
        ctx.poly([(120, 430), (520, 430), (540, 466), (104, 466)],
                 fill=TABLE_SIL + (255,))
        ctx.line([(160, 466), (148, 664)], fill=TABLE_SIL + (255,), w=16)
        ctx.line([(486, 466), (500, 664)], fill=TABLE_SIL + (255,), w=16)
        # two chair silhouettes he has to slip past
        for cx, flip in ((600, 1), (742, -1)):
            ctx.poly([(cx - 46, 470), (cx + 46, 470), (cx + 40, 500), (cx - 40, 500)],
                     fill=CHAIR_SIL + (255,))
            ctx.poly([(cx - 40, 500), (cx + 40, 500), (cx + 30, 690), (cx - 30, 690)],
                     fill=CHAIR_SIL + (255,))
            ctx.poly([(cx + 34 * flip, 330), (cx + 66 * flip, 336),
                      (cx + 60 * flip, 500), (cx + 30 * flip, 498)],
                     fill=CHAIR_SIL + (255,))

    def draw(self, ctx, lt):
        t = lt
        p = clamp(lt / self.span())
        b0 = self.beat(5, 0)          # "crouch-sprint past table and chairs"
        b1 = self.beat(5, 1)          # "toward the kitchen counter edge"

        # ---- the key waiting on the counter
        kx, ky = self.KEY_AT
        g = 0.55 + 0.45 * pulse(t, 1.9) + 0.35 * clamp(ramp(t, b1, b1 + 1.2))
        ctx.glow((kx, ky), 66 * min(1.4, g), NEON_AMBER, alpha=int(72 * min(1.4, g)))
        key_prop(ctx, kx, ky, 1.2, a=255, rot=-0.3)

        # ---- the crouch-sprint
        x = 140 + 700 * (p ** 1.5)
        y, s = 706.0, 2.9
        T = silhouette(ctx, x, y, s, crouch_walk((lt * 2.2) % 1.0),
                       rim=NEON_AMBER, rim2=NEON_CYAN, w=8, mouth="grimace")

        # speed streaks trailing behind him
        for i in range(5):
            yy = 500 + i * 44
            ctx.line([(x - 300 - i * 44, yy), (x - 150 - i * 30, yy)],
                     fill=NEON_CYAN + (120 - i * 18,), w=5)
        motion_lines(ctx, x - 60, 560, 200, n=4, r0=60, r1=190,
                     color=NEON_MAGENTA, a=150, w=5)

        # ---- labels as he commits to the counter
        if t >= b1:
            ntext(ctx, (kx, ky - 62), "KEY", size=30, color=KEY_BRASS,
                  a=int(205 + 50 * pulse(t, 2.4)))
            ntext(ctx, (980, 566), "REACH", size=24, color=NEON_AMBER,
                  a=int(140 + 70 * pulse(t, 3.0)))

        self.hud(ctx, lt)

    def shake(self, lt):
        p = clamp(lt / self.span())
        b0 = self.beat(5, 0)
        k = max(0.0, 1.0 - abs(lt - b0) / 0.7)
        dx = 40 * p + 6.0 * k * k * math.sin(lt * 60)
        dy = 3.4 * math.sin(lt * 9.0) + 3.0 * k * k * math.cos(lt * 52)
        return safe_shake(self.zoom(lt), dx, dy)


# ------------------------- 6 · the finish: grab, slide, one clean click

class KeyGrabUnlock(Scene):
    id = "key_grab_unlock"
    zoom_range = (1.16, 1.04)          # pulls back as the door opens

    KEY_AT = (1085, 412)
    LOCK_AT = (390, 496)

    def build(self):
        self.bg = make_bg((12, 14, 30), (4, 5, 12))
        ctx = Ctx(self.bg)
        ctx.glow((60, 300), 340, NEON_CYAN, alpha=44)
        ctx.glow((1255, 620), 360, NEON_MAGENTA, alpha=44)
        # wall + floor
        ctx.poly([(0, 0), (W, 0), (W, 660), (0, 660)], fill=NIGHT_WALL + (255,))
        for k in range(8):
            ctx.line([(0, 54 + k * 74), (W, 54 + k * 74)], fill=(17, 19, 38, 255), w=3)
        ctx.poly([(0, 660), (W, 660), (W, H), (0, H)], fill=HALL_FLOOR + (255,))
        ctx.line([(0, 660), (W, 660)], fill=INK + (255,), w=5)
        # kitchen counter on the right
        ctx.poly([(880, 452), (W, 452), (W, H), (880, H)],
                 fill=COUNTER_BODY + (255,))
        ctx.poly([(856, 424), (W, 424), (W, 464), (856, 464)],
                 fill=COUNTER_TOP + (255,))
        ctx.line([(856, 424), (W, 424)], fill=NEON_AMBER + (210,), w=5)
        for k in range(3):
            ctx.line([(960 + k * 110, 470), (960 + k * 110, H)],
                     fill=(12, 10, 20, 255), w=5)
        # mat + doorstep on the left
        ctx.poly([(40, 708), (500, 708), (540, 720), (0, 720)],
                 fill=(21, 21, 36, 255))

    def draw(self, ctx, lt):
        t = lt
        g0 = self.beat(6, 0)          # "fingers close around the key"
        g1 = self.beat(6, 1)          # "brass and finally real"
        s0 = self.beat(7, 0)          # "slide back to the door"
        s1 = self.beat(7, 1)          # "turn the cylinder"
        u0 = self.beat(8, 0)          # "one clean click"
        u1 = self.beat(8, 1)          # "step through into the night"

        lx, ly = self.LOCK_AT

        # ---- the front door (opens after the click)
        gap = 230 * ease_out(clamp(ramp(t, u0 + 0.1, u0 + 1.5))) if t >= u0 else 0.0
        if gap > 1:
            ctx.poly([(70, 60), (70 + gap, 60), (70 + gap, 704), (70, 704)],
                     fill=DOOR_GAP + (255,))
            ctx.glow((70 + gap / 2, 380), 200 * min(1.0, gap / 120),
                     DOOR_GAP, alpha=110)
        door_x0 = 70 + gap
        nrrect(ctx, [door_x0, 52, 470, 708], 12, DOOR_FRAME, w=7,
               fill=DOOR_PANEL + (255,))
        # glass panel in the door (cyan street outside)
        if gap < 380:
            ctx.rrect([door_x0 + 48, 96, 424, 380], 8, fill=INTERIOR_DARK + (255,),
                      outline=NEON_CYAN + (150,), w=4)
            ctx.line([(door_x0 + 48 + (424 - door_x0 - 48) / 2, 100),
                      (door_x0 + 48 + (424 - door_x0 - 48) / 2, 376)],
                     fill=(30, 44, 66, 255), w=5)
        # handle + lock cylinder (dynamic so the key can turn in it)
        if gap < 120:
            ha = int(255 * (1 - gap / 120.0))
            ctx.line([(lx - 220, 556), (lx - 70, 556)],
                     fill=NEON_AMBER + (ha,), w=12)
            ctx.line([(lx - 218, 528), (lx - 218, 556)],
                     fill=NEON_AMBER + (ha,), w=10)
        turn = ease_out(clamp(ramp(t, s1, s1 + 0.6)))
        ctx.circle((lx, ly), 30, fill=LOCK_RING + (255,))
        ctx.circle((lx, ly), 15, fill=(9, 8, 14, 255))
        ctx.line([(lx - 9, ly), (lx + 9, ly)], fill=LOCK_RING + (255,), w=5)
        if t >= s1:
            ang = math.radians(-90 + 150 * turn)
            ctx.line([(lx, ly), (lx + 13 * math.cos(ang), ly + 13 * math.sin(ang))],
                     fill=(255, 255, 255, 230), w=5)

        # ---- hero: approach, grab, slide back, turn, step through
        if t < s0:
            x = 243 + 657 * ease_in_out(clamp(ramp(t, 0, g0)))
            reach = ease_in_out(clamp(ramp(t, g0 - 1.4, g0)))
            pose = blend_pose(crouch_walk((lt * 2.0) % 1.0), POSE_GRAB, reach)
            rot = 0.0
            mouth = "o" if t >= g0 else "flat"
        elif t < s1:
            sl = ease_in_out(clamp(ramp(t, s0, s1 - 0.15)))
            x = lerp(900, 243, sl)
            pose = crouch_walk((lt * 2.4) % 1.0, k=0.5)
            rot = -0.05 * math.sin(lt * 18)
            mouth = "grimace"
        elif t < u1:
            x = 243
            pose = POSE_TURN
            rot = 0.02 * math.sin(lt * 11)
            mouth = "o"
        else:
            step = ease_in_out(clamp(ramp(t, u1, u1 + 1.8)))
            x = lerp(243, 118, step)
            pose = blend_pose(POSE_TURN, walk_through((lt * 1.5) % 1.0), step)
            rot = 0.0
            mouth = "flat"

        T = silhouette(ctx, x, 706.0, 3.0, pose, rim=NEON_CYAN,
                       rim2=NEON_MAGENTA if t < u0 else NEON_AMBER,
                       w=9, rot=rot, mouth=mouth)

        # ---- the key: counter -> hand -> lock
        kx, ky = self.KEY_AT
        if t < g0:
            g = 0.55 + 0.45 * pulse(t, 1.9)
            ctx.glow((kx, ky), 64 * g, NEON_AMBER, alpha=int(70 * g))
            key_prop(ctx, kx, ky, 1.2, a=255, rot=-0.3)
        elif t < s1:
            hx, hy = x + 58, 706 - 158 + 6 * math.sin(lt * 7)
            ctx.glow((hx, hy), 54, NEON_AMBER, alpha=74)
            key_prop(ctx, hx, hy, 1.1, a=255, rot=0.5 + 0.3 * math.sin(lt * 9))
            if g0 <= t < g0 + 1.0:      # jingle burst as it comes off the counter
                k = clamp((t - g0) / 1.0)
                for i in range(5):
                    ang = lt * 4 + i * 1.256
                    rr = 30 + 60 * k
                    ctx.circle((hx + rr * math.cos(ang), hy + rr * math.sin(ang) * 0.8),
                               3.4, fill=KEY_GLOW + (int(220 * (1 - k)),))
        else:
            # in the cylinder, turning
            key_prop(ctx, lx - 6, ly, 1.0, a=255, rot=math.radians(-40 + 150 * turn))
            ctx.glow((lx, ly), 74, NEON_AMBER, alpha=int(70 + 50 * pulse(t, 3.0)))

        # ---- slide-back trails
        if s0 < t < s1:
            k = clamp((t - s0) / (s1 - s0))
            for i in range(4):
                ctx.line([(x + 300 + i * 60, 706 - 60 - i * 34),
                          (x + 120 + i * 40, 706 - 34 - i * 30)],
                         fill=NEON_CYAN + (140 - i * 26,), w=6)

        # ---- the click: amber rings off the cylinder
        if u0 <= t < u0 + 1.6:
            k = clamp((t - u0) / 1.6)
            for i in range(3):
                kk = clamp(k * 1.3 - i * 0.2)
                if 0 < kk < 1:
                    rr = 40 + 260 * kk
                    ctx.circle((lx, ly), rr,
                               outline=NEON_AMBER + (int(230 * (1 - kk)),), w=6)
            ntext(ctx, (lx + 40, ly - 130), "CLICK", size=44, color=KEY_GLOW,
                  a=int(255 * (1 - 0.55 * k)))

        # ---- unlocked label on the open doorway
        if t >= u0 + 0.8:
            ntext(ctx, (180, 140), "UNLOCKED", size=34, color=NEON_CYAN,
                  a=int(190 + 65 * pulse(t, 2.2)))

        self.hud(ctx, lt, held=(g0 <= t < u0), unlocked=t >= u0)

    def shake(self, lt):
        g0 = self.beat(6, 0)
        u0 = self.beat(8, 0)
        a = 9.0 * max(0.0, 1.0 - abs(lt - g0) / 0.7)
        b = 12.0 * max(0.0, 1.0 - abs(lt - u0) / 0.8)
        amp = a + b
        dx = amp * math.sin(lt * 56) + 1.4 * math.sin(lt * 2.3)
        dy = amp * 0.7 * math.cos(lt * 49) + 1.2 * math.cos(lt * 1.9)
        return safe_shake(self.zoom(lt), dx, dy)


# ------------------------------------------------------------------ registry

SCENES = {cls.id: cls for cls in
          (DoorLockPanic, HallwayShadow, FloorboardCreak, WindowNeonGlare,
           CounterDash, KeyGrabUnlock)}




