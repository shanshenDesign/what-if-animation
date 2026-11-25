"""The six scenes of the "feeling behind" episode — Design 02.

Style: **Neon-on-black sketch.** A near-black canvas, no photographic or
warm-gradient backgrounds: every element is a glowing neon stroke (ice-white
figures, cyan = you, magenta = everyone else, neon-red = motion lines and
alerts) with a soft halo pass around it and a touch of hand-drawn jitter, so
the frame reads like a fast marker sketch lit by neon tubes.

Each scene pre-renders a static background once (build) and then draws its
animated layer per frame (draw). Beats are anchored to caption chunks from
build/timeline.json, so picture changes land on the spoken words.
"""
import math

from PIL import Image

from common import (BG_BOT, BG_TOP, BLUE, CREAM, CYAN, DIM, GOLD, GRID, GREEN,
                    MAGENTA, NEON_CYCLE, NEON_RED, PAPER, SKETCH, SS, W, W2,
                    H, H2, WARM, clamp, ease_in, ease_in_out, ease_out,
                    ease_out_back, lerp, ramp, smoothstep)
from stick import (Ctx, face, figure, sparkle, sweat, walk_pose)

# ------------------------------------------------------------ design prompts
# AI animation prompts for Design 02. Same global style block for every
# shot; SCENE_PROMPTS is the per-scene prompt used when a shot is handed to
# a video/image model or to a storyboard reviewer.

DESIGN = "02 — Neon-on-black sketch"

DESIGN_PROMPT = (
    "Neon-on-black sketch animation. Pure near-black background (#04060E to "
    "#0C1020) with a faint construction grid; nothing photographic. All "
    "characters are single-weight stick figures drawn as glowing neon strokes "
    "with a soft bloom halo: ice-white bodies, cyan for the main character, "
    "magenta for everyone else, neon-red reserved for motion lines, X marks "
    "and alerts. Lines are slightly hand-drawn — tiny overshoot and jitter, "
    "never vector-perfect — and boil very gently at 12 fps while the camera "
    "holds a slow 1.02–1.05 push-in. Bold sans-serif labels glow in the same "
    "neon as the object they name. Fast, dry comedic timing: every punchline "
    "lands exactly on its caption chunk with a 0.3 s snap, one idea per shot, "
    "no slow fades."
)

SCENE_PROMPTS = {
    "scroll": (
        "Neon-on-black sketch: on a black grid canvas a cyan stickman stands "
        "bottom-left holding a glowing phone, while three magenta/cyan feed "
        "cards pop in one by one on the right, each with a tiny effortless "
        "vignette (crossing a finish line, coffee walk, mountain peak with "
        "arms up) gliding on smooth loops. On 'always three steps behind' the "
        "cards freeze and neon-red motion lines snap in from the left, "
        "pointing at the cyan figure, who sinks and frowns. Slow push-in."
    ),
    "reel": (
        "Neon-on-black sketch: two neon panels split the black frame — left "
        "'THEIR REEL' in magenta with a smooth glowing curve and a figure "
        "gliding along it trailing gold sparkles; right 'YOUR RAW FOOTAGE' in "
        "cyan with a bumpy path where the figure trips, a red scribble tangle "
        "and impact lines burst. Panels stroke on at the first caption, the "
        "trip snaps on 'your raw footage', sparkles bloom on 'highlight reel'."
    ),
    "edit": (
        "Neon-on-black sketch: a video-edit timeline across a black canvas — "
        "three cyan clip blocks labelled PANIC, RETRIES, 2 AM MELTDOWNS get "
        "struck out one per caption with a neon-red X and sink toward a red "
        "'NEVER POSTED' bin while white draft papers tumble in; then a magenta "
        "'WHAT YOU ACTUALLY SEE' card springs in with a flawless curve and a "
        "gliding figure. Camera shake on each strike."
    ),
    "guess": (
        "Neon-on-black sketch: five ice-white stickmen stand in a row on "
        "black, all shrugging, as coloured question marks pop over their heads "
        "one per word; below, a cyan 'YOUR TIMELINE' scrub bar full of "
        "flickering red glitch blocks that smooth into one clean neon line on "
        "'It's just unedited', labelled NOT LATE — JUST UNEDITED."
    ),
    "next": (
        "Neon-on-black sketch: on the left a cyan-lit page titled YOUR "
        "CHAPTER writes itself line by line; on the right a spinning blue "
        "REFRESHING THEIR LIFE loader freezes and gets a neon-red X on 'stop "
        "refreshing'; then a checkbox labelled THE NEXT SMALL THING springs in "
        "and a thick cyan tick lands with a shake and a sparkle burst on "
        "'today'."
    ),
    "keep": (
        "Neon-on-black sketch: a glowing cyan line climbs steeply across the "
        "black grid while an ice-white stickman walks up it, effort sweat and "
        "neon-red motion lines behind him; a red-outlined camera on a tripod "
        "in the corner gets X'd with NEVER FILMED on 'nobody filmed'; then a "
        "warm horizon glow rises on 'Your turn is coming', the climber reaches "
        "the top, throws his arms up and KEEP GOING blazes in cyan."
    ),
}

# ------------------------------------------------------------------ helpers


def gradient(w, h, top, bottom):
    strip = Image.new("RGB", (1, h))
    px = []
    for i in range(h):
        t = i / max(1, h - 1)
        px.append(tuple(int(top[c] + (bottom[c] - top[c]) * t) for c in range(3)))
    strip.putdata(px)
    return strip.resize((w * SS, h * SS), Image.BILINEAR)


def dark_bg(grid=True, top=BG_TOP, bot=BG_BOT):
    """Black canvas with the faint construction grid of the style."""
    img = Image.new("RGB", (W2, H2))
    img.paste(gradient(W, H, top, bot), (0, 0))
    if grid:
        ctx = Ctx(img)
        for x in range(0, W + 1, 80):
            ctx.line([(x, 0), (x, H)], fill=GRID + (255,), w=1)
        for y in range(0, H + 1, 80):
            ctx.line([(0, y), (W, y)], fill=GRID + (255,), w=1)
    return img


def overlay(base, fn, angle=0.0, scale=1.0):
    """Draw fn (1x coords) on an RGBA layer, optionally rotated/scaled."""
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    fn(Ctx(lay))
    if angle:
        lay = lay.rotate(angle, resample=Image.BICUBIC,
                         center=(base.width / 2, base.height / 2))
    if abs(scale - 1.0) > 0.004:
        lay = lay.resize((max(1, int(base.width * scale)),
                          max(1, int(base.height * scale))), Image.BILINEAR)
    if lay.size != base.size:
        x0 = (lay.width - base.width) // 2
        y0 = (lay.height - base.height) // 2
        if x0 >= 0 and y0 >= 0:
            lay = lay.crop((x0, y0, x0 + base.width, y0 + base.height))
        else:
            padded = Image.new("RGBA", base.size, (0, 0, 0, 0))
            padded.paste(lay, ((base.width - lay.width) // 2,
                               (base.height - lay.height) // 2))
            lay = padded
    base.paste(lay, (0, 0), lay)


def scaled_box(box, s, cx=None, cy=None):
    cx = (box[0] + box[2]) / 2 if cx is None else cx
    cy = (box[1] + box[3]) / 2 if cy is None else cy
    return [cx + (box[0] - cx) * s, cy + (box[1] - cy) * s,
            cx + (box[2] - cx) * s, cy + (box[3] - cy) * s]


def blend_pose(a, b, t):
    t = clamp(t)
    if t <= 0:
        return a
    if t >= 1:
        return b
    out = {}
    for k in a:
        va, vb = a[k], b[k]
        if isinstance(va, tuple):
            out[k] = tuple(lerp(va[i], vb[i], t) for i in range(len(va)))
        else:
            out[k] = [tuple(lerp(va[i][c], vb[i][c], t) for c in range(len(va[i])))
                      for i in range(len(va))]
    return out


def polar(cx, cy, r, deg):
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def sketchy(pts, jit=SKETCH, seed=0.0):
    """Deterministic hand-drawn wobble so strokes look marker-drawn."""
    if not jit:
        return list(pts)
    out = []
    for i, p in enumerate(pts):
        n1 = math.sin(seed * 12.9898 + i * 78.233) * 43758.5453
        n1 = (n1 - math.floor(n1)) - 0.5
        n2 = math.sin(seed * 39.3468 + i * 11.135 + 1.7) * 24634.6345
        n2 = (n2 - math.floor(n2)) - 0.5
        out.append((p[0] + n1 * 2 * jit, p[1] + n2 * 2 * jit))
    return out


def nline(ctx, pts, color, w=6, a=255, halo=3.2, jit=SKETCH, seed=0.0):
    """Neon stroke: two halo passes + a bright core, optional jitter."""
    pts = sketchy(pts, jit, seed) if jit else list(pts)
    c = tuple(color[:3])
    if halo and a > 8:
        ctx.line(pts, fill=c + (int(a * 0.15),), w=w * halo)
        ctx.line(pts, fill=c + (int(a * 0.36),), w=w * 1.9)
    ctx.line(pts, fill=c + (int(a),), w=w)


def ncircle(ctx, c, r, color, w=6, a=255, fill=None, halo=3.2):
    c3 = tuple(color[:3])
    if fill is not None:
        ctx.circle(c, r, fill=tuple(fill[:3]) + (int(a),))
    if halo and a > 8:
        ctx.circle(c, r, outline=c3 + (int(a * 0.16),), w=w * halo)
        ctx.circle(c, r, outline=c3 + (int(a * 0.38),), w=w * 1.9)
    ctx.circle(c, r, outline=c3 + (int(a),), w=w)


def nrrect(ctx, box, r, color, w=6, a=255, fill=None, halo=3.2):
    c3 = tuple(color[:3])
    if fill is not None:
        ctx.rrect(box, r, fill=tuple(fill[:3]) + (int(a),))
    if halo and a > 8:
        ctx.rrect(box, r, outline=c3 + (int(a * 0.16),), w=w * halo)
        ctx.rrect(box, r, outline=c3 + (int(a * 0.38),), w=w * 1.9)
    ctx.rrect(box, r, outline=c3 + (int(a),), w=w)


def ntext(ctx, xy, s, size=30, color=CREAM, a=255, anchor="mm", bold=True,
          halo=2.0):
    """Glowing label: halo stroke pass, then the crisp core."""
    c = tuple(color[:3])
    if a <= 4:
        return
    if halo:
        ctx.text(xy, s, size=size, fill=c + (int(a * 0.30),), anchor=anchor,
                 bold=bold, stroke=halo, stroke_fill=c + (int(a * 0.45),))
    ctx.text(xy, s, size=size, fill=c + (int(a),), anchor=anchor, bold=bold)


def partial_poly(pts, target):
    """First `target` px of a polyline (for drawing strokes on progressively)."""
    out = [pts[0]]
    acc = 0.0
    for i in range(len(pts) - 1):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        seg = math.hypot(bx - ax, by - ay)
        if acc + seg <= target:
            out.append((bx, by))
            acc += seg
        else:
            t = max(0.0, (target - acc) / seg) if seg else 0.0
            out.append((ax + (bx - ax) * t, ay + (by - ay) * t))
            break
    return out


def motion_lines(ctx, cx, cy, ang, n=5, r0=30, r1=110, color=NEON_RED,
                 a=255, spread=90.0, w=6, seed=1.0):
    """Neon-red speed/stress lines radiating from a point."""
    if a <= 6:
        return
    for i in range(n):
        t = (i / max(1, n - 1) - 0.5) * spread
        a0 = math.radians(ang + t)
        j = ((i * 37 + int(seed * 13)) % 7) / 7.0
        rr0 = r0 * (0.7 + 0.6 * j)
        rr1 = rr0 + (r1 - r0) * (0.55 + 0.45 * ((i * 53) % 5) / 5.0)
        p0 = (cx + rr0 * math.cos(a0), cy + rr0 * math.sin(a0))
        p1 = (cx + rr1 * math.cos(a0), cy + rr1 * math.sin(a0))
        nline(ctx, [p0, p1], color, w=w, a=a, jit=0, halo=2.4)


def scribble(ctx, cx, cy, r, color=NEON_RED, a=255, turns=3.0, seed=0.0, w=5):
    """Tangled marker scribble — the 'messy raw footage' mark."""
    if a <= 6:
        return
    pts = []
    n = max(8, int(turns * 12))
    for i in range(n + 1):
        t = i / n
        ang = t * turns * 2 * math.pi + seed
        rr = r * (0.35 + 0.65 * abs(math.sin(t * math.pi * 1.7 + seed)))
        pts.append((cx + rr * math.cos(ang) * 1.15, cy + rr * math.sin(ang) * 0.8))
    nline(ctx, pts, color, w=w, a=a, jit=0, halo=2.6)


def xmark(ctx, box, prog, color=NEON_RED, w=9):
    """Neon-red X, drawn stroke by stroke as prog goes 0 -> 1."""
    if prog <= 0:
        return
    x0, y0, x1, y1 = box
    for k, (ax, ay, bx, by) in enumerate(((x0, y0, x1, y1), (x1, y0, x0, y1))):
        local = clamp((prog - k * 0.45) / 0.55)
        if local <= 0:
            continue
        pts = partial_poly([(ax, ay), (bx, by)],
                           local * math.hypot(bx - ax, by - ay))
        nline(ctx, pts, color, w=w, a=255, jit=0, halo=2.8)


def checkmark(ctx, box, prog, color=CYAN, w=11):
    if prog <= 0:
        return
    x0, y0, x1, y1 = box
    pts = [(x0 + 0.14 * (x1 - x0), y0 + 0.54 * (y1 - y0)),
           (x0 + 0.42 * (x1 - x0), y0 + 0.82 * (y1 - y0)),
           (x1 - 0.04 * (x1 - x0), y0 + 0.16 * (y1 - y0))]
    total = (math.hypot(pts[1][0] - pts[0][0], pts[1][1] - pts[0][1])
             + math.hypot(pts[2][0] - pts[1][0], pts[2][1] - pts[1][1]))
    nline(ctx, partial_poly(pts, clamp(prog) * total), color, w=w,
          a=255, jit=0, halo=2.8)


def person(ctx, x, y, s, pose, color=CREAM, w=6, rot=0.0, **face_kw):
    """Stickman + face in one call; (x, y) is the ground anchor."""
    figure(ctx, x, y, s, pose, w=w, color=color, rot=rot)
    hx, hy, hr = pose["head"]
    face(ctx, (x + hx * s, y + hy * s), hr * s, color=color,
         w=max(2.4, w * 0.62), **face_kw)


# ------------------------------------------------------------------- poses

POSE_PHONE = {                    # standing, phone up in the right hand
    "head": (0, -88, 12),
    "spine": [(0, -76), (0, -44)],
    "armL": [(0, -72), (-14, -58), (-10, -44)],
    "armR": [(0, -72), (16, -64), (22, -52)],
    "legL": [(0, -44), (-13, -22), (-15, 0)],
    "legR": [(0, -44), (13, -22), (15, 0)],
}

POSE_SHRUG = {                     # the shrug everyone is doing
    "head": (0, -88, 12),
    "spine": [(0, -76), (0, -44)],
    "armL": [(0, -72), (-21, -64), (-27, -47)],
    "armR": [(0, -72), (21, -64), (27, -47)],
    "legL": [(0, -44), (-13, -22), (-15, 0)],
    "legR": [(0, -44), (13, -22), (15, 0)],
}

POSE_CHEER = {                     # arms up, made it
    "head": (0, -88, 12),
    "spine": [(0, -76), (0, -44)],
    "armL": [(0, -72), (-19, -87), (-27, -102)],
    "armR": [(0, -72), (19, -87), (27, -102)],
    "legL": [(0, -44), (-13, -22), (-15, 0)],
    "legR": [(0, -44), (13, -22), (15, 0)],
}


def mini_act(ctx, kind, x, y, s, col, t):
    """Tiny 'effortless life' vignette inside a feed card; (x, y) = ground."""
    a = 245
    if kind == 0:                                  # crossing a finish line
        nline(ctx, [(x - 74 * s, y - 74 * s), (x - 74 * s, y)], col, w=4, a=a, jit=1)
        nline(ctx, [(x + 74 * s, y - 74 * s), (x + 74 * s, y)], col, w=4, a=a, jit=1)
        nline(ctx, [(x - 74 * s, y - 74 * s), (x + 74 * s, y - 74 * s)], col,
              w=5, a=a, jit=1)
        ph = (t * 0.7) % 1.0
        person(ctx, x - 36 * s + 72 * s * ph, y, 0.7 * s, walk_pose(ph),
               color=CREAM, w=4, look=(0.5, 0), brow="up", mouth="smile")
    elif kind == 1:                                # coffee walk, zero rush
        ph = (t * 0.5) % 1.0
        p = walk_pose(ph)
        person(ctx, x, y, 0.76 * s, p, color=CREAM, w=4,
               look=(0.4, 0), brow="flat", mouth="smile")
        hx, hy = p["armR"][-1]
        ctx.dot((x + hx * 0.76 * s, y + hy * 0.76 * s - 7 * s), 9 * s,
                fill=WARM + (a,))
    else:                                           # peak, arms up
        ctx.poly([(x - 84 * s, y), (x, y - 54 * s), (x + 84 * s, y)],
                 fill=(18, 24, 42, 255))
        nline(ctx, [(x - 84 * s, y), (x, y - 54 * s), (x + 84 * s, y)], col,
              w=4, a=a, jit=1)
        person(ctx, x, y - 54 * s, 0.5 * s, POSE_CHEER, color=CREAM, w=4,
               brow="up", mouth="smile")


# ------------------------------------------------------------------ base


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

    def line_end(self, i):
        return self.tl["lines"][i]["end"] - self.t0

    def build(self):
        pass

    def draw(self, ctx, lt):        # lt = seconds since scene start
        pass

    def shake(self, lt):
        return (0.0, 0.0)

    def zoom(self, lt):
        p = clamp(lt / max(0.5, self.t1 - self.t0))
        a, b = self.zoom_range
        return lerp(a, b, smoothstep(p))


# ------------------------------------------------------------------ 1: scroll


class ScrollScene(Scene):
    id = "scroll"
    CARDS = ((596, 54, 906, 246), (934, 150, 1244, 342), (654, 356, 964, 548))
    TAGS = ("THE PROMOTION", "THE TRIP", "THE GLOW-UP")

    def build(self):
        self.bg = dark_bg()

    def draw(self, ctx, lt):
        b = [self.beat(0, k) for k in range(4)]
        feed_a = int(255 * ramp(lt, b[0], b[0] + 0.4))
        ntext(ctx, (336, 64), "EVERYONE ELSE'S FEED", size=22, color=DIM,
              a=feed_a)

        # three effortless cards, popping in one caption at a time
        for i, box in enumerate(self.CARDS):
            t0 = b[1] + i * 0.30
            s = ramp(lt, t0, t0 + 0.42)
            if s <= 0:
                continue
            sc = lerp(0.74, 1.0, ease_out_back(s))
            bx = scaled_box(box, sc)
            col = (CYAN, MAGENTA, WARM)[i]
            a = int(255 * clamp(s * 2.2))
            ctx.rrect(bx, 16, fill=PAPER + (int(225 * s),))
            ctx.rrect(bx, 16, outline=col + (a,), w=5)
            ntext(ctx, ((bx[0] + bx[2]) / 2, bx[1] + 26), self.TAGS[i],
                  size=20, color=col, a=a)
            mini_act(ctx, i, (bx[0] + bx[2]) / 2, bx[3] - 26, sc, col, lt)

        # you, bottom left, phone in hand
        sink = 10 * ease_out(ramp(lt, b[3], b[3] + 0.5))
        x, y, s = 268.0, 634.0, 2.6
        px, py = x + 22 * s, y - 52 * s
        ctx.glow((px, py - 4), 40, CYAN, alpha=int(70 * feed_a / 255), rings=4)
        person(ctx, x, y - sink, s, POSE_PHONE, color=CYAN, w=7,
               look=(0.55, -0.55),
               brow=("sad" if lt >= b[3] else "up"),
               mouth=("frown" if lt >= b[3] else "flat"))
        ctx.rrect([px - 9, py - 15, px + 9, py + 7], 4, fill=(6, 20, 34, 255),
                  outline=CYAN + (235,), w=3)

        # "always three steps behind" -> neon-red motion lines snap in
        p = ramp(lt, b[3], b[3] + 0.45)
        if p > 0:
            motion_lines(ctx, 44, 330, 0, n=5, r0=8, r1=96, a=int(235 * p),
                         spread=110, w=6, seed=2)
            for k in range(3):                      # three chevrons
                q = ramp(lt, b[3] + 0.1 + k * 0.14, b[3] + 0.3 + k * 0.14)
                if q <= 0:
                    continue
                cx = 118 + k * 46
                nline(ctx, [(cx, 292), (cx + 26 * q, 330), (cx, 368)],
                      NEON_RED, w=6, a=int(240 * q), jit=0, halo=2.6)
            ntext(ctx, (176, 556), "3 STEPS BEHIND", size=24, color=NEON_RED,
                  a=int(255 * p))

        if lt >= b[2]:                     # worried blink of the feed glow
            ctx.glow((268, 470), 120, CYAN, alpha=18, rings=4)


# ------------------------------------------------------------------ 2: reel


class ReelScene(Scene):
    id = "reel"
    LEFT = (66, 96, 620, 574)
    RIGHT = (660, 96, 1214, 574)

    def build(self):
        self.bg = dark_bg()

    def draw(self, ctx, lt):
        b0, b1, b2 = self.beat(1, 0), self.beat(1, 1), self.beat(1, 2)
        app = ramp(lt, b0, b0 + 0.45)
        if app <= 0:
            return
        A = int(255 * app)
        end = self.line_end(1) + 0.9

        for box, col, tag in ((self.LEFT, MAGENTA, "THEIR REEL"),
                              (self.RIGHT, CYAN, "YOUR RAW FOOTAGE")):
            ctx.rrect(list(box), 18, fill=PAPER + (int(218 * app),))
            ctx.rrect(list(box), 18, outline=col + (A,), w=5)
            ntext(ctx, ((box[0] + box[2]) / 2, box[1] + 32), tag, size=24,
                  color=col, a=A)

        base = (self.LEFT[1] + self.LEFT[3]) / 2 + 46
        span = (self.LEFT[2] - self.LEFT[0] - 92)

        # their reel: one smooth curve, a figure gliding along it
        curve = [(self.LEFT[0] + 46 + i * span / 48,
                  base - 74 * math.sin(i / 48 * math.pi)) for i in range(49)]
        nline(ctx, curve, MAGENTA, w=6, a=A, jit=0, halo=2.6, seed=3)
        u = ease_in_out(ramp(lt, b0 + 0.3, end))
        fi = min(48, max(0, int(u * 48)))
        fx, fy = curve[fi]
        person(ctx, fx, fy, 1.35, walk_pose((lt * 0.6) % 1.0), color=CREAM,
               w=5, look=(0.5, 0), brow="up", mouth="smile")
        if lt >= b2:                                # highlight sparkles
            aa = int(230 * clamp((lt - b2) / 0.4))
            for k in range(6):
                sp = polar(fx, fy - 54, 30 + 12 * ((k * 13) % 24) / 24.0 * 3,
                           k * 60 + lt * 40)
                sparkle(ctx, sp, 8, color=GOLD + (aa,))

        # your raw footage: bumpy path, then the trip
        rpath = [(self.RIGHT[0] + 46 + i * span / 48,
                  base + 30 - 52 * math.sin(i / 48 * math.pi)) for i in range(49)]
        nline(ctx, rpath, CYAN, w=6, a=A, jit=0, halo=2.6, seed=5)
        rx = self.RIGHT[0] + 46 + span * 0.66
        ry = base - 8
        trip = ease_out(ramp(lt, b1, b1 + 0.5))
        person(ctx, rx - 46 * trip, ry + 16 * trip, 1.35,
               walk_pose((lt * 0.6) % 1.0), color=CREAM, w=5, rot=-0.55 * trip,
               look=(0.4, 0.2), brow=("sad" if trip > 0.4 else "up"),
               mouth=("grimace" if trip > 0.4 else "flat"))
        if trip > 0:
            scribble(ctx, rx + 18, ry + 4, 34, NEON_RED,
                     a=int(235 * trip), turns=2.6, seed=1.3, w=5)
            motion_lines(ctx, rx + 18, ry, -30, n=6, r0=34, r1=78,
                         a=int(225 * trip), spread=330, w=5, seed=4)
            if trip > 0.5:
                sweat(ctx, (rx - 74, ry - 78), 22, color=CYAN)

        # panel divider snaps down on the first word
        d = ramp(lt, b0 + 0.15, b0 + 0.55)
        if d > 0:
            nline(ctx, [(640, 116), (640, 116 + 440 * d)], CREAM, w=5,
                  a=int(220 * d), jit=0, halo=2.4)

    def shake(self, lt):
        d = lt - (self.beat(1, 1) + 0.12)
        if 0 <= d < 0.35:
            a = 6 * (1 - d / 0.35)
            return (a * math.sin(lt * 70), a * 0.5 * math.cos(lt * 61))
        return (0.0, 0.0)


# ------------------------------------------------------------------ 3: edit


class EditScene(Scene):
    id = "edit"
    CLIPS = (("PANIC", 90, 380), ("RETRIES", 400, 700),
             ("2 AM MELTDOWNS", 720, 1060))
    BIN = (90, 452, 700, 604)
    SEEN = (760, 452, 1190, 604)

    def build(self):
        self.bg = dark_bg()

    def draw(self, ctx, lt):
        hits = (self.beat(2, 0), self.beat(2, 1), self.beat(2, 2))
        b30, b31 = self.beat(3, 0), self.beat(3, 1)

        ntext(ctx, (172, 150), "RAW FOOTAGE", size=24, color=DIM,
              a=int(255 * ramp(lt, hits[0] - 0.35, hits[0] + 0.05)))
        nline(ctx, [(70, 336), (1210, 336)], DIM, w=4, a=230, jit=1, halo=1.8)

        # three clips, struck out one caption at a time
        for i, (name, x0, x1) in enumerate(self.CLIPS):
            xp = ramp(lt, hits[i] + 0.05, hits[i] + 0.45)
            a = int(255 * (1 - 0.55 * xp))
            box = [x0, 214 + 16 * xp, x1, 320]
            ctx.rrect(box, 12, fill=PAPER + (int(255 * (1 - 0.4 * xp)),))
            ctx.rrect(box, 12, outline=CYAN + (a,), w=4)
            if xp > 0:
                xmark(ctx, [x0 + 18, box[1] + 10, x1 - 18, box[3] - 10], xp, w=8)
            ntext(ctx, ((x0 + x1) / 2, (box[1] + box[3]) / 2), name, size=26,
                  color=CREAM, a=a)

        # the bin nothing ever posts into
        bp = ramp(lt, hits[0], hits[0] + 0.4)
        if bp > 0:
            nrrect(ctx, self.BIN, 14, NEON_RED, w=5, a=int(255 * bp),
                   fill=(24, 8, 12))
            ntext(ctx, ((self.BIN[0] + self.BIN[2]) / 2, self.BIN[1] - 24),
                  "NEVER POSTED", size=26, color=NEON_RED, a=int(255 * bp))

        # failed drafts tumble into the bin and stay there
        drafts = [b30 + i * 0.30 for i in range(3)] + [b31 + 0.15]
        for i, t0 in enumerate(drafts):
            p = ramp(lt, t0, t0 + 0.75)
            if p <= 0:
                continue
            a = 255
            y = lerp(40, 528, ease_in(p))
            x = 168 + i * 148 + 18 * math.sin(p * 6 + i)
            ctx.rrect([x - 34, y - 44, x + 34, y + 44], 6,
                      fill=(238, 242, 250, a))
            for k in range(4):
                ctx.line([(x - 24, y - 24 + k * 15), (x + 24, y - 24 + k * 15)],
                         fill=(70, 82, 104, a), w=3)
            if i == 3:
                ntext(ctx, (x, y), "4th TRY", size=18, color=(30, 36, 54),
                      a=a, halo=0)
            else:
                scribble(ctx, x, y + 6, 18, NEON_RED, a=int(a * 0.9),
                         turns=1.6, seed=i * 2.1, w=3)

        # what is actually posted: a flawless little reel
        s31 = ramp(lt, b31 + 0.15, b31 + 0.6)
        if s31 > 0:
            sc = lerp(0.8, 1.0, ease_out_back(s31))
            box = scaled_box(self.SEEN, sc)
            a = int(255 * clamp(s31 * 2.0))
            ctx.rrect(box, 16, fill=PAPER + (int(225 * s31),))
            ctx.rrect(box, 16, outline=MAGENTA + (a,), w=5)
            ntext(ctx, ((box[0] + box[2]) / 2, box[1] + 26),
                  "WHAT YOU ACTUALLY SEE", size=22, color=MAGENTA, a=a)
            cx0, cx1 = box[0] + 40, box[2] - 40
            cy = box[3] - 26
            pts = [(cx0 + i * (cx1 - cx0) / 32,
                    cy - 24 * math.sin(i / 32 * math.pi)) for i in range(33)]
            nline(ctx, pts, MAGENTA, w=5, a=a, jit=0, halo=2.6, seed=7)
            u = ease_in_out((lt * 0.35) % 1.0)
            fi = min(32, max(0, int(u * 32)))
            person(ctx, pts[fi][0], pts[fi][1], 0.7, walk_pose((lt * 0.7) % 1.0),
                   color=CREAM, w=4, look=(0.5, 0), brow="up", mouth="smile")

    def shake(self, lt):
        amp = 0.0
        for b in (self.beat(2, 0), self.beat(2, 1), self.beat(2, 2),
                  self.beat(3, 1) + 0.15):
            d = lt - b
            if 0 <= d < 0.32:
                amp = max(amp, 7 * (1 - d / 0.32))
        if amp <= 0:
            return (0.0, 0.0)
        return (amp * math.sin(lt * 74), amp * 0.6 * math.cos(lt * 61))


# ------------------------------------------------------------------ 4: guess


class GuessScene(Scene):
    id = "guess"
    BAR = (110, 486, 1170, 560)

    def build(self):
        self.bg = dark_bg()

    def draw(self, ctx, lt):
        c0, c1, c2 = self.beat(4, 0), self.beat(4, 1), self.beat(4, 2)
        d0, d1 = self.beat(5, 0), self.beat(5, 1)

        ntext(ctx, (640, 92), "BEHIND THE SCENES", size=30, color=DIM,
              a=int(255 * ramp(lt, c0, c0 + 0.4)))
        nline(ctx, [(430, 122), (850, 122)], DIM, w=3,
              a=int(200 * ramp(lt, c0, c0 + 0.5)), jit=2, halo=1.6)

        # a row of people, all doing the same shrug
        for i in range(5):
            x = 176 + i * 232
            born = c1 + i * 0.16
            v = ramp(lt, born, born + 0.35)
            if v <= 0:
                continue
            bob = 3.0 * math.sin(lt * 2.4 + i)
            person(ctx, x, 430 + bob, 1.7, POSE_SHRUG, color=CREAM, w=6,
                   look=(0, -0.4), brow="up", mouth="flat")
            q = ease_out_back(ramp(lt, born + 0.18, born + 0.48))
            if q > 0.12:
                ntext(ctx, (x + 44, 232 - 14 * (1 - q)), "?",
                      size=int(round(52 * q)), color=NEON_CYCLE[i % 5],
                      a=int(255 * clamp(q)))

        # your timeline scrub bar
        bp = ramp(lt, d0, d0 + 0.5)
        if bp > 0:
            nrrect(ctx, self.BAR, 14, CYAN, w=4, a=int(255 * bp), fill=PAPER)
            ntext(ctx, (self.BAR[0] + 150, self.BAR[1] + 18),
                  "YOUR TIMELINE", size=22, color=CYAN, a=int(255 * bp))

        fix = ramp(lt, d1, d1 + 0.9)
        if bp > 0:
            for i in range(6):
                x0 = self.BAR[0] + 20 + i * 176
                wdt = 152 * (1 - 0.86 * fix)
                if wdt < 8:
                    continue
                flick = (0.55 + 0.45 * math.sin(lt * 7.5 + i * 2.1)
                         if fix < 0.4 else 1.0 - fix)
                col = NEON_RED if i % 2 else MAGENTA
                ctx.rrect([x0, 518, x0 + wdt, 546], 6,
                          fill=col + (int(235 * clamp(flick) * bp),))
        if fix > 0.25:
            nline(ctx, [(self.BAR[0] + 20, 532), (self.BAR[2] - 24, 532)],
                  CYAN, w=7, a=int(255 * ramp(fix, 0.25, 1)), jit=0, halo=3)
        if lt >= d1:
            ntext(ctx, (640, 462), "NOT LATE — JUST UNEDITED", size=26,
                  color=GREEN, a=int(255 * ramp(lt, d1, d1 + 0.4)))

        if lt >= c2:                 # a nervous beat of collective guessing
            for i in range(5):
                x = 176 + i * 232
                ctx.glow((x, 330), 70, NEON_CYCLE[i % 5], alpha=14, rings=4)


# ------------------------------------------------------------------ 5: next


class NextScene(Scene):
    id = "next"
    PAGE = (70, 84, 610, 566)
    LOADER = (930, 214, 78)
    BOX = (846, 430, 1024, 556)

    def build(self):
        self.bg = dark_bg()

    def draw(self, ctx, lt):
        c0, c1 = self.beat(6, 0), self.beat(6, 1)
        d0, d1 = self.beat(7, 0), self.beat(7, 1)

        # your chapter, writing itself line by line
        pa = ramp(lt, c0 - 0.4, c0)
        if pa > 0:
            nrrect(ctx, self.PAGE, 16, CYAN, w=4, a=int(255 * pa), fill=PAPER)
            ntext(ctx, ((self.PAGE[0] + self.PAGE[2]) / 2, self.PAGE[1] + 34),
                  "YOUR CHAPTER", size=26, color=CYAN, a=int(255 * pa))
            widths = (430, 372, 452, 300, 410, 356, 448, 262, 392)
            pace = 0.30 if lt < c0 else 0.17
            for i, wd in enumerate(widths):
                t0 = c0 - 0.6 + i * pace
                p = ramp(lt, t0, t0 + 0.26)
                if p <= 0:
                    continue
                y = self.PAGE[1] + 96 + i * 44
                x0 = self.PAGE[0] + 44
                nline(ctx, [(x0, y), (x0 + wd * p, y)], CREAM, w=6,
                      a=int(255 * pa), jit=1, seed=i * 3.3, halo=2.4)
                if 0.98 < p < 1.0 or (i == int((lt - (c0 - 0.6)) / pace)
                                      and lt >= c0 - 0.6):
                    caret = 200 if int(lt * 3) % 2 else 60
                    ctx.line([(x0 + wd * p + 8, y - 16), (x0 + wd * p + 8, y + 16)],
                             fill=CYAN + (caret,), w=4)

        # the refresh loop, frozen and X'd (the loader keeps spinning until caught)
        lx, ly, lr = self.LOADER
        spin = (lt * 230) % 360 if lt < c0 else (c0 * 230) % 360
        la = int(255 * ramp(lt, c0 - 0.3, c0 + 0.1))
        for k in range(3):
            a0 = spin + k * 120
            ctx.arc([lx - lr, ly - lr, lx + lr, ly + lr], a0, a0 + 78,
                    fill=BLUE + (int(la * 0.25),), w=16)
            ctx.arc([lx - lr, ly - lr, lx + lr, ly + lr], a0, a0 + 78,
                    fill=BLUE + (la,), w=8)
        ntext(ctx, (lx, ly + lr + 44), "REFRESHING THEIR LIFE", size=22,
              color=BLUE, a=la)
        p = ramp(lt, c0 + 0.1, c0 + 0.4)
        if p > 0:
            xmark(ctx, [lx - lr, ly - lr, lx + lr, ly + lr], p, w=12)
            ntext(ctx, (lx, ly + lr + 84), "STILL THEIR STORY", size=20,
                  color=NEON_RED, a=int(255 * p))

        # the next small thing: one checkbox, one tick
        bp = ramp(lt, d0 - 0.1, d0 + 0.3)
        if bp > 0:
            sc = lerp(0.7, 1.0, ease_out_back(bp))
            box = scaled_box(self.BOX, sc)
            ntext(ctx, ((box[0] + box[2]) / 2, box[1] - 34),
                  "THE NEXT SMALL THING", size=22, color=GREEN,
                  a=int(255 * bp))
            nrrect(ctx, box, 14, GREEN, w=6, a=int(255 * bp), fill=PAPER)
            tick = ramp(lt, d0 + 0.12, d0 + 0.5)
            checkmark(ctx, [box[0] + 22, box[1] + 16, box[2] - 22, box[3] - 16],
                      tick, color=CYAN, w=12)
            if tick >= 1:
                br = 1 + 0.05 * math.sin(clamp((lt - d0 - 0.5) * 6) * math.pi)
                ctx.glow(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2),
                         120 * br, CYAN, alpha=34, rings=4)

        if lt >= d1:                 # "today." -> sparkle burst
            pr = ramp(lt, d1, d1 + 0.9)
            if 0 < pr < 1:
                for k in range(8):
                    sp = polar(935, 493, 40 + 90 * pr, k * 45 + 22)
                    sparkle(ctx, sp, 11 - 7 * pr, color=GOLD +
                            (int(235 * (1 - pr)),))
                ntext(ctx, (1150, 470), "TODAY", size=26, color=WARM,
                      a=int(255 * (1 - pr)))

    def shake(self, lt):
        d = lt - (self.beat(7, 0) + 0.12)
        if 0 <= d < 0.32:
            a = 8 * (1 - d / 0.32)
            return (a * math.sin(lt * 78), a * 0.55 * math.cos(lt * 66))
        return (0.0, 0.0)


# ------------------------------------------------------------------ 6: keep


class KeepScene(Scene):
    id = "keep"
    zoom_range = (1.02, 1.06)

    @staticmethod
    def path():
        pts = []
        for i in range(61):
            t = i / 60
            x = 120 + 1040 * t
            y = 575 - 335 * (t ** 1.4) + 14 * math.sin(t * 8.5)
            pts.append((x, y))
        return pts

    def build(self):
        self.bg = dark_bg()

    def draw(self, ctx, lt):
        b80, b81 = self.beat(8, 0), self.beat(8, 1)
        b90, b91 = self.beat(9, 0), self.beat(9, 1)
        pts = self.path()
        glow_a = int(250 * ramp(lt, b80 - 0.3, b80 + 0.3))
        nline(ctx, pts, CYAN, w=8, a=max(60, glow_a), jit=1, seed=4, halo=3.4)

        # the effort itself: sweat + neon-red motion lines behind the climber
        u = ease_in_out(ramp(lt, b80 - 0.6, b90 + 1.4))
        i = min(59, max(0, int(u * 59)))
        cx, cy = pts[i]
        nx, ny = pts[min(60, i + 1)]
        rot = math.atan2(ny - cy, nx - cx)
        if lt >= b91 - 0.05 and u > 0.94:
            person(ctx, cx, cy, 2.0, POSE_CHEER, color=CREAM, w=7,
                   brow="up", mouth="smile")
        else:
            person(ctx, cx, cy, 2.0, walk_pose((lt * 0.85) % 1.0),
                   color=CREAM, w=7, rot=rot,
                   look=(0.5, -0.3), brow="sad", mouth="grimace")
            sweat(ctx, (cx + 40, cy - 202), 22, color=CYAN)
            motion_lines(ctx, cx - 36, cy - 116, 168, n=4, r0=18, r1=66,
                         a=int(210 * ramp(lt, b80, b80 + 0.4)), spread=70,
                         w=5, seed=6)

        # a camera that never recorded any of it (top-left, clear of the path)
        camx, camy = 176, 176
        ca = int(255 * ramp(lt, b80 - 0.5, b80))
        ctx.rrect([camx - 58, camy - 40, camx + 34, camy + 30], 8,
                  fill=PAPER + (int(230 * ca / 255),),
                  outline=NEON_RED + (ca,), w=5)
        ncircle(ctx, (camx + 46, camy - 4), 26, NEON_RED, w=5, a=ca,
                fill=(8, 12, 22))
        ncircle(ctx, (camx + 46, camy - 4), 11, CYAN, w=4, a=ca)
        nline(ctx, [(camx - 12, camy + 30), (camx - 52, camy + 150)], CREAM,
              w=6, a=ca, jit=1)
        nline(ctx, [(camx - 12, camy + 30), (camx + 28, camy + 150)], CREAM,
              w=6, a=ca, jit=1)
        nline(ctx, [(camx - 12, camy + 30), (camx - 12, camy + 104)], CREAM,
              w=6, a=ca, jit=1)
        ntext(ctx, (camx - 12, camy - 74), "REC", size=24, color=NEON_RED, a=ca)
        if lt >= b81:
            p = ramp(lt, b81, b81 + 0.4)
            xmark(ctx, [camx - 66, camy - 48, camx + 76, camy + 40], p, w=10)
            ntext(ctx, (camx - 12, camy + 186), "NEVER FILMED", size=22,
                  color=NEON_RED, a=int(255 * p))

        # "Your turn is coming." -> warm horizon glow, arrow at the line's end
        hz = ramp(lt, b90, b90 + 1.1)
        if hz > 0:
            ctx.glow((1150, 470), 290, WARM, alpha=int(40 * hz), rings=8)
            nline(ctx, [(860, 600), (1256, 600)], WARM, w=5,
                  a=int(210 * hz), jit=2)
            tip = pts[60]
            ah = ramp(lt, b90 + 0.3, b90 + 0.8)
            if ah > 0:
                nline(ctx, [(tip[0] - 46 * ah, tip[1] - 20 * ah),
                            (tip[0] + 4, tip[1] + 4)],
                      CYAN, w=8, a=int(255 * ah), jit=0, halo=3)
                nline(ctx, [(tip[0] - 46 * ah, tip[1] + 24 * ah),
                            (tip[0] + 4, tip[1] + 4)],
                      CYAN, w=8, a=int(255 * ah), jit=0, halo=3)

        # "Keep going."
        if lt >= b91:
            p = ramp(lt, b91, b91 + 0.5)
            sc = lerp(0.7, 1.0, ease_out_back(p))
            ntext(ctx, (486, 126), "KEEP GOING", size=int(46 * sc),
                  color=CYAN, a=int(255 * p))
            if p > 0.5:
                for k in range(5):
                    sp = polar(486, 126, 138, k * 72 + lt * 30)
                    sparkle(ctx, sp, 9, color=GOLD +
                            (int(220 * (p - 0.5) * 2),))

    def shake(self, lt):
        d = lt - (self.beat(9, 1) + 0.1)
        if 0 <= d < 0.4:
            a = 5 * (1 - d / 0.4)
            return (a * math.sin(lt * 66), a * 0.5 * math.cos(lt * 58))
        return (0.0, 0.0)


# ------------------------------------------------------------------ registry

SCENES = {cls.id: cls for cls in
          (ScrollScene, ReelScene, EditScene, GuessScene, NextScene, KeepScene)}
