"""The five scenes of the "pause time" episode — Design 02.

Style: **Neon-on-black sketch**, with a richer set-dressing pass. Every scene
starts on the same near-black canvas, but the rooms are built out of dim steel
architecture, glass, night windows and warm practicals so the café, conference
room, barbershop and staff party read as real places. The hero and the freeze
cues stay in bright neon on top, with a dark separation stroke behind the
figure so nothing gets lost against the detail.

The world freezes on command. `pause_badge`, `freeze_ripple`, `freeze_frame`
and `frozen_clock` are shared cues: a 10.0 -> 0.0 countdown ring, suspended
coffee, frosted frame edges and a hard click when the world unpauses.

Each scene bakes its detailed room once in build() and draws only the moving
layers per frame.
"""
import math

from PIL import Image

from common import (AMBER, BG_BOT, BG_TOP, BLUE, CHALK, CREAM, CYAN, DIM, GLASS,
                    GOLD, GRID, GREEN, INK, MAGENTA, NEON_RED, PAPER, SKETCH,
                    SS, STEEL, STEEL_DIM, W, W2, H, H2, WARM, clamp, dim,
                    ease_in, ease_in_out, ease_out, ease_out_back,
                    frozen_clock, lerp, mix, pulse, ramp, rgba, smoothstep)
from stick import (Ctx, POSE_SIT, POSE_STAND, face, figure, sparkle, sweat,
                   walk_pose)

# ------------------------------------------------------------ design prompts

DESIGN = "02 — Neon-on-black sketch, detailed rooms"

DESIGN_PROMPT = (
    "Neon-on-black sketch animation with detailed neon set dressing. Pure "
    "near-black canvas; rooms drawn in muted steel, glass and amber practicals "
    "so they read as real cafés, meeting rooms and barbershops without "
    "competing with the characters. All people are single-weight stick figures "
    "in glowing ice-white/cyan strokes with a soft bloom. Neon-red is reserved "
    "for freeze ripples, motion lines and alerts. Every environment has clear "
    "architecture: brick, windows, pendant lamps, counters, chairs, signage. "
    "When time pauses, the frame frosts at the edges, a 10-second ring appears, "
    "and splashes hang in mid-air. The hero stays bright cyan and is separated "
    "from the background by a faint dark stroke. Dry, fast comedic timing."
)

SCENE_PROMPTS = {
    "spill": (
        "Neon-on-black café: a cyan stickman fumbles a takeaway cup over a "
        "detailed counter with espresso machine, pastry dome, menu board and a "
        "night-city window; the cup tips, coffee hangs mid-splash, a 10-second "
        "freeze ring snaps in and the whole room frosts."
    ),
    "pose": (
        "Same frozen café, now a photoshoot: the cyan hero ignores the hanging "
        "spill and strikes a model pose, chin up, one hand on the counter, as a "
        "FLAWLESS label and camera sparkles pop around him; the barista and "
        "customers stay frozen mid-step behind him."
    ),
    "fixes": (
        "Neon-on-black split screen: a wrong meeting freezes mid-presentation "
        "and the slide swaps to cat photos; a bad haircut freezes with the "
        "scissors in mid-air and the customer backs out of the barbershop; a "
        "10-second tick strip lands underneath."
    ),
    "resume": (
        "Back in the café: the freeze ring hits zero, frost shatters, the clock "
        "clicks and the coffee cup finishes its fall with a splash while the "
        "hero freezes into an innocent hand-on-counter pose and every customer "
        "happens to be looking at a phone."
    ),
    "camera": (
        "Neon-on-black café staff party: a security camera in the corner beams "
        "down while its monitor replays the hero's frozen poses, wrong meeting "
        "and barber escape at 1.0x; staff in party hats gather around the screen "
        "and laugh while the hero dies inside."
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
    c = tuple(color[:3])
    if a <= 4:
        return
    if halo:
        ctx.text(xy, s, size=size, fill=c + (int(a * 0.30),), anchor=anchor,
                 bold=bold, stroke=halo, stroke_fill=c + (int(a * 0.45),))
    ctx.text(xy, s, size=size, fill=c + (int(a),), anchor=anchor, bold=bold)


def partial_poly(pts, target):
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


def person(ctx, x, y, s, pose, color=CREAM, w=6, rot=0.0, outline=True,
           **face_kw):
    """Stickman + face, with a dark separation stroke for busy backgrounds."""
    if outline:
        figure(ctx, x, y, s, pose, w=w + 5.0, color=(2, 5, 12), rot=rot)
    figure(ctx, x, y, s, pose, w=w, color=color, rot=rot)
    hx, hy, hr = pose["head"]
    c, sa = math.cos(rot), math.sin(rot)
    hcx = x + (hx * c - hy * sa) * s
    hcy = y + (hx * sa + hy * c) * s
    if outline:
        face(ctx, (hcx, hcy), hr * s, color=(2, 5, 12),
             w=max(4.0, w * 1.25), **face_kw)
    face(ctx, (hcx, hcy), hr * s, color=color, w=max(2.4, w * 0.62), **face_kw)


# --------------------------------------------------------- detailed rooms


def city_skyline(ctx, box, a=255, seed=1.0):
    """Deterministic night skyline inside a window box."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    ctx.rrect(box, 3, fill=(5, 12, 26, a))
    moonx = x0 + w * 0.76
    moony = y0 + h * 0.23
    ctx.circle((moonx, moony), 15, fill=(236, 246, 255, int(a * 0.55)))
    for i in range(9):
        bx = x0 + (i + 0.25) * w / 9.0
        bw = w / 9.0 * (0.72 + 0.25 * ((i * 7) % 5) / 5.0)
        bh = h * (0.18 + 0.42 * ((i * 13 + int(seed * 9)) % 11) / 11.0)
        by = y1 - bh
        col = mix((6, 14, 28), STEEL_DIM, 0.42 + 0.25 * ((i * 3) % 4) / 4.0)
        ctx.rrect([bx, by, bx + bw, y1], 1, fill=col + (a,))
        for r in range(4):
            wy = by + 12 + r * 18
            if wy > y1 - 10:
                break
            for c in range(2):
                wx = bx + 8 + c * (bw * 0.38)
                if wx + 5 > bx + bw:
                    continue
                lit = ((i * 5 + r * 3 + c) % 4) == 0
                ctx.rrect([wx, wy, wx + 5, wy + 7], 1,
                          fill=(AMBER if lit else (18, 30, 48)) + (a,))
    # street haze / traffic
    nline(ctx, [(x0 + 6, y1 - 26), (x1 - 6, y1 - 26)], AMBER, w=2,
          a=int(a * 0.28), jit=0, halo=1.8)
    for i in range(5):
        px = x0 + 14 + i * (w - 28) / 4.0
        nline(ctx, [(px, y1 - 20), (px + 5, y1 - 20)], NEON_RED, w=2,
              a=int(a * 0.55), jit=0, halo=1.6)


def window_pane(ctx, box, a=255, seed=1.0):
    x0, y0, x1, y1 = box
    ctx.rrect(box, 8, fill=GLASS + (a,), outline=STEEL + (a,), w=4)
    city_skyline(ctx, [x0 + 10, y0 + 10, x1 - 10, y1 - 12], a=int(a * 0.9),
                 seed=seed)
    mx = (x0 + x1) / 2
    my = (y0 + y1) / 2
    nline(ctx, [(mx, y0 + 8), (mx, y1 - 8)], STEEL, w=3, a=a, jit=0, halo=1.5)
    nline(ctx, [(x0 + 8, my), (x1 - 8, my)], STEEL, w=3, a=a, jit=0, halo=1.5)
    # reflection slash
    nline(ctx, [(x0 + 22, y1 - 24), (x0 + 92, y0 + 26)], CHALK, w=1.5,
          a=int(a * 0.35), jit=0, halo=0)


def brick_wall(ctx, box, a=255, step=44, seed=0.0):
    x0, y0, x1, y1 = box
    for row, y in enumerate(range(int(y0), int(y1), step)):
        off = 0 if row % 2 == 0 else step // 2
        nline(ctx, [(x0, y), (x1, y)], STEEL_DIM, w=1.4,
              a=int(a * 0.42), jit=0, halo=0)
        for x in range(int(x0 - step + off), int(x1), step * 2):
            nline(ctx, [(x, y), (x, min(y1, y + step))], STEEL_DIM, w=1.2,
                  a=int(a * 0.30), jit=0, halo=0)


_CAFE_CACHE = None


def cafe_bg():
    """Baked café: night window, shelves, menu, counter, espresso machine."""
    global _CAFE_CACHE
    if _CAFE_CACHE is not None:
        return _CAFE_CACHE
    img = dark_bg()
    c = Ctx(img)

    # ceiling + wall seams
    c.rrect([0, 0, W, 118], 0, fill=(5, 8, 18, 255))
    nline(c, [(0, 118), (W, 118)], STEEL_DIM, w=3.5, a=220, jit=0, halo=1.8)
    for x in range(70, W, 155):
        nline(c, [(x, 0), (x, 112)], STEEL_DIM, w=1.2, a=70, jit=0, halo=0)
    brick_wall(c, [0, 150, W, 456], a=160, step=48)
    nline(c, [(0, 454), (W, 454)], STEEL, w=4, a=170, jit=1, halo=1.6)

    # big night window, left
    window_pane(c, [64, 176, 374, 446], a=255, seed=3.0)
    # hanging OPEN sign inside the window
    nrrect(c, [88, 300, 166, 350], 5, AMBER, w=3, a=210, fill=(28, 20, 12))
    ntext(c, (127, 325), "OPEN", size=17, color=AMBER, a=230)

    # shelves of cups and jars
    nrrect(c, [408, 178, 652, 404], 14, STEEL, w=4, a=185,
           fill=(8, 12, 24))
    for sy in (244, 306, 368):
        nline(c, [(424, sy), (636, sy)], STEEL, w=4, a=195, jit=0, halo=1.5)
    jars = ((432, 224, 18, 38, AMBER), (470, 214, 24, 22, GOLD),
            (512, 228, 20, 40, WARM), (560, 220, 27, 28, CHALK),
            (612, 232, 20, 36, STEEL))
    for jx, jy, jw, jh, col in jars:
        c.rrect([jx, jy, jx + jw, jy + jh], 5, fill=dim(col, 0.28) + (255,),
                outline=col + (190,), w=2)
        c.rrect([jx + 3, jy - 5, jx + jw - 3, jy + 1], 2,
                fill=STEEL_DIM + (255,))
    for i, sx in enumerate((432, 470, 510, 552, 596)):
        c.rrect([sx, 338, sx + 28, 362], 4, fill=(12, 18, 30, 255),
                outline=CHALK + (155,), w=2)
        c.arc([sx + 7, 342, sx + 20, 354], 0, 180, fill=CHALK + (130,), w=2)
    ntext(c, (530, 194), "SHELF 03", size=12, color=DIM, a=180)

    # menu board
    nrrect(c, [686, 168, 952, 410], 14, STEEL, w=4, a=190,
           fill=(9, 13, 24))
    ntext(c, (819, 198), "NEON BEAN", size=27, color=CREAM, a=240)
    nline(c, [(718, 218), (920, 218)], CYAN, w=2.5, a=170, jit=1, halo=1.6)
    menu = (("ESPRESSO", "3"), ("LATTE", "4"), ("DOUGHNUT", "2"),
            ("RE-FILL", "1"))
    for i, (name, price) in enumerate(menu):
        y = 250 + i * 33
        ntext(c, (716, y), name, size=16, color=CHALK, a=220, anchor="lm")
        ntext(c, (914, y), price, size=16, color=AMBER, a=220, anchor="rm")
        nline(c, [(714, y + 13), (924, y + 13)], STEEL_DIM, w=1.2, a=95,
              jit=0, halo=0)
    # little cup doodle
    nline(c, [(738, 374), (738, 392), (758, 392), (758, 374)],
          CREAM, w=2.5, a=165, jit=1, halo=1.5)
    c.arc([755, 378, 770, 392], 270, 90, fill=CREAM + (165,), w=2)
    ntext(c, (806, 380), "PAUSE = PERKS", size=12, color=DIM, a=150)

    # counter
    c.rrect([480, 466, 1258, 510], 8, fill=(34, 48, 66, 255),
            outline=STEEL + (225,), w=4)
    c.rrect([498, 508, 1248, 650], 5, fill=(11, 16, 28, 255),
            outline=STEEL_DIM + (235,), w=3)
    for x in range(540, 1220, 118):
        nline(c, [(x, 520), (x, 636)], STEEL_DIM, w=2, a=130, jit=0, halo=1.2)
        nline(c, [(x + 14, 536), (x + 82, 536)], STEEL_DIM, w=1.5, a=75,
              jit=0, halo=0)
    nline(c, [(510, 626), (1236, 626)], STEEL, w=3, a=120, jit=0, halo=1.4)
    ntext(c, (874, 578), "NEON BEAN", size=19, color=STEEL, a=135)

    # espresso machine
    c.rrect([930, 356, 1170, 466], 10, fill=(22, 30, 46, 255),
            outline=STEEL + (215,), w=3)
    c.rrect([948, 372, 1152, 405], 5, fill=GLASS + (255,),
            outline=CHALK + (130,), w=2)
    c.circle((1012, 388), 9, outline=AMBER + (210,), w=2)
    c.line([(1012, 388), (1018, 382)], fill=AMBER + (210,), w=2)
    c.circle((1090, 388), 9, outline=CYAN + (160,), w=2)
    for x, col in ((966, AMBER), (998, GREEN), (1130, NEON_RED)):
        c.circle((x, 422), 5, fill=col + (220,))
    c.rrect([954, 434, 1002, 450], 3, fill=STEEL_DIM + (255,))
    c.rrect([1120, 410, 1130, 466], 3, fill=STEEL + (180,))
    # steam wand + cup
    nline(c, [(1120, 414), (1097, 438), (1099, 456)], CHALK, w=3, a=170,
          jit=1, halo=1.5)
    c.rrect([1072, 448, 1096, 466], 3, fill=(14, 20, 32, 255),
            outline=CREAM + (180,), w=2)
    # portafilter
    nline(c, [(1008, 430), (1034, 436), (1040, 446)], CREAM, w=4, a=185,
          jit=1, halo=1.5)

    # pastry dome
    c.arc([716, 394, 892, 480], 180, 360, fill=CHALK + (155,), w=3)
    nline(c, [(716, 444), (892, 444)], STEEL, w=3, a=185, jit=0, halo=1.5)
    for i, (cx, cy) in enumerate(((764, 440), (810, 447), (850, 438))):
        c.poly([(cx - 22, cy + 8), (cx, cy - 18), (cx + 22, cy + 8)],
               fill=(44, 26, 12, 220), outline=AMBER + (170,), w=2)
        nline(c, [(cx - 12, cy), (cx + 10, cy - 4)], GOLD, w=2, a=170,
              jit=0, halo=1.2)

    # register + cup stack
    c.rrect([600, 402, 686, 466], 6, fill=(18, 26, 40, 255),
            outline=STEEL + (180,), w=3)
    c.rrect([612, 414, 674, 432], 3, fill=GLASS + (255,),
            outline=CYAN + (130,), w=2)
    for i in range(3):
        c.rrect([526 + i * 3, 434 - i * 12, 562 + i * 3, 446 - i * 12], 4,
                fill=(18, 24, 38, 255), outline=CHALK + (145,), w=2)

    # pendant lamps
    for lx, ly in ((198, 218), (612, 220), (1182, 210)):
        nline(c, [(lx, 118), (lx, ly - 26)], STEEL, w=2.5, a=170, jit=0, halo=1.2)
        c.poly([(lx - 30, ly - 26), (lx + 30, ly - 26), (lx + 17, ly + 8),
                (lx - 17, ly + 8)], fill=(24, 18, 12, 255),
               outline=STEEL + (200,), w=3)
        c.circle((lx, ly + 13), 6, fill=WARM + (245,))
        c.glow((lx, ly + 18), 46, WARM, alpha=14, rings=4)

    # floor
    nline(c, [(0, 650), (W, 650)], STEEL_DIM, w=2.5, a=110, jit=0, halo=0)
    for x in range(-120, W + 160, 150):
        nline(c, [(x, 650), (x + 70, H)], STEEL_DIM, w=1.3, a=55, jit=0, halo=0)
    for y in (676, 704):
        nline(c, [(0, y), (W, y)], STEEL_DIM, w=1.1, a=38, jit=0, halo=0)
    _CAFE_CACHE = img
    return img


def conference_panel(c, box):
    x0, y0, x1, y1 = box
    nrrect(c, box, 16, STEEL, w=3.5, a=210, fill=(7, 11, 21))
    ntext(c, ((x0 + x1) / 2, y0 + 20), "WRONG MEETING", size=18,
          color=CHALK, a=230)
    # wall panelling
    for x in range(int(x0 + 36), int(x1 - 20), 86):
        nline(c, [(x, y0 + 38), (x, y0 + 216)], STEEL_DIM, w=1.2, a=70,
              jit=0, halo=0)
    # projector screen
    screen = [x0 + 46, y0 + 46, x1 - 46, y0 + 176]
    nrrect(c, screen, 6, STEEL, w=3, a=190, fill=GLASS)
    ntext(c, ((screen[0] + screen[2]) / 2, screen[1] + 27), "Q3 SYNERGY",
          size=22, color=CREAM, a=235)
    # bar chart
    heights = (30, 48, 22, 58, 40)
    for i, h in enumerate(heights):
        bx = screen[0] + 28 + i * 64
        nline(c, [(bx, screen[3] - 18 - h), (bx, screen[3] - 18)], CYAN,
              w=13, a=160, jit=0, halo=1.4)
    nline(c, [(screen[0] + 22, screen[3] - 18), (screen[0] + 338, screen[3] - 18)],
          CHALK, w=2, a=150, jit=0, halo=1.2)
    ntext(c, (screen[0] + 58, screen[3] - 42), "UP", size=12, color=GREEN, a=190)
    # table
    c.rrect([x0 + 26, y0 + 226, x1 - 26, y0 + 276], 12,
            fill=(22, 30, 46, 255), outline=STEEL + (180,), w=3)
    nline(c, [(x0 + 48, y0 + 276), (x0 + 48, y0 + 336)], STEEL, w=5, a=170,
          jit=0, halo=1.3)
    nline(c, [(x1 - 48, y0 + 276), (x1 - 48, y0 + 336)], STEEL, w=5, a=170,
          jit=0, halo=1.3)
    # laptops and water
    for lx in (x0 + 72, x0 + 242, x0 + 410):
        c.poly([(lx, y0 + 246), (lx + 48, y0 + 246), (lx + 54, y0 + 270),
                (lx - 6, y0 + 270)], fill=(8, 13, 24, 255),
               outline=CHALK + (135,), w=2)
        c.rrect([lx + 8, y0 + 250, lx + 40, y0 + 264], 2,
                fill=CYAN + (40,), outline=CYAN + (80,), w=1)
    for gx in (x0 + 182, x0 + 360):
        c.rrect([gx, y0 + 236, gx + 14, y0 + 258], 3,
                fill=(22, 46, 58, 190), outline=CHALK + (110,), w=1.5)
    # chairs behind
    for cx in (x0 + 96, x0 + 266, x0 + 436):
        c.rrect([cx - 23, y0 + 190, cx + 23, y0 + 238], 10,
                fill=(12, 18, 30, 255), outline=STEEL_DIM + (180,), w=2)
        nline(c, [(cx - 18, y0 + 234), (cx - 28, y0 + 300)], STEEL_DIM,
              w=3, a=150, jit=0, halo=1.2)
    # floor + shadow
    nline(c, [(x0 + 18, y0 + 342), (x1 - 18, y0 + 342)], STEEL_DIM,
          w=2.5, a=120, jit=0, halo=1.2)
    c.ellipse([x0 + 140, y0 + 332, x1 - 80, y0 + 356],
              fill=(0, 0, 0, 90))


def barber_panel(c, box):
    x0, y0, x1, y1 = box
    nrrect(c, box, 16, STEEL, w=3.5, a=210, fill=(9, 11, 22))
    ntext(c, ((x0 + x1) / 2, y0 + 20), "BAD HAIRCUT", size=18,
          color=CHALK, a=230)
    # tiled wall
    brick_wall(c, [x0 + 18, y0 + 40, x1 - 18, y0 + 338], a=90, step=36)
    # mirror
    mirror = [x0 + 38, y0 + 46, x0 + 310, y0 + 190]
    nrrect(c, mirror, 10, CHALK, w=3, a=175, fill=GLASS)
    nline(c, [(mirror[0] + 28, mirror[3] - 26), (mirror[0] + 116, mirror[1] + 22)],
          CHALK, w=2, a=90, jit=0, halo=0)
    nline(c, [(mirror[0] + 62, mirror[3] - 20), (mirror[0] + 152, mirror[1] + 18)],
          CHALK, w=1.5, a=55, jit=0, halo=0)
    # bulbs around mirror
    for i in range(7):
        bx = mirror[0] + 18 + i * (mirror[2] - mirror[0] - 36) / 6
        c.circle((bx, mirror[1] - 2), 4, fill=WARM + (190,))
    # shelf with bottles
    nline(c, [(x0 + 330, y0 + 176), (x1 - 28, y0 + 176)], STEEL, w=4,
          a=175, jit=0, halo=1.4)
    for i, col in enumerate((AMBER, GREEN, MAGENTA, CHALK)):
        bx = x0 + 346 + i * 38
        c.rrect([bx, y0 + 136, bx + 18, y0 + 174], 3,
                fill=dim(col, 0.25) + (255,), outline=col + (150,), w=2)
        c.rrect([bx + 4, y0 + 128, bx + 14, y0 + 138], 2,
                fill=STEEL_DIM + (255,))
    # barber chair
    c.rrect([x0 + 202, y0 + 230, x0 + 354, y0 + 326], 12,
            fill=(18, 24, 38, 255), outline=STEEL + (195,), w=3)
    nline(c, [(x0 + 224, y0 + 326), (x0 + 214, y0 + 354)], STEEL, w=6,
          a=170, jit=0, halo=1.3)
    nline(c, [(x0 + 332, y0 + 326), (x0 + 342, y0 + 354)], STEEL, w=6,
          a=170, jit=0, halo=1.3)
    nline(c, [(x0 + 224, y0 + 354), (x0 + 334, y0 + 354)], STEEL, w=4,
          a=150, jit=0, halo=1.2)
    # counter under mirror
    c.rrect([x0 + 32, y0 + 196, x0 + 304, y0 + 224], 5,
            fill=(16, 22, 36, 255), outline=STEEL_DIM + (170,), w=2)
    # floor
    nline(c, [(x0 + 22, y0 + 356), (x1 - 22, y0 + 356)], STEEL_DIM,
          w=2.5, a=110, jit=0, halo=1.1)


def party_bg():
    """Baked back room: security monitor, camera mount, staff-party table."""
    img = dark_bg()
    c = Ctx(img)

    # wall
    brick_wall(c, [0, 110, W, 610], a=165, step=50)
    nline(c, [(0, 110), (W, 110)], STEEL_DIM, w=4, a=180, jit=0, halo=1.5)
    for x in range(70, W, 180):
        nline(c, [(x, 110), (x, 610)], STEEL_DIM, w=1.2, a=55, jit=0, halo=0)

    # bunting + string lights, right side
    pts = [(626, 166), (760, 206), (906, 218), (1052, 198), (1206, 154)]
    nline(c, pts, STEEL, w=2.5, a=170, jit=1, halo=1.3)
    for i, (px, py) in enumerate(pts[1:-1]):
        col = (AMBER, CYAN, MAGENTA)[i % 3]
        c.poly([(px - 17, py + 4), (px + 17, py + 4), (px, py + 36)],
               fill=dim(col, 0.33) + (255,), outline=col + (140,), w=2)
        c.circle((px, py + 43), 3.5, fill=WARM + (210,))
    # little practicals along the wall
    for lx, ly in ((690, 290), (900, 270), (1120, 292)):
        c.circle((lx, ly), 7, fill=WARM + (210,))
        c.glow((lx, ly), 66, WARM, alpha=12, rings=3)

    # security monitor (top left)
    nrrect(c, [54, 84, 614, 388], 18, STEEL, w=5, a=230,
           fill=(10, 14, 26))
    nrrect(c, [76, 104, 592, 364], 10, STEEL_DIM, w=2.5, a=210,
           fill=GLASS)
    ntext(c, (334, 402), "SECURITY FEED  //  CAM 04", size=15, color=CHALK,
          a=190)
    for i in range(3):
        c.circle((548 - i * 12, 408), 3, fill=(AMBER, GREEN, NEON_RED)[i] + (180,))

    # wall clock right of monitor, behind hero's space
    c.circle((1018, 140), 41, fill=(7, 11, 20, 255),
             outline=STEEL + (190,), w=3)
    for i in range(12):
        px, py = polar(1018, 140, 33, i * 30 - 90)
        px2, py2 = polar(1018, 140, 38, i * 30 - 90)
        c.line([(px, py), (px2, py2)], fill=CHALK + (150,), w=2)
    c.line([(1018, 140), (1018, 116)], fill=CREAM + (210,), w=3)
    c.line([(1018, 140), (1036, 145)], fill=CYAN + (190,), w=2)
    c.circle((1018, 140), 4, fill=WARM + (230,))

    # camera mount (top right)
    nline(c, [(1192, 66), (1234, 50), (1252, 70)], STEEL, w=5, a=200,
          jit=1, halo=1.4)
    c.poly([(1094, 84), (1196, 100), (1182, 150), (1080, 132)],
           fill=(20, 27, 42, 255), outline=STEEL + (210,), w=3)
    nline(c, [(1112, 100), (1104, 84)], STEEL, w=4, a=180, jit=0, halo=1.3)
    c.circle((1092, 120), 17, fill=(5, 8, 16, 255), outline=CHALK + (190,),
             w=3)
    c.circle((1092, 120), 7, fill=CYAN + (120,))
    ntext(c, (1138, 174), "CAM 04", size=14, color=CHALK, a=180)

    # party table / bar top
    c.rrect([650, 512, 1250, 570], 10, fill=(27, 36, 52, 255),
            outline=STEEL + (190,), w=4)
    c.rrect([674, 568, 1226, 640], 5, fill=(10, 15, 26, 255),
            outline=STEEL_DIM + (210,), w=3)
    # cake + cups + snacks
    c.rrect([836, 486, 928, 516], 5, fill=(38, 24, 42, 255),
            outline=MAGENTA + (170,), w=2)
    for i in range(4):
        c.circle((854 + i * 18, 486), 4, fill=WARM + (220,))
    for i, x in enumerate((704, 758, 1012, 1078, 1150)):
        c.rrect([x, 496 - (i % 2) * 4, x + 20, 514 - (i % 2) * 4], 3,
                fill=(12, 18, 30, 255), outline=CHALK + (135,), w=2)
    c.arc([964, 486, 1002, 510], 180, 360, fill=AMBER + (150,), w=2)
    # floor
    nline(c, [(0, 640), (W, 640)], STEEL_DIM, w=3, a=120, jit=0, halo=1.1)
    for x in range(-120, W + 160, 150):
        nline(c, [(x, 640), (x + 70, H)], STEEL_DIM, w=1.2, a=55,
              jit=0, halo=0)

    # balloons
    for bx, by, col in ((644, 280, MAGENTA), (618, 340, CYAN), (1210, 286, AMBER)):
        nline(c, [(bx, by + 44), (bx + 7, by + 130), (bx - 2, by + 190)],
              STEEL, w=1.4, a=110, jit=0, halo=0)
        c.ellipse([bx - 24, by - 30, bx + 24, by + 32],
                  fill=dim(col, 0.30) + (220,), outline=col + (150,), w=2)
        nline(c, [(bx - 9, by - 10), (bx - 2, by - 18)], CHALK, w=1.5,
              a=90, jit=0, halo=0)
    return img


# ---------------------------------------------------------- freeze / props


def coffee_cup(ctx, c, size=18, tilt=0.0, a=255, cream=CREAM):
    s = size
    ca, sa = math.cos(tilt), math.sin(tilt)

    def T(p):
        return (c[0] + p[0] * ca - p[1] * sa, c[1] + p[0] * sa + p[1] * ca)

    body = [(-s * 0.82, -s), (s * 0.82, -s), (s * 0.62, s),
            (-s * 0.62, s)]
    ctx.poly([T(p) for p in body], fill=(10, 16, 28, int(a * 0.92)))
    nline(ctx, [T(p) for p in body], cream, w=3.2, a=a, jit=0, halo=2.0)
    nline(ctx, [T((-s * 0.82, -s + 2)), T((s * 0.82, -s + 2))], CHALK,
          w=2.4, a=int(a * 0.8), jit=0, halo=1.5)
    nline(ctx, [T((-s * 0.76, -s * 0.35)), T((s * 0.76, -s * 0.35))],
          AMBER, w=4.0, a=int(a * 0.65), jit=0, halo=1.4)
    hc = T((s * 1.02, 0))
    ctx.circle(hc, s * 0.38, outline=cream + (int(a * 0.9),), w=2.5)


def hanging_splash(ctx, cup_tip, floor_y, a=255, p=1.0):
    """Coffee hanging in mid-air under a frozen cup."""
    x, y = cup_tip
    pts = [(x, y), (x + 5, y + 15), (x - 3, y + 31), (x + 4, y + 48),
           (x - 1, y + 62)]
    nline(ctx, pts, AMBER, w=5.0, a=a, jit=1.5, halo=2.2)
    nline(ctx, pts, WARM, w=1.8, a=a, jit=0, halo=1.8)
    for i in range(6):
        dx = (-28 + i * 12) + 5 * math.sin(i * 2.2)
        dy = y + 48 + 12 * ((i * 7) % 5) / 5.0
        rr = 3.0 + 2.2 * ((i * 11) % 4) / 4.0
        ctx.circle((x + dx, dy), rr, fill=AMBER + (int(a * 0.8),))
    # suspended ripple under the hanging drop
    ctx.ellipse([x - 42, y + 66, x + 48, y + 82],
                fill=WARM + (int(a * 0.16),), outline=AMBER + (int(a * 0.55),),
                w=2)
    if p > 0:
        ntext(ctx, (x + 4, floor_y - 12), "SUSPENDED", size=13, color=AMBER,
              a=int(a * 0.75))


def coffee_puddle(ctx, c, p, a=255):
    if p <= 0:
        return
    cx, cy = c
    rx = 38 + 78 * clamp(p)
    ctx.ellipse([cx - rx, cy - 10, cx + rx, cy + 15],
                fill=AMBER + (int(a * 0.22),), outline=WARM + (int(a * 0.70),),
                w=2)
    for i in range(8):
        dx = (i - 3.5) * (rr := 12 + 8 * ((i * 5) % 4))
        dy = -8 - 16 * ((i * 7) % 5) / 5.0 - 16 * clamp(p)
        ctx.circle((cx + dx, cy + dy), 2.5 + (i % 3), fill=AMBER +
                   (int(a * 0.6),))
    for i in range(5):
        ex = cx - rx + i * (2 * rx) / 4
        nline(ctx, [(ex, cy + 5), (ex + 10, cy + 13)], AMBER, w=1.6,
              a=int(a * 0.6), jit=0, halo=1.0)


def bad_hair(ctx, c, r, a=255):
    """Jagged, clearly-wrong fringe around the top of a head."""
    pts = []
    for i in range(12):
        ang = math.radians(205 + i * 11.0)
        rr = r * (1.03 if i % 2 == 0 else 1.34)
        pts.append((c[0] + rr * math.cos(ang), c[1] + rr * math.sin(ang)))
    nline(ctx, pts, CREAM, w=3.0, a=a, jit=0, halo=2.0)
    # dangling side clump
    nline(ctx, [(c[0] - r * 0.92, c[1] - r * 0.46),
                (c[0] - r * 1.16, c[1] - r * 0.08),
                (c[0] - r * 0.94, c[1] + r * 0.20)], CREAM, w=2.5,
          a=int(a * 0.9), jit=1, halo=1.6)


def shears(ctx, c, p=1.0, a=255):
    x, y = c
    for ang in (-26, 26):
        ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        p0 = (x, y)
        p1 = (x + 38 * ca * p, y + 38 * sa * p)
        nline(ctx, [p0, p1], CHALK, w=3.5, a=a, jit=0, halo=1.8)
    ctx.circle((x - 2, y - 5), 4.0, outline=STEEL + (a,), w=2)
    ctx.circle((x + 4, y - 9), 4.0, outline=STEEL + (a,), w=2)


def party_hat(ctx, c, color, a=255):
    x, y = c
    ctx.poly([(x - 15, y + 8), (x + 15, y + 8), (x + 2, y - 30)],
             fill=dim(color, 0.45) + (int(a * 0.9),), outline=color + (a,),
             w=2)
    ctx.circle((x + 2, y - 31), 3.5, fill=WARM + (a,))


def wall_clock(ctx, c, r, phase, a=255, frozen=False, tick=1.0):
    cx, cy = c
    ncircle(ctx, c, r, STEEL, w=3, a=a, fill=(7, 11, 20))
    for i in range(12):
        p0 = polar(cx, cy, r * 0.78, i * 30 - 90)
        p1 = polar(cx, cy, r * 0.93, i * 30 - 90)
        nline(ctx, [p0, p1], CHALK, w=2.2, a=int(a * 0.85), jit=0, halo=1.2)
    h_ang = -90 + (phase * 360.0) % 360.0
    m_ang = -90 + (phase * 12 * 360.0) % 360.0
    hp = polar(cx, cy, r * 0.48, h_ang)
    mp = polar(cx, cy, r * 0.72, m_ang)
    nline(ctx, [(cx, cy), hp], CREAM, w=4.5, a=a, jit=0, halo=1.8)
    nline(ctx, [(cx, cy), mp], CYAN, w=3.0, a=a, jit=0, halo=1.6)
    ctx.circle(c, r * 0.10, fill=WARM + (a,))
    if frozen:
        for i in range(6):
            sp = polar(cx, cy, r * 0.58, i * 60 + 15)
            nline(ctx, [polar(sp[0], sp[1], 5, i * 60 + 15),
                        polar(sp[0], sp[1], 5, i * 60 + 195)], CHALK,
                  w=1.5, a=int(a * 0.55), jit=0, halo=0)
    if tick > 0:
        ctx.glow(c, r * 2.5, CYAN, alpha=int(14 * tick), rings=3)


def pause_badge(ctx, t, freeze_t, thaw_t, center=(640, 72), r=42, a=255,
                compact=False):
    """10.0 -> 0.0 ring with a readable number and PAUSED / RESUMED label."""
    if t < freeze_t - 0.10 or t > thaw_t + 1.0:
        return
    remain, prog = frozen_clock(t, freeze_t, thaw_t)
    aa = int(a * ramp(t, freeze_t - 0.10, freeze_t + 0.18)
             * (1.0 - ramp(t, thaw_t + 0.10, thaw_t + 0.85)))
    if aa <= 4:
        return
    cx, cy = center
    # housing
    ctx.circle(center, r + 8, fill=(4, 8, 16, int(aa * 0.72)),
               outline=STEEL + (int(aa * 0.70),), w=2)
    # ticks
    for i in range(20):
        p0 = polar(cx, cy, r + 2, i * 18 - 90)
        p1 = polar(cx, cy, r + 8, i * 18 - 90)
        lit = (i / 20.0) <= prog
        nline(ctx, [p0, p1], (CYAN if lit else STEEL_DIM), w=1.8,
              a=int(aa * (0.95 if lit else 0.40)), jit=0, halo=0)
    # remaining arc
    if prog > 0.002:
        ctx.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * prog,
                fill=CYAN + (aa,), w=4.5)
    else:
        ctx.circle(center, r, outline=STEEL + (aa,), w=3)
    # pause glyph + number
    if t < thaw_t:
        for dx in (-7, 5):
            nline(ctx, [(cx + dx, cy - 18), (cx + dx, cy - 4)], CREAM, w=3.5,
                  a=aa, jit=0, halo=1.4)
    else:
        checkmark(ctx, [cx - 13, cy - 22, cx + 13, cy + 2], 1.0, color=GREEN,
                  w=4)
    ntext(ctx, (cx, cy + 17), f"{remain:04.1f}s", size=16, color=CREAM,
          a=aa)
    if not compact:
        ntext(ctx, (cx, cy + r + 22),
              ("TIME PAUSED" if t < thaw_t else "TIME RESUMED"),
              size=13, color=(CHALK if t < thaw_t else GREEN), a=aa)


def freeze_frame(ctx, p, t, a=255):
    """Frosted border and corner shards that snap in while time is stopped."""
    if p <= 0:
        return
    aa = int(a * p)
    inset = 20
    nrrect(ctx, [inset, inset, W - inset, H - inset], 18, STEEL_DIM, w=1.5,
           a=int(aa * 0.45), halo=0)
    for cx, cy, sx, sy in ((inset, inset, 1, 1), (W - inset, inset, -1, 1),
                           (inset, H - inset, 1, -1),
                           (W - inset, H - inset, -1, -1)):
        shard = [(cx, cy + sy * 82), (cx + sx * 42, cy + sy * 38),
                 (cx + sx * 18, cy + sy * 14), (cx + sx * 88, cy)]
        nline(ctx, shard, CHALK, w=2.2, a=int(aa * 0.55), jit=1, halo=1.5)
        for k in range(2):
            p0 = (cx + sx * (54 + k * 24), cy + sy * (12 + k * 18))
            p1 = (cx + sx * (92 + k * 30), cy + sy * (30 + k * 26))
            nline(ctx, [p0, p1], STEEL, w=1.3, a=int(aa * 0.42), jit=0, halo=0)
    # a few motes held in place
    for i in range(9):
        mx = 100 + (i * 137) % 1080
        my = 96 + (i * 89) % 420
        yy = my + 3 * math.sin(t * 1.7 + i)
        ctx.circle((mx, yy), 1.6 + (i % 3), fill=CHALK + (int(aa * 0.30),))


def freeze_ripple(ctx, c, p, color=CYAN, a=255):
    if p <= 0:
        return
    aa = int(a * (1.0 - clamp(p)) * 0.85)
    for i in range(3):
        rr = 24 + 96 * clamp(p) + i * 34
        ctx.circle(c, rr, outline=color + (max(0, aa - i * 18),), w=2.0)
    for i in range(12):
        p0 = polar(c[0], c[1], 18 + 70 * clamp(p), i * 30 + 8)
        p1 = polar(c[0], c[1], 30 + 92 * clamp(p), i * 30 + 8)
        nline(ctx, [p0, p1], CHALK, w=1.4, a=max(0, aa - 18), jit=0, halo=0)


# --------------------------------------------------------------- figures

POSE_DROP = {
    "head": (3, -88, 12),
    "spine": [(2, -76), (0, -44)],
    "armL": [(0, -72), (-16, -56), (-22, -40)],
    "armR": [(1, -72), (18, -62), (28, -55)],
    "legL": [(0, -44), (-15, -22), (-18, 0)],
    "legR": [(0, -44), (14, -22), (18, 0)],
}

POSE_SHOCK = {
    "head": (0, -90, 13),
    "spine": [(0, -76), (0, -44)],
    "armL": [(0, -72), (-22, -84), (-28, -98)],
    "armR": [(0, -72), (22, -84), (28, -98)],
    "legL": [(0, -44), (-16, -22), (-20, 0)],
    "legR": [(0, -44), (16, -22), (20, 0)],
}

POSE_POSE_1 = {
    "head": (0, -88, 12),
    "spine": [(0, -76), (0, -44)],
    "armL": [(0, -72), (-25, -58), (-34, -42)],
    "armR": [(0, -72), (22, -64), (30, -48)],
    "legL": [(0, -44), (-15, -22), (-24, 0)],
    "legR": [(0, -44), (12, -22), (21, 0)],
}

POSE_POSE_2 = {
    "head": (1, -90, 12),
    "spine": [(1, -76), (0, -44)],
    "armL": [(0, -72), (-26, -58), (-35, -43)],
    "armR": [(0, -72), (27, -67), (54, -58)],
    "legL": [(0, -44), (-16, -22), (-25, 0)],
    "legR": [(0, -44), (12, -22), (22, 0)],
}

POSE_INNOCENT = {
    "head": (0, -88, 12),
    "spine": [(0, -76), (0, -44)],
    "armL": [(0, -72), (-16, -58), (-20, -42)],
    "armR": [(0, -72), (27, -67), (54, -58)],
    "legL": [(0, -44), (-14, -22), (-17, 0)],
    "legR": [(0, -44), (14, -22), (17, 0)],
}

POSE_POINT = {
    "head": (2, -88, 12),
    "spine": [(1, -76), (0, -44)],
    "armL": [(0, -72), (-15, -58), (-20, -42)],
    "armR": [(0, -72), (30, -77), (48, -88)],
    "legL": [(0, -44), (-14, -22), (-18, 0)],
    "legR": [(0, -44), (13, -22), (17, 0)],
}

POSE_THUMBS = {
    "head": (0, -88, 12),
    "spine": [(0, -76), (0, -44)],
    "armL": [(0, -72), (-15, -58), (-20, -42)],
    "armR": [(0, -72), (19, -60), (26, -76)],
    "legL": [(0, -44), (-14, -22), (-18, 0)],
    "legR": [(0, -44), (13, -22), (17, 0)],
}

POSE_BACKPEDAL = {
    "head": (2, -88, 12),
    "spine": [(2, -76), (0, -44)],
    "armL": [(0, -72), (-18, -84), (-26, -96)],
    "armR": [(0, -72), (17, -83), (24, -96)],
    "legL": [(0, -44), (-16, -24), (-28, -2)],
    "legR": [(0, -44), (13, -22), (28, -4)],
}

POSE_HOLD_CUP = {
    "head": (0, -88, 12),
    "spine": [(0, -76), (0, -44)],
    "armL": [(0, -72), (-15, -58), (-18, -44)],
    "armR": [(0, -72), (21, -60), (30, -50)],
    "legL": [(0, -44), (-14, -22), (-18, 0)],
    "legR": [(0, -44), (14, -22), (18, 0)],
}

POSE_SIT_BARBER = {
    "head": (0, -88, 13),
    "spine": [(0, -76), (0, -44)],
    "armL": [(0, -72), (-17, -58), (-22, -44)],
    "armR": [(0, -72), (17, -58), (22, -44)],
    "legL": [(0, -44), (-31, -43), (-58, -42)],
    "legR": [(0, -44), (-28, -41), (-54, -40)],
}


def sit_cape(ctx, x, y, s, a=255):
    """A barber cape around the seated hero, drawn behind the figure."""
    ctx.poly([(x - 24 * s, y - 70 * s), (x + 24 * s, y - 70 * s),
              (x + 42 * s, y - 28 * s), (x + 30 * s, y - 14 * s),
              (x + 8 * s, y - 21 * s), (x - 9 * s, y - 14 * s),
              (x - 36 * s, y - 26 * s)],
             fill=(16, 22, 36, int(a * 0.9)), outline=STEEL + (a,), w=3)


def doctor(ctx, x, y, s, a=255, mouth="flat"):
    person(ctx, x, y, s, POSE_STAND, color=CHALK, w=5,
           look=(0.2, 0), brow="flat", mouth=mouth)
    # lapel / lanyard
    nline(ctx, [(x - 8 * s, y - 69 * s), (x, y - 52 * s),
                (x + 8 * s, y - 69 * s)], CYAN, w=2.1, a=int(a * 0.8), jit=0,
          halo=1.2)


# --------------------------------------------------------------- scenes


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

    def build(self):
        pass

    def draw(self, ctx, lt):
        pass

    def shake(self, lt):
        return (0.0, 0.0)

    def zoom(self, lt):
        p = clamp(lt / max(0.5, self.t1 - self.t0))
        a, b = self.zoom_range
        return lerp(a, b, smoothstep(p))


# ------------------------------------------------------------------ 1: spill


class SpillScene(Scene):
    id = "spill"

    def build(self):
        self.bg = cafe_bg()

    def freeze_abs(self):
        return self.L(0)["caps"][1]["start"]

    def thaw_abs(self):
        return self.L(7)["caps"][1]["start"]

    def draw(self, ctx, lt):
        b00, b01 = self.beat(0, 0), self.beat(0, 1)
        b10, b11 = self.beat(1, 0), self.beat(1, 1)
        f_abs = self.freeze_abs()
        f_local = f_abs - self.t0
        abs_t = self.t0 + lt
        remain, prog = frozen_clock(abs_t, f_abs, self.thaw_abs())
        fz = ramp(lt, f_local, f_local + 0.22)

        # the other customers, already in the room
        frozen_phase = 0.18
        ph1 = frozen_phase if lt >= f_local else (lt * 0.55) % 1.0
        ph2 = 0.62 if lt >= f_local else (lt * 0.45 + 0.3) % 1.0
        person(ctx, 842, 650, 2.05, walk_pose(ph1), color=CHALK, w=5,
               look=(0.0, 0.0), brow="flat", mouth="flat")
        person(ctx, 1078, 650, 2.12, POSE_HOLD_CUP, color=CHALK, w=5,
               look=(-0.2, 0.0), brow="flat", mouth="flat")
        cup_x = 1078 + 30 * 2.12
        coffee_cup(ctx, (cup_x, 650 - 50 * 2.12), size=13, tilt=-0.12,
                   a=210, cream=CHALK)

        # takeaway cup leaves the hero's hand
        drop_t = ramp(lt, b00 + 0.14, max(b00 + 0.2, f_local - 0.02))
        drop = ease_in(drop_t)
        hx, hy = 360, 650
        cup = (hx + (28 + 18 * drop) * 2.6, hy - (55 - 22 * drop) * 2.6)
        tilt = -0.08 - 0.72 * drop
        coffee_cup(ctx, cup, size=18, tilt=tilt, a=255)

        # hero
        p = blend_pose(POSE_DROP, POSE_SHOCK,
                       ease_out(ramp(lt, b00 + 0.12, b00 + 0.46)))
        if lt < f_local:
            p = blend_pose(p, POSE_DROP, ramp(lt, b10, b10 + 0.5))
        jolt = 1.4 * math.sin(lt * 46) * ramp(lt, b00 + 0.3, b00 + 0.6)
        person(ctx, hx + jolt, hy, 2.6, p, color=CYAN, w=7,
               look=(0.35, -0.45), brow="up",
               mouth=("o" if lt >= b00 + 0.28 else "flat"))

        if lt >= f_local:
            # the cup is stuck; the splash hangs under it
            tip = (cup[0] + 4, cup[1] + 21)
            hanging_splash(ctx, tip, 650, a=int(255 * ramp(lt, f_local,
                                                          f_local + 0.16)),
                           p=prog)
            ripple = ramp(lt, f_local, f_local + 0.5)
            if ripple < 1:
                freeze_ripple(ctx, (cup[0], cup[1] + 6), ripple,
                              color=CYAN, a=255)
        if fz > 0:
            freeze_frame(ctx, fz, lt, a=255)

        pause_badge(ctx, abs_t, f_abs, self.thaw_abs(), center=(640, 72), r=42)

        # cue labels
        lab = int(255 * ramp(lt, b01, b01 + 0.25))
        if lab > 10:
            ntext(ctx, (506, 452), "COFFEE: HALTED", size=15, color=AMBER,
                  a=lab)
            nline(ctx, [(438, 464), (486, 452), (528, 462)], AMBER, w=2,
                  a=lab, jit=1, halo=1.3)
        if lt >= b11:
            a2 = int(255 * ramp(lt, b11, b11 + 0.35))
            ntext(ctx, (640, 556), "EVERY DROPLET  //  FROZEN", size=14,
                  color=CHALK, a=int(a2 * 0.8))

        # tiny speed lines when the cup first slips
        slip = ramp(lt, b00 + 0.05, b00 + 0.35) * (1 - ramp(lt, f_local,
                                                           f_local + 0.1))
        motion_lines(ctx, 448, 540, 80, n=4, r0=16, r1=52,
                     a=int(165 * slip), spread=52, w=3.5, seed=3)


# ------------------------------------------------------------------ 2: pose


class PoseScene(Scene):
    id = "pose"

    def build(self):
        self.bg = cafe_bg()

    def freeze_abs(self):
        return self.L(0)["caps"][1]["start"]

    def thaw_abs(self):
        return self.L(7)["caps"][1]["start"]

    def draw(self, ctx, lt):
        b20, b21 = self.beat(2, 0), self.beat(2, 1)
        b30, b31, b32 = (self.beat(3, 0), self.beat(3, 1),
                         self.beat(3, 2))
        abs_t = self.t0 + lt
        f_abs = self.freeze_abs()
        remain, prog = frozen_clock(abs_t, f_abs, self.thaw_abs())

        # frozen room, spill untouched
        person(ctx, 842, 650, 2.05, walk_pose(0.18), color=CHALK, w=5,
               look=(-0.3, 0.0), brow="flat", mouth="flat")
        cup_x = 1078 + 30 * 2.12
        person(ctx, 1078, 650, 2.12, POSE_HOLD_CUP, color=CHALK, w=5,
               look=(-0.5, 0.0), brow="up", mouth="flat")
        coffee_cup(ctx, (cup_x, 650 - 50 * 2.12), size=13, tilt=-0.12,
                   a=210, cream=CHALK)
        # completely still splash from the previous shot
        cup = (360 + 46 * 2.6, 650 - 33 * 2.6)
        coffee_cup(ctx, cup, size=18, tilt=-0.80, a=255)
        hanging_splash(ctx, (cup[0] + 4, cup[1] + 21), 650, a=255, p=prog)

        # hero: shrug -> pose -> chin up -> hand on counter
        p = POSE_POSE_1
        p = blend_pose(POSE_POSE_1, POSE_POSE_2,
                       ease_out_back(ramp(lt, b21 + 0.05, b21 + 0.52)))
        p = blend_pose(p, POSE_POSE_2,
                       ease_in_out(ramp(lt, b21 + 0.52, b30 + 0.10)))
        if lt < b21:
            p = blend_pose(POSE_POSE_1, POSE_POSE_2, 0.0)
        # hand slides onto the counter edge on "one hand..."
        p = blend_pose(p, POSE_POSE_2, ease_in_out(ramp(lt, b31, b31 + 0.45)))
        # micro-breath, but the room is frozen
        breath = 1.5 * math.sin(lt * 2.2) * ramp(lt, b21, b21 + 0.5)
        face_up = ramp(lt, b30, b30 + 0.35)
        smile = "smile" if lt >= b30 - 0.05 else "flat"
        person(ctx, 360, 650 + breath, 2.6, p, color=CYAN, w=7,
               look=(0.10, -0.75 * face_up), brow="up", mouth=smile)

        # spill label, still frozen
        ntext(ctx, (486, 452), "STILL FROZEN", size=14, color=AMBER, a=190)
        nline(ctx, [(440, 464), (482, 452), (524, 462)], AMBER, w=2,
              a=190, jit=1, halo=1.3)

        # the pose lands in stages
        aa = int(255 * ramp(lt, b20, b20 + 0.35))
        if aa > 8:
            ntext(ctx, (162, 246), "DO NOT CLEAN.", size=22, color=CHALK,
                  a=aa)
            ntext(ctx, (162, 274), "POSE.", size=26, color=CYAN, a=aa)
        if lt >= b30:
            q = ramp(lt, b30, b30 + 0.38)
            ntext(ctx, (508, 286), "CHIN UP", size=20, color=GOLD,
                  a=int(255 * q))
            nline(ctx, [(394, 332), (454, 306), (500, 298)], GOLD, w=2.2,
                  a=int(255 * q), jit=1, halo=1.4)
        if lt >= b31:
            q = ramp(lt, b31, b31 + 0.42)
            ntext(ctx, (620, 492), "HAND ON COUNTER", size=16, color=GOLD,
                  a=int(255 * q))
            nline(ctx, [(544, 510), (578, 502), (606, 496)], GOLD, w=2,
                  a=int(255 * q), jit=1, halo=1.3)

        # FLAWLESS + camera flash
        if lt >= b32:
            q = ramp(lt, b32, b32 + 0.48)
            sc = lerp(0.65, 1.0, ease_out_back(q))
            ntext(ctx, (214, 178), "FLAWLESS", size=int(round(42 * sc)),
                  color=CREAM, a=int(255 * q))
            for k in range(6):
                sp = polar(214, 178, 134, k * 60 + lt * 45)
                sparkle(ctx, sp, 9, color=GOLD + (int(220 * q),))
            # viewfinder corners around the hero
            for ax, ay, sx, sy in ((286, 390, 1, 1), (438, 390, -1, 1),
                                   (286, 654, 1, -1), (438, 654, -1, -1)):
                nline(ctx, [(ax, ay + sy * 22), (ax, ay),
                            (ax + sx * 22, ay)], CHALK, w=2.2,
                      a=int(210 * q), jit=0, halo=1.3)
            if q < 0.55:
                ctx.rrect([0, 0, W, H], 0, fill=(240, 250, 255,
                                                 int(50 * (1 - q / 0.55))))

        if prog > 0:
            freeze_frame(ctx, min(1.0, prog * 4), lt, a=255)
        pause_badge(ctx, abs_t, f_abs, self.thaw_abs(), center=(640, 72), r=42)

    def shake(self, lt):
        d = lt - self.beat(3, 2)
        if 0 <= d < 0.28:
            a = 4.0 * (1 - d / 0.28)
            return (a * math.sin(lt * 70), a * 0.5 * math.cos(lt * 60))
        return (0.0, 0.0)


# ------------------------------------------------------------------ 3: fixes


class FixesScene(Scene):
    id = "fixes"
    LEFT = (54, 128, 620, 500)
    RIGHT = (660, 128, 1226, 500)

    def build(self):
        self.bg = dark_bg(grid=False)
        c = Ctx(self.bg)
        ntext(c, (640, 56), "DAMAGE CONTROL  //  TWO FREEZES", size=18,
              color=DIM, a=220)
        conference_panel(c, self.LEFT)
        barber_panel(c, self.RIGHT)
        nline(c, [(640, 140), (640, 490)], STEEL_DIM, w=2, a=90,
              jit=0, halo=0)

    def freeze_abs(self):
        return self.L(0)["caps"][1]["start"]

    def thaw_abs(self):
        return self.L(7)["caps"][1]["start"]

    def draw(self, ctx, lt):
        b40, b41, b42 = (self.beat(4, 0), self.beat(4, 1),
                         self.beat(4, 2))
        b50, b51, b52 = (self.beat(5, 0), self.beat(5, 1),
                         self.beat(5, 2))
        b60, b61 = self.beat(6, 0), self.beat(6, 1)
        abs_t = self.t0 + lt
        remain, prog = frozen_clock(abs_t, self.freeze_abs(), self.thaw_abs())

        # ---- left: the wrong meeting
        # hero presenting, board members frozen in their chairs
        person(ctx, 170, 478, 1.62, POSE_POINT, color=CYAN, w=5,
               look=(0.45, -0.25), brow="up",
               mouth=("o" if b40 <= lt < b41 else "flat"))
        person(ctx, 430, 456, 1.35, POSE_SIT, color=CHALK, w=4,
               look=(-0.4, 0.0), brow="flat", mouth="flat")
        person(ctx, 532, 456, 1.32, POSE_SIT, color=CHALK, w=4,
               look=(0.2, 0.0), brow="up", mouth="flat")

        # slide swap on "Swap the slides."
        if lt >= b42:
            q = ramp(lt, b42, b42 + 0.32)
            # blank the old slide with a dark card, then the cat slide
            ctx.rrect([100, 176, 574, 302], 6,
                      fill=(7, 11, 21, int(235 * q)))
            sc = lerp(0.64, 1.0, ease_out_back(q))
            box = scaled_box([126, 186, 548, 292], sc)
            nrrect(ctx, box, 5, GREEN, w=2.5, a=int(255 * q),
                   fill=(12, 20, 32))
            ntext(ctx, ((box[0] + box[2]) / 2, box[1] + 22),
                  "STRATEGY: NAP", size=15, color=GREEN, a=int(255 * q))
            # cat: head + ears + whiskers
            ccx, ccy = (box[0] + box[2]) / 2, box[1] + 67
            ncircle(ctx, (ccx, ccy), 21, CREAM, w=3, a=int(255 * q))
            nline(ctx, [(ccx - 18, ccy - 12), (ccx - 26, ccy - 32),
                        (ccx - 4, ccy - 22)], CREAM, w=3, a=int(255 * q),
                  jit=0, halo=1.8)
            nline(ctx, [(ccx + 18, ccy - 12), (ccx + 26, ccy - 32),
                        (ccx + 4, ccy - 22)], CREAM, w=3, a=int(255 * q),
                  jit=0, halo=1.8)
            for sx in (-1, 1):
                ctx.circle((ccx + sx * 7, ccy - 3), 2.2,
                           fill=CREAM + (int(255 * q),))
                nline(ctx, [(ccx + sx * 10, ccy + 8), (ccx + sx * 30, ccy + 6)],
                      CHALK, w=1.2, a=int(190 * q), jit=0, halo=0)
            nline(ctx, [(ccx, ccy + 2), (ccx, ccy + 7)], WARM, w=2,
                  a=int(255 * q), jit=0, halo=0)
            # thumbs up
            if q > 0.55:
                ntext(ctx, (334, 314), "FIXED", size=16, color=GREEN,
                      a=int(255 * ramp(q, 0.55, 1)))
                checkmark(ctx, [292, 296, 324, 326], ramp(q, 0.5, 1),
                          color=GREEN, w=4)

        if b41 <= lt < b41 + 0.55:
            freeze_ripple(ctx, (334, 324), ramp(lt, b41, b41 + 0.55),
                          color=CYAN, a=255)
        if lt >= b41:
            ntext(ctx, (248, 116), "PAUSED", size=12, color=CYAN, a=220)
            # frozen meeting dust
            for i in range(3):
                ctx.circle((286 + i * 48, 154 + 9 * math.sin(i * 2)),
                           1.8, fill=CHALK + (130,))

        # ---- right: bad haircut
        if lt < b52:
            sit_cape(ctx, 950, 474, 1.72, a=240)
            sit_p = POSE_SIT_BARBER
            person(ctx, 950, 474, 1.72, sit_p, color=CYAN, w=5,
                   look=(0.0, 0.0), brow="sad", mouth="grimace")
            # bad fringe, drawn over the head circle
            hx = 950 + 0 * 1.72
            hy = 474 - 88 * 1.72
            bad_hair(ctx, (hx, hy), 13 * 1.72, a=245)
        # barber behind the chair
        person(ctx, 1110, 486, 1.58, POSE_THUMBS, color=CHALK, w=4.5,
               look=(-0.5, 0.0), brow="flat", mouth="smile")
        shears(ctx, (1084, 398), p=1.0, a=220)
        if lt >= b51:
            # scissors freeze, loose clump hangs
            ntext(ctx, (1084, 436), "SNIP: FROZEN", size=11, color=NEON_RED,
                  a=210)
            for i in range(3):
                hxx = 1052 + i * 13
                nline(ctx, [(hxx, 356), (hxx + 2, 374), (hxx - 2, 387)],
                      CREAM, w=1.4, a=180, jit=1, halo=1.2)
        # the customer backs out on "Walk out backwards."
        if lt >= b52:
            q = ramp(lt, b52, b52 + 0.8)
            bx = 950 - 180 * ease_out(q)
            person(ctx, bx, 474, 1.72, POSE_BACKPEDAL, color=CYAN, w=5,
                   look=(-0.4, 0.0), brow="sad", mouth="grimace")
            hx2 = bx
            hy2 = 474 - 88 * 1.72
            bad_hair(ctx, (hx2, hy2), 13 * 1.72, a=245)
            motion_lines(ctx, bx + 44, 390, 0, n=4, r0=16, r1=62,
                         a=int(190 * q), spread=52, w=4, seed=2)
            if q > 0.5:
                ntext(ctx, (795, 436), "EXIT: BACKWARDS", size=11,
                      color=CHALK, a=int(210 * q))
        if b50 <= lt < b50 + 0.5:
            freeze_ripple(ctx, (948, 392), ramp(lt, b50, b50 + 0.5),
                          color=MAGENTA, a=255)

        # ---- bottom ten-second strip
        if lt >= b60:
            q = ramp(lt, b60, b60 + 0.38)
            nrrect(ctx, [330, 518, 950, 590], 15, CYAN, w=2.5,
                   a=int(220 * q), fill=(7, 11, 20))
            ntext(ctx, (640, 540), "TEN SECONDS  =  ENOUGH", size=19,
                  color=CREAM, a=int(255 * q))
            # ten little ticks
            for i in range(10):
                tx = 380 + i * 57
                lit = (i / 10.0) <= prog
                nline(ctx, [(tx, 566), (tx, 576)], (CYAN if lit else STEEL),
                      w=3, a=int(210 * q), jit=0, halo=1.2)
            if lt >= b61:
                r = ramp(lt, b61, b61 + 0.45)
                for k, (bx, lab) in enumerate(((392, "MEETING"),
                                               (640, "HAIRCUT"),
                                               (888, "SPILL"))):
                    checkmark(ctx, [bx - 13, 536, bx + 13, 562],
                              ramp(r, k * 0.16, k * 0.16 + 0.7),
                              color=GREEN, w=4)
                    ntext(ctx, (bx + 28, 550), lab, size=9, color=CHALK,
                          a=int(180 * r))

        # tint the whole montage cold while time is paused
        if prog > 0:
            freeze_frame(ctx, min(1.0, prog * 4), lt, a=255)
        pause_badge(ctx, abs_t, self.freeze_abs(), self.thaw_abs(),
                    center=(640, 70), r=34, compact=True)

    def shake(self, lt):
        for b in (self.beat(4, 1), self.beat(5, 1), self.beat(6, 1)):
            d = lt - b
            if 0 <= d < 0.28:
                a = 5.0 * (1 - d / 0.28)
                return (a * math.sin(lt * 74), a * 0.5 * math.cos(lt * 64))
        return (0.0, 0.0)


# ------------------------------------------------------------------ 4: resume


class ResumeScene(Scene):
    id = "resume"

    def build(self):
        self.bg = cafe_bg()

    def freeze_abs(self):
        return self.L(0)["caps"][1]["start"]

    def thaw_abs(self):
        return self.L(7)["caps"][1]["start"]

    def draw(self, ctx, lt):
        b70, b71 = self.beat(7, 0), self.beat(7, 1)
        b80, b81 = self.beat(8, 0), self.beat(8, 1)
        abs_t = self.t0 + lt
        f_abs = self.freeze_abs()
        thaw_abs = self.thaw_abs()
        remain, prog = frozen_clock(abs_t, f_abs, thaw_abs)

        thawed = lt >= b71
        drink_phase = (lt * 0.55) % 1.0 if thawed else 0.18
        person(ctx, 842, 650, 2.05, walk_pose(drink_phase), color=CHALK, w=5,
               look=(0.0, 0.0), brow="flat", mouth="flat")
        cup_x = 1078 + 30 * 2.12
        person(ctx, 1078, 650, 2.12, POSE_HOLD_CUP, color=CHALK, w=5,
               look=(-0.2, 0.0), brow="flat", mouth="flat")
        coffee_cup(ctx, (cup_x, 650 - 50 * 2.12), size=13, tilt=-0.12,
                   a=210, cream=CHALK)

        # cup stays frozen until the click, then finishes falling
        fall = ramp(lt, b71 - 0.02, max(b71 + 0.3, b80 - 0.02))
        cup = (360 + 46 * 2.6, 650 - (33 + 22 * ease_in(fall)) * 2.6)
        take_pose = POSE_INNOCENT
        if lt < b70:
            take_pose = POSE_POSE_2
        elif lt < b80:
            take_pose = blend_pose(POSE_POSE_2, POSE_SHOCK,
                                   ease_out(ramp(lt, b70 + 0.08, b70 + 0.38)))
        else:
            take_pose = blend_pose(POSE_SHOCK, POSE_INNOCENT,
                                   ease_out(ramp(lt, b81, b81 + 0.45)))
        person(ctx, 360, 650, 2.6, take_pose, color=CYAN, w=7,
               look=(0.25, 0.55 if b70 <= lt < b81 else 0.0),
               brow=("up" if lt < b81 else "flat"),
               mouth=("o" if b70 <= lt < b80 else
                      ("grimace" if b80 <= lt < b81 else "smile")))

        # the falling coffee
        if lt < b80:
            coffee_cup(ctx, cup, size=18, tilt=-0.80 + 0.35 * fall, a=255)
            if thawed:
                # thin falling stream and droplets
                tipx, tipy = cup[0] - 2, cup[1] + 18
                for i in range(5):
                    yy = tipy + 8 + i * 11
                    ctx.circle((tipx + (i % 2) * 4, yy), 2.0,
                               fill=AMBER + (170,))
        else:
            coffee_cup(ctx, (cup[0], 626), size=18, tilt=-0.20, a=255)
            coffee_puddle(ctx, (472, 648), ramp(lt, b80, b80 + 0.58), a=255)
            if lt < b80 + 0.55:
                motion_lines(ctx, 472, 620, -90, n=5, r0=14, r1=50,
                             a=int(180 * (1 - ramp(lt, b80, b80 + 0.55))),
                             spread=80, w=3, seed=5)

        # clock: frozen, then clicks and runs
        clk_x, clk_y = (1118, 214)
        if lt < b70:
            phase = 0.74
        elif lt < b71:
            phase = 0.74 + 0.02 * math.sin(lt * 55)
        else:
            phase = 0.76 + (lt - b71) * 0.17
        wall_clock(ctx, (clk_x, clk_y), 35, phase, a=230,
                   frozen=lt < b71, tick=(1 - ramp(lt, b71, b71 + 0.6)))
        if b70 <= lt < b70 + 0.6:
            q = ramp(lt, b70, b70 + 0.6)
            ntext(ctx, (clk_x, clk_y + 64), "CLICK", size=17, color=WARM,
                  a=int(255 * (1 - q)))
            motion_lines(ctx, clk_x, clk_y, -90, n=5, r0=44, r1=76,
                         color=AMBER, a=int(180 * (1 - q)), spread=60, w=2.5,
                         seed=4)

        if thawed:
            # frost breaks and the room restarts
            br = ramp(lt, b71, b71 + 0.6)
            if br < 1:
                for i in range(8):
                    ang = i * 45 + 11
                    p0 = polar(640, 360, 90 + 120 * br, ang)
                    p1 = polar(640, 360, 120 + 180 * br, ang)
                    nline(ctx, [p0, p1], CHALK, w=1.3,
                          a=int(150 * (1 - br)), jit=0, halo=0)
            ntext(ctx, (640, 172), "TIME RESUMED", size=18, color=GREEN,
                  a=int(255 * (1 - ramp(lt, b71, b71 + 1.3))))
            # warm machine steam wakes up
            for i in range(3):
                sx = 1124 + i * 6
                pts = [(sx, 414), (sx + 6 * math.sin(lt * 1.5 + i),
                                   390 - i * 8),
                       (sx - 6, 366 - i * 8)]
                nline(ctx, pts, CHALK, w=2, a=95, jit=1, halo=1.4)
        else:
            freeze_frame(ctx, 1.0, lt, a=255)

        # labels / sight gags
        if lt >= b80:
            q = ramp(lt, b80, b80 + 0.32)
            ntext(ctx, (438, 596), "SPLASH", size=18, color=AMBER,
                  a=int(255 * q))
        if lt >= b81:
            q = ramp(lt, b81, b81 + 0.4)
            ntext(ctx, (646, 474), "NOBODY SAW A THING", size=20, color=GREEN,
                  a=int(255 * q))
            checkmark(ctx, [476, 456, 508, 488], ramp(q, 0.15, 0.9),
                      color=GREEN, w=4)
            # every witness is suddenly fascinated by a phone
            for wx in (842, 1078):
                ctx.rrect([wx - 11, 452, wx + 11, 480], 3,
                          fill=(6, 18, 34, 240), outline=CYAN + (190,), w=2)
                nline(ctx, [(wx, 462), (wx + 5, 460)], CHALK, w=1.2,
                      a=160, jit=0, halo=0)

        pause_badge(ctx, abs_t, f_abs, thaw_abs, center=(640, 72), r=42)


# ------------------------------------------------------------------ 5: camera


class CameraScene(Scene):
    id = "camera"
    FEED = (76, 104, 592, 364)

    def build(self):
        self.bg = party_bg()

    def draw(self, ctx, lt):
        b90, b91 = self.beat(9, 0), self.beat(9, 1)
        b100, b101 = self.beat(10, 0), self.beat(10, 1)
        b110, b111 = self.beat(11, 0), self.beat(11, 1)
        t = lt

        # hero, trying to look normal while the evidence plays
        deadpan = lt >= b100
        person(ctx, 540, 650, 2.35, POSE_INNOCENT if deadpan else POSE_POSE_2,
               color=CYAN, w=6.5, look=(0.25, -0.45),
               brow="flat", mouth=("flat" if lt < b111 else "grimace"))
        if lt >= b111:
            sweat(ctx, (500, 430), 18, color=CYAN)

        # camera beam + lens flare
        beam = ramp(lt, b90, b90 + 0.45)
        if beam > 0:
            alpha = int(34 * beam * (1 - 0.35 * ramp(lt, b110, b110 + 0.8)))
            ctx.poly([(1094, 120), (586, 636), (1254, 650)],
                     fill=NEON_RED + (alpha,))
            for i in range(3):
                nline(ctx, [(1094, 120), (650 + i * 190, 640)], NEON_RED,
                      w=1.2, a=int(65 * beam), jit=0, halo=0)
        ncircle(ctx, (1092, 120), 16, CHALK, w=3, a=230, fill=(5, 8, 16))
        ctx.circle((1092, 120), 7, fill=(CYAN if int(t * 2) % 2 == 0 else
                                         (10, 30, 44)) + (220,))
        lx = 1174
        if int(t * 2) % 2 == 0:
            ncircle(ctx, (lx, 102), 5, NEON_RED, w=2, a=245, fill=NEON_RED)
        ntext(ctx, (1138, 174), "CAM 04", size=14,
              color=(NEON_RED if int(t * 2) % 2 == 0 else CHALK), a=210)

        # feed content: evidence reel
        phase = 0 if lt < b100 else (1 if lt < b111 else 2)
        self.cctv_feed(ctx, self.FEED, lt, phase, b90, b100, b110, b111)

        # labels beside the monitor
        if lt >= b90:
            q = ramp(lt, b90, b90 + 0.35)
            ntext(ctx, (334, 424), "THE ONE THING THAT NEVER FREEZES", size=15,
                  color=CHALK, a=int(230 * q))
        if lt >= b100:
            q = ramp(lt, b100, b100 + 0.4)
            ntext(ctx, (640, 424), "REC  //  NO PAUSE BUTTON", size=17,
                  color=NEON_RED, a=int(245 * q))
        if lt >= b110:
            q = ramp(lt, b110, b110 + 0.35)
            ntext(ctx, (630, 462), "PLAYBACK: 1.0x", size=16, color=GOLD,
                  a=int(255 * q))
        if lt >= b111:
            q = ramp(lt, b111, b111 + 0.4)
            ntext(ctx, (952, 218), "STAFF PARTY", size=31, color=CREAM,
                  a=int(255 * q))
            ntext(ctx, (952, 250), "TONIGHT  //  8 PM", size=14, color=AMBER,
                  a=int(230 * q))
            # bunting lights blaze for the party
            for i in range(9):
                bx = 780 + i * 54
                by = 170 + 22 * math.sin(i * 0.65)
                sparkle(ctx, (bx, by), 4 + 2 * pulse(lt + i, 1.1),
                        color=(AMBER, CYAN, MAGENTA)[i % 3] +
                        (int(210 * q),))

        # staff: three co-workers, increasingly delighted by the footage
        staff = ((792, 2.02, 0.0), (956, 1.98, 0.9), (1126, 2.06, 1.8))
        for i, (x, s, ph) in enumerate(staff):
            bounce = (3.5 * math.sin(lt * 3.1 + ph) * ramp(lt, b111, b111 + 0.5))
            laugh = lt >= b111
            p = POSE_THUMBS if i == 1 else POSE_HOLD_CUP
            mood = "smile" if laugh else "flat"
            person(ctx, x, 650 + bounce, s, p, color=CHALK, w=5,
                   look=(-0.55, -0.1), brow=("up" if laugh else "flat"),
                   mouth=mood)
            if laugh:
                party_hat(ctx, (x, 650 + bounce - 88 * s - 8), 
                          (MAGENTA, CYAN, AMBER)[i], a=235)
                # raised party cup
                hx, hy = x + 30 * s, 650 + bounce - 50 * s
                coffee_cup(ctx, (hx, hy), size=10, tilt=-0.2, a=220,
                           cream=CHALK)
        # one of them holds up a phone to record the replay
        if lt >= b100:
            nline(ctx, [(968, 488), (994, 466)], CHALK, w=2, a=120, jit=0,
                  halo=0)

        # confetti on the final line
        if lt >= b111:
            q = ramp(lt, b111, b111 + 0.9)
            for i in range(14):
                px = 700 + (i * 97) % 520
                py = 230 + (i * 43) % 160 + 42 * ((lt * 0.4 + i) % 1)
                col = (AMBER, CYAN, MAGENTA, GREEN)[i % 4]
                nline(ctx, [(px, py), (px + 5, py + 9)], col, w=2,
                      a=int(180 * (1 - q * 0.3)), jit=0, halo=1.0)

    def cctv_feed(self, ctx, box, lt, phase, b90, b100, b110, b111):
        x0, y0, x1, y1 = box
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        a = 245
        # screen texture / scan lines
        for yy in range(int(y0 + 6), int(y1 - 4), 11):
            nline(ctx, [(x0 + 4, yy), (x1 - 4, yy)], STEEL_DIM, w=1,
                  a=32, jit=0, halo=0)
        # HUD corners
        for ax, ay, sx, sy in ((x0 + 10, y0 + 10, 1, 1),
                               (x1 - 10, y0 + 10, -1, 1),
                               (x0 + 10, y1 - 10, 1, -1),
                               (x1 - 10, y1 - 10, -1, -1)):
            nline(ctx, [(ax, ay + sy * 16), (ax, ay), (ax + sx * 16, ay)],
                  CHALK, w=1.5, a=130, jit=0, halo=0)
        rec = (int(lt * 2) % 2 == 0)
        if rec:
            ctx.circle((x0 + 28, y0 + 26), 5, fill=NEON_RED + (235,))
        ntext(ctx, (x0 + 40, y0 + 26), "REC", size=11, color=NEON_RED,
              a=230, anchor="lm")
        ntext(ctx, (x1 - 18, y0 + 26), "CAM 04", size=11, color=CHALK,
              a=180, anchor="rm")

        if phase == 0:
            # the room from above + the hero posing
            nline(ctx, [(x0 + 18, y1 - 26), (x1 - 18, y1 - 26)], STEEL,
                  w=2, a=115, jit=0, halo=0)
            person(ctx, cx - 28, y1 - 36, 1.0, POSE_POSE_2, color=CREAM,
                   w=3.5, look=(0.0, 0.0), brow="up", mouth="smile")
            ncircle(ctx, (cx, cy), 58, CYAN, w=1.5, a=135)
            nline(ctx, [(cx - 80, cy), (cx + 80, cy)], CYAN, w=1.2,
                  a=100, jit=0, halo=0)
            nline(ctx, [(cx, cy - 72), (cx, cy + 72)], CYAN, w=1.2,
                  a=100, jit=0, halo=0)
            ntext(ctx, (x0 + 22, y1 - 12), "LIVE", size=10, color=GREEN,
                  a=200, anchor="lm")
        elif phase == 1:
            # three freeze-frame exhibits with timestamps
            tags = (("10:42", "THE POSE"), ("10:47", "THE MEETING"),
                    ("10:53", "THE HAIRCUT"))
            for i, (tc, label) in enumerate(tags):
                bx0 = x0 + 10 + i * (x1 - x0 - 20) / 3
                bx1 = bx0 + (x1 - x0 - 28) / 3
                nrrect(ctx, [bx0, y0 + 40, bx1, y1 - 28], 3, STEEL,
                       w=1.2, a=125, fill=(6, 11, 21))
                ntext(ctx, ((bx0 + bx1) / 2, y0 + 50), label, size=8,
                      color=CHALK, a=190)
                if i == 0:
                    person(ctx, (bx0 + bx1) / 2, y1 - 48, 0.72, POSE_POSE_2,
                           color=CREAM, w=2.5, look=(0.0, 0.0), brow="up",
                           mouth="smile")
                elif i == 1:
                    nline(ctx, [(bx0 + 12, y0 + 76), (bx1 - 12, y0 + 76)],
                          CYAN, w=2, a=170, jit=0, halo=1.0)
                    ntext(ctx, ((bx0 + bx1) / 2, y0 + 92), "Q3", size=11,
                          color=CREAM, a=200)
                    for k in range(3):
                        nline(ctx, [(bx0 + 18 + k * 17, y1 - 54),
                                    (bx0 + 18 + k * 17, y1 - 78 - k * 5)],
                              CYAN, w=5, a=140, jit=0, halo=1.0)
                else:
                    ncircle(ctx, ((bx0 + bx1) / 2, y1 - 92), 16, CREAM,
                            w=2.4, a=210)
                    bad_hair(ctx, ((bx0 + bx1) / 2, y1 - 92), 16, a=210)
                ntext(ctx, (bx0 + 5, y1 - 33), tc, size=7, color=AMBER,
                      a=160, anchor="lm")
            ntext(ctx, ((x0 + x1) / 2, y0 + 31), "ALL OF IT  //  1x", size=10,
                  color=GOLD, a=220)
        else:
            # playback at normal speed
            ntext(ctx, (cx, y0 + 42), "PLAYBACK  1.0x", size=13, color=GOLD,
                  a=230)
            nline(ctx, [(x0 + 24, y1 - 34), (x1 - 24, y1 - 34)], STEEL,
                  w=4, a=120, jit=0, halo=0)
            for i in range(8):
                bx = x0 + 24 + i * (x1 - x0 - 48) / 8
                nline(ctx, [(bx, y1 - 41), (bx, y1 - 27)], CHALK, w=1.2,
                      a=90, jit=0, halo=0)
            # mini hero, looping the pose
            bob = 2 * math.sin(lt * 3.5)
            person(ctx, cx - 30, y1 - 46 + bob, 1.35, POSE_POSE_2,
                   color=CREAM, w=4, look=(0.0, 0.0), brow="up", mouth="smile")
            ntext(ctx, (x1 - 22, y1 - 16), "SPEED: NORMAL", size=8,
                  color=GREEN, a=185, anchor="rm")
            ntext(ctx, (x0 + 22, y1 - 16), "REC  //  STAFF PARTY", size=8,
                  color=NEON_RED, a=185, anchor="lm")


# ------------------------------------------------------------------ registry

SCENES = {cls.id: cls for cls in
          (SpillScene, PoseScene, FixesScene, ResumeScene, CameraScene)}