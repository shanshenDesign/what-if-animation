"""The six scenes of the 2 AM episode.

Each scene pre-renders a static background once (build) and then draws its
animated layer per frame (draw). Beats are anchored to caption chunks from
build/timeline.json, so picture changes land on the spoken words.
"""
import math

from PIL import Image, ImageChops, ImageDraw

from common import (BLUE, CREAM, GOLD, GREEN, INK, NIGHT_BOT, NIGHT_TOP,
                    PAPER, PINK, PINK_DEEP, RED, SS, W, W2, H, H2, WARM, WHITE,
                    clamp, ease_in, ease_in_out, ease_out, ease_out_back,
                    lerp, ramp, smoothstep)
from stick import (Ctx, POSE_CHEST, POSE_REACH, POSE_SIT, POSE_WAVE,
                   POSE_WAVE_DOWN, face, figure, sparkle, sweat, walk_pose)

# ------------------------------------------------------------------ helpers


def gradient(w, h, top, bottom):
    strip = Image.new("RGB", (1, h))
    px = []
    for i in range(h):
        t = i / max(1, h - 1)
        px.append(tuple(int(top[c] + (bottom[c] - top[c]) * t) for c in range(3)))
    strip.putdata(px)
    return strip.resize((w * SS, h * SS), Image.BILINEAR)


def clip_ellipse(base, box, fn):
    """Draw fn (1x coords) on a transparent layer, clipped to an ellipse box."""
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    fn(Ctx(lay))
    mask = Image.new("L", base.size, 0)
    ImageDraw.Draw(mask).ellipse([box[0] * SS, box[1] * SS,
                                  box[2] * SS, box[3] * SS], fill=255)
    lay.putalpha(ImageChops.multiply(lay.getchannel("A"), mask))
    base.paste(lay, (0, 0), lay)


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


def ghost(ctx, c, r, alpha=235):
    """Pink cringe-memory blob: dome, scalloped hem, wavy embarrassed mouth."""
    a = int(clamp(alpha, 0, 255))
    if a <= 2:
        return
    body = tuple(PINK[:3]) + (a,)
    pts = []
    for deg in range(180, 361, 15):
        pts.append(polar(c[0], c[1], r, deg))
    n = 4
    for i in range(n + 1):
        x = c[0] + r - (2 * r) * i / n
        y = c[1] + r * (0.62 if i % 2 else 0.95)
        pts.append((x, y))
    ctx.poly(pts, fill=body)
    for sx in (-1, 1):
        ex = c[0] + sx * 0.34 * r
        ey = c[1] - 0.14 * r
        ctx.circle((ex, ey), 0.18 * r, fill=tuple(WHITE) + (a,))
        ctx.dot((ex, ey + 0.04 * r), 0.17 * r, fill=tuple(INK) + (a,))
    mouth = []
    for i in range(5):
        mouth.append((c[0] - 0.34 * r + i * 0.17 * r,
                      c[1] + 0.30 * r + (0.12 * r if i % 2 else -0.02 * r)))
    ctx.line(mouth, fill=tuple(INK) + (a,), w=max(2.0, r * 0.09))


def waving_pose(t):
    p = {k: ([tuple(q) for q in v] if isinstance(v, list) else v)
         for k, v in POSE_WAVE.items()}
    ex, ey = 17.0, -84.0
    ang = math.radians(24 * math.sin(2 * math.pi * 2.1 * t))
    dx, dy = 30.0 - ex, -95.0 - ey
    p["armR"] = [(0, -72), (ex, ey),
                 (ex + dx * math.cos(ang) - dy * math.sin(ang),
                  ey + dx * math.sin(ang) + dy * math.cos(ang))]
    return p


def xmark(ctx, box, prog, color=RED, w=9):
    if prog <= 0:
        return
    x0, y0, x1, y1 = box
    for ax, ay, bx, by in ((x0, y0, x1, y1), (x1, y0, x0, y1)):
        ctx.line([(ax, ay), (lerp(ax, bx, prog), lerp(ay, by, prog))],
                 fill=tuple(color) + (255,), w=w)


def clock_text(ctx, txt, alpha=255):
    ctx.text((478, 439), txt, size=30, fill=tuple(WARM) + (int(alpha),),
             anchor="mm", bold=True)


# ------------------------------------------------------------------ bedroom


def bedroom(sky="night"):
    img = Image.new("RGB", (W2, H2))
    img.paste(gradient(W, H, NIGHT_TOP, NIGHT_BOT), (0, 0))
    ctx = Ctx(img)
    # floor
    ctx.poly([(0, 560), (W, 560), (W, H), (0, H)], fill=(12, 14, 30))
    ctx.line([(0, 560), (W, 560)], fill=(46, 52, 96), w=5)
    # window
    ctx.rrect([84, 84, 306, 336], 10, fill=(9, 10, 24), outline=(52, 58, 104), w=6)
    if sky == "night":
        ctx.rrect([96, 96, 294, 324], 6, fill=(26, 30, 68))
        ctx.circle((238, 150), 27, fill=(250, 240, 205))
        ctx.circle((225, 140), 23, fill=(26, 30, 68))
        for sx, sy, sr in ((132, 132, 3), (172, 196, 2.4), (256, 244, 2.4),
                           (124, 262, 2), (216, 300, 2)):
            ctx.dot((sx, sy), sr * 2, fill=(226, 232, 255, 210))
    else:
        ctx.rrect([96, 96, 294, 324], 6, fill=(255, 204, 154))
        ctx.circle((150, 302), 27, fill=(255, 246, 204))
        ctx.circle((222, 164), 34, fill=(255, 232, 196, 210))
        ctx.circle((262, 172), 22, fill=(255, 232, 196, 210))
    ctx.line([(195, 96), (195, 324)], fill=(52, 58, 104), w=5)
    ctx.line([(96, 210), (294, 210)], fill=(52, 58, 104), w=5)
    ctx.line([(78, 336), (312, 336)], fill=(58, 66, 120), w=7)
    # warm wall lamp
    ctx.poly([(440, 318), (500, 318), (491, 292), (449, 292)], fill=WARM)
    ctx.glow((470, 314), 95, WARM, alpha=46, rings=5)
    ctx.dot((470, 321), 9, fill=(255, 247, 216))
    # bed
    ctx.rrect([612, 300, 666, 568], 8, fill=(35, 40, 73), outline=(58, 64, 118), w=4)
    ctx.rrect([650, 424, 1192, 548], 14, fill=(43, 49, 89), outline=(58, 64, 118), w=4)
    ctx.rrect([790, 414, 1192, 540], 16, fill=(58, 66, 115))
    ctx.line([(802, 436), (1180, 436)], fill=(74, 84, 140), w=4)
    ctx.rrect([676, 392, 806, 448], 16, fill=(230, 221, 201))
    # nightstand + clock frame (digits are drawn per frame)
    ctx.rrect([388, 468, 572, 564], 8, fill=(35, 40, 73), outline=(58, 64, 118), w=4)
    ctx.line([(388, 478), (572, 478)], fill=(58, 64, 118), w=4)
    ctx.rrect([416, 416, 540, 462], 8, fill=(14, 16, 36), outline=(74, 84, 140), w=3)
    return img


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


# ------------------------------------------------------------------ 1: bed


class BedScene(Scene):
    id = "bed"

    def build(self):
        self.bg = bedroom("night")

    def draw(self, ctx, lt):
        breath = 2.2 * math.sin(2 * math.pi * lt / 3.4)
        closed = ((lt + 0.35) % 1.15) < 0.09
        gx = 0.5 * math.sin(lt * 2.6)
        b1, b2 = self.beat(0, 1), self.beat(0, 2)
        if lt >= b2:
            brow, mouth, look = "up", ("o" if lt < b2 + 0.7 else "flat"), (0.0, -0.7)
        elif lt >= b1:
            brow, mouth, look = "flat", "flat", (-gx, -0.4)
        else:
            brow, mouth, look = "flat", "flat", (gx, -0.3)
        lying_figure(ctx, breath, closed, look, brow, mouth)

        # clock flicker
        txt, a = "2:00", 255
        f = lt - (self.beat(0, 0) + 0.05)
        if 0 <= f < 0.45:
            a = 140 + 115 * abs(math.sin(f * 42))
        clock_text(ctx, txt, a)

        # thought seed forming over his head
        s = ramp(lt, self.beat(0, 2), self.beat(0, 2) + 0.9)
        if s > 0:
            for (dx, dy, r) in ((55, -26, 10), (101, -58, 14), (155, -94, 19)):
                sc = clamp(s * 1.15 - r / 60.0)
                if sc > 0:
                    ctx.circle((735 + dx, 400 + dy), r * sc,
                               outline=CREAM, w=5)


# ------------------------------------------------------------------ 2: wave


class WaveScene(Scene):
    id = "wave"
    BUBBLE = [240, 60, 1040, 500]

    def build(self):
        self.bg = Image.new("RGB", (W2, H2))
        self.bg.paste(gradient(W, H, NIGHT_TOP, (9, 11, 26)), (0, 0))

    def draw(self, ctx, lt):
        b = self.beat(1, 0)
        bdrop = self.beat(1, 1) + 0.6
        end = self.line_end(1) + 0.6

        if lt >= b:
            s = lerp(0.12, 1.0, ease_out_back(ramp(lt, b, b + 0.5)))
            box = scaled_box(self.BUBBLE, s)

            def contents(c):
                c.ellipse(box, fill=PAPER)
                c.line([(300, 430), (990, 430)], fill=(154, 142, 116), w=6)
                # the guy waving — smiles, then deflates when she keeps walking
                drop = ramp(lt, bdrop, bdrop + 0.4)
                pose = blend_pose(waving_pose(lt), POSE_WAVE_DOWN, drop)
                figure(c, 470, 430, 1.65, pose, w=4.5, color=(74, 62, 52))
                whx, why, _ = pose["head"]
                face(c, (470 + whx * 1.65, 430 + why * 1.65), 12 * 1.65,
                     look=(0.45, 0.05), brow="sad" if drop > 0.5 else "up",
                     mouth="frown" if drop > 0.5 else "smile", w=3.4)
                # the person who keeps walking
                px = lerp(585, 905, ramp(lt, b, end))
                figure(c, px, 430, 1.65, walk_pose((px / 95.0) % 1.0),
                       w=4.5, color=(74, 62, 52))
                face(c, (px, 430 - 88 * 1.65), 12 * 1.65, look=(0.5, 0),
                     brow="flat", mouth="flat", w=3.4)

            clip_ellipse(ctx.img, box, contents)
            ctx.ellipse(box, outline=CREAM, w=7)

        # trail from his head up to the bubble edge (kept outside the ellipse)
        if lt >= b:
            for i, (dx, dy, r, at) in enumerate((
                    (85, -65, 9, 0.0), (125, -95, 12, 0.12), (165, -105, 15, 0.24))):
                sc = clamp(ramp(lt, b + at, b + at + 0.3))
                if sc > 0:
                    ctx.circle((250 + dx, 570 + dy), r * sc, outline=CREAM, w=5)

        # close-up of his own head, bottom left
        chin_y = 570
        ctx.line([(250, 672), (142, 720)], fill=CREAM, w=12)
        ctx.line([(250, 672), (372, 720)], fill=CREAM, w=12)
        ctx.circle((250, chin_y), 100, outline=CREAM, w=13)
        b1 = self.beat(1, 1)
        if lt >= b1 + 0.6:
            brow, mouth, look, sweat_on = "sad", "frown", (0.55, -0.5), True
        elif lt >= b1:
            brow, mouth, look, sweat_on = "up", "flat", (0.55, -0.6), False
        else:
            brow, mouth, look, sweat_on = "up", "flat", (0.55, -0.65), False
        face(ctx, (250, chin_y), 100, look=look, brow=brow, mouth=mouth,
             color=CREAM, w=7)
        if sweat_on:
            sweat(ctx, (366, 476), 30)

# ------------------------------------------------------------------ 3: bouncer


class BouncerScene(Scene):
    id = "bouncer"
    DOOR = (470, 180, 700, 560)

    def build(self):
        img = Image.new("RGB", (W2, H2))
        img.paste(gradient(W, H, (13, 15, 34), (26, 29, 58)), (0, 0))
        ctx = Ctx(img)
        ctx.poly([(0, 560), (W, 560), (W, H), (0, H)], fill=(10, 11, 24))
        ctx.line([(0, 560), (W, 560)], fill=(44, 50, 92), w=5)
        ctx.rrect(list(self.DOOR), 6, fill=(6, 7, 16), outline=(58, 64, 118), w=7)
        # sign over the door
        ctx.glow((586, 122), 96, GOLD, alpha=34, rings=4)
        ctx.rrect([430, 76, 742, 168], 12, fill=(14, 16, 36),
                  outline=tuple(GOLD) + (170,), w=4)
        ctx.text((586, 111), "PREFRONTAL", size=26, anchor="mm", bold=True, fill=GOLD)
        ctx.text((586, 147), "CORTEX", size=26, anchor="mm", bold=True, fill=GOLD)
        self.bg = img

    def draw(self, ctx, lt):
        open_t = self.beat(2, 2)
        o = ease_in_out(ramp(lt, open_t + 0.5, open_t + 1.7))

        # pink spill through the opening
        if o > 0:
            ctx.glow((586, 400), 175, PINK, alpha=int(120 * o), rings=5)
            ctx.poly([(492, 560), (688, 560), (748, 720), (430, 720)],
                     fill=tuple(PINK) + (int(46 * o),))
        # door panel swings out past its left hinge
        fx = 700 - 272 * o
        ctx.poly([(470, 181), (fx, 174), (fx, 566), (470, 559)],
                 fill=(35, 40, 73), outline=(58, 64, 118), w=5)
        kx = 470 + (fx - 470) * 0.86
        ctx.circle((kx, 372), 9, fill=(196, 168, 110))

        # the bouncer clocks out
        w0 = self.beat(2, 2) + 0.2
        wp = ramp(lt, w0, w0 + 1.9)
        if wp < 1.0:
            x = 820 + 560 * wp
            pose = walk_pose((x / 95.0) % 1.0)
            hx, hy = pose["armR"][-1]
            pose["props"] = [
                ("poly", [(0, -70), (-6, -58), (0, -50), (6, -58)], RED),
                ("rrect", (hx - 4, hy + 3, hx + 22, hy + 17), 3, (198, 161, 104)),
            ]
            figure(ctx, x, 560, 3.4, pose, w=7, color=CREAM)
            face(ctx, (x + 2 * 3.4, 560 - 88 * 3.4), 12 * 3.4,
                 look=(0.6 if wp > 0 else 0.1, 0), brow="flat", mouth="flat",
                 color=CREAM, w=5)

        # blocked memories flood out
        g0 = self.beat(3, 0)
        for i in range(5):
            born = g0 + i * 0.34
            tt = lt - born
            if tt <= 0:
                continue
            travel = ramp(lt, born, born + 3.0) ** 1.5
            gx = lerp(585, 1335, travel)
            gy = 398 + 58 * math.sin(lt * 1.9 + i * 2.1)
            a = 235 * clamp(tt / 0.35) * (1 - ramp(gx, 1140, 1335))
            ghost(ctx, (gx, gy), 40 + i * 5, alpha=a)

    def shake(self, lt):
        d = lt - (self.beat(3, 1) + 0.1)
        if 0 <= d < 0.4:
            a = 5 * (1 - d / 0.4)
            return (a * math.sin(lt * 66), a * 0.5 * math.cos(lt * 58))
        return (0.0, 0.0)


# ------------------------------------------------------------------ 4: stage


def draw_brain(ctx, cx, cy, r, kind="shout", limbs=True, scale=1.0):
    rr = r * max(0.05, scale)
    for k in range(7):
        ctx.circle(polar(cx, cy, rr * 0.86, k * (360 / 7) + 14), rr * 0.34,
                   fill=PINK, outline=PINK_DEEP, w=4)
    ctx.circle((cx, cy), rr, fill=PINK, outline=PINK_DEEP, w=4)
    ctx.arc([cx - rr * 0.66, cy - rr * 0.6, cx + rr * 0.02, cy + rr * 0.28],
            30, 250, fill=PINK_DEEP, w=4)
    ctx.arc([cx + rr * 0.12, cy - rr * 0.16, cx + rr * 0.62, cy + rr * 0.52],
            210, 340, fill=PINK_DEEP, w=4)
    if limbs:
        ctx.line([(cx - 0.32 * rr, cy + 0.8 * rr), (cx - 0.36 * rr, cy + 1.12 * rr),
                  (cx - 0.56 * rr, cy + 1.16 * rr)], fill=PINK, w=7)
        ctx.line([(cx + 0.32 * rr, cy + 0.8 * rr), (cx + 0.36 * rr, cy + 1.12 * rr),
                  (cx + 0.56 * rr, cy + 1.16 * rr)], fill=PINK, w=7)
        ctx.line([(cx - 0.95 * rr, cy + 0.1 * rr), (cx - 1.16 * rr, cy + 0.5 * rr),
                  (cx - 1.06 * rr, cy + 0.82 * rr)], fill=PINK, w=7)
        ctx.line([(cx + 0.95 * rr, cy - 0.05 * rr), (cx + 1.26 * rr, cy - 0.2 * rr),
                  (cx + 1.5 * rr, cy - 0.35 * rr)], fill=PINK, w=7)
    # face
    for sx in (-1, 1):
        ex, ey = cx + sx * 0.36 * rr, cy - 0.1 * rr
        ctx.circle((ex, ey), 0.23 * rr, fill=WHITE, outline=INK, w=3)
        ctx.dot((ex + 0.07 * rr, ey + 0.03 * rr), 0.2 * rr, fill=INK)
        bx, by = cx + sx * 0.36 * rr, cy - 0.44 * rr
        ctx.line([(bx - 0.2 * rr, by + 0.1 * rr * sx),
                  (bx + 0.2 * rr, by - 0.1 * rr * sx)], fill=INK, w=4)
    if kind == "shout":
        ctx.ellipse([cx - 0.2 * rr, cy + 0.28 * rr, cx + 0.2 * rr, cy + 0.56 * rr],
                    fill=(122, 30, 62), outline=INK, w=3)
    else:
        ctx.arc([cx - 0.3 * rr, cy + 0.22 * rr, cx + 0.3 * rr, cy + 0.54 * rr],
                20, 160, fill=INK, w=max(2.0, rr * 0.07))


def draw_icon(c, kind, cx, cy, a):
    if kind == "sun":
        c.circle((cx, cy), 17, outline=tuple(WARM) + (int(255 * a),), w=5)
        for k in range(8):
            c.line([polar(cx, cy, 26, k * 45), polar(cx, cy, 37, k * 45)],
                   fill=tuple(WARM) + (int(255 * a),), w=4)
    elif kind == "list":
        c.rrect([cx - 26, cy - 30, cx + 26, cy + 30], 6,
                outline=tuple(WHITE) + (int(255 * a),), w=4)
        for k in range(3):
            yy = cy - 14 + k * 14
            c.line([(cx - 14, yy), (cx + 16, yy)],
                   fill=tuple(WHITE) + (int(205 * a),), w=4)
    else:
        c.rrect([cx - 16, cy - 30, cx + 16, cy + 30], 6,
                outline=tuple(BLUE) + (int(255 * a),), w=4)
        c.line([(cx - 7, cy - 21), (cx + 7, cy - 21)],
               fill=tuple(BLUE) + (int(215 * a),), w=4)
        c.dot((cx, cy + 20), 9, fill=tuple(BLUE) + (int(215 * a),))


class StageScene(Scene):
    id = "stage"
    ICON_X = (300, 640, 980)

    def build(self):
        img = Image.new("RGB", (W2, H2))
        img.paste(gradient(W, H, (10, 12, 27), (23, 26, 55)), (0, 0))
        ctx = Ctx(img)
        ctx.poly([(640, -40), (250, 720), (1030, 720)], fill=(255, 244, 214, 24))
        ctx.poly([(640, -40), (420, 720), (860, 720)], fill=(255, 244, 214, 18))
        ctx.ellipse([340, 524, 940, 624], fill=(29, 33, 69), outline=(58, 64, 118), w=5)
        ctx.arc([340, 524, 940, 624], 180, 360, fill=(96, 106, 178), w=4)
        self.bg = img

    def draw(self, ctx, lt):
        # three things daylight and tasks and distraction would be doing
        icons_t = self.beat(4, 0)
        for i, kind in enumerate(("sun", "list", "phone")):
            vis = ramp(lt, icons_t + i * 0.15, icons_t + i * 0.15 + 0.3)
            if vis <= 0:
                continue
            cx = self.ICON_X[i]
            cy = 122 - 16 * (1 - vis)
            ctx.rrect([cx - 85, cy - 52, cx + 85, cy + 52], 14,
                      fill=(255, 255, 255, int(26 * vis)),
                      outline=(255, 255, 255, int(85 * vis)), w=3)
            draw_icon(ctx, kind, cx, cy, vis)
        for i, xt in enumerate((icons_t + 0.45, icons_t + 0.92,
                                self.beat(4, 1) + 0.15)):
            p = ramp(lt, xt, xt + 0.18)
            if p > 0:
                cx = self.ICON_X[i]
                xmark(ctx, [cx - 66, 76, cx + 66, 172], p, w=10)

        # the brain on stage with a megaphone
        dy = 0.0
        loop_t = self.beat(5, 2)
        if lt >= loop_t:
            dy = -6 * abs(math.sin((lt - loop_t) * 4.0))
        cy = 430 + dy
        draw_brain(ctx, 640, cy, 85, kind="shout")
        ctx.line([(767, cy - 30), (786, cy - 32)], fill=INK, w=6)
        ctx.poly([(786, cy - 52), (900, cy - 88), (900, cy + 26), (786, cy - 14)],
                 fill=WARM, outline=INK, w=5)
        ctx.line([(900, cy - 88), (900, cy + 26)], fill=INK, w=7)

        # megaphone rings while it is loud
        loud = ramp(lt, self.beat(5, 1), self.beat(5, 1) + 0.3)
        for i, rr2 in enumerate((64, 106, 148)):
            ph = (lt * 1.6 - i * 0.33) % 1.0
            a = int(215 * loud * clamp(1.25 - ph * 1.45))
            if a > 6:
                ctx.arc([915 - rr2, cy - 31 - rr2, 915 + rr2, cy - 31 + rr2],
                        -52, 52, fill=tuple(GOLD) + (a,), w=6)

        # "as urgent." -> the stamp
        st = self.beat(4, 3) + 0.1
        if lt >= st:
            sc = lerp(1.55, 1.0, ease_out_back(ramp(lt, st, st + 0.35)))
            al = ramp(lt, st, st + 0.1)

            def card(c):
                c.rrect([950, 296, 1240, 474], 18, fill=(255, 255, 255, int(240 * al)),
                        outline=tuple(RED) + (int(255 * al),), w=8)
                c.text((1095, 366), "URGENT", size=54, fill=tuple(RED) + (int(255 * al),),
                       anchor="mm", bold=True, stroke=2,
                       stroke_fill=(255, 255, 255, int(235 * al)))
                c.line([(988, 412), (1202, 412)], fill=tuple(RED) + (int(150 * al),), w=4)
                c.text((1095, 442), "2:00 AM", size=24,
                       fill=tuple(INK) + (int(215 * al),), anchor="mm", bold=True)

            overlay(ctx.img, card, angle=-7, scale=sc)

        # "On loop." -> a dashed ring going round
        if lt >= loop_t:
            p = lt - loop_t
            rr3 = 197
            for k in range(16):
                a0 = p * 140 + k * 22.5
                ctx.arc([640 - rr3, cy - rr3, 640 + rr3, cy + rr3], a0, a0 + 12,
                        fill=tuple(GOLD) + (225,), w=6)
            ah = p * 140 + 15 * 22.5 + 14
            ctx.poly([polar(640, cy, rr3, ah + 9), polar(640, cy, rr3 + 14, ah - 6),
                      polar(640, cy, rr3 - 14, ah - 6)], fill=GOLD)

    def shake(self, lt):
        amp = 0.0
        for b in (self.beat(4, 3) + 0.1, self.beat(5, 1)):
            d = lt - b
            if 0 <= d < 0.55:
                amp = max(amp, 10 * (1 - d / 0.55))
        if amp <= 0:
            return (0.0, 0.0)
        return (amp * math.sin(lt * 74), amp * 0.6 * math.cos(lt * 61))

# ------------------------------------------------------------------ shared


def lying_figure(ctx, breath, closed, look, brow, mouth, hx=735.0, hy=400.0):
    """Him, flat on his back, arm on the blanket."""
    ctx.line([(768, 432), (812, 438 + breath * 0.5)], fill=CREAM, w=10)
    ctx.line([(812, 438 + breath * 0.5), (872, 416 + breath)], fill=CREAM, w=9)
    ctx.line([(872, 416 + breath), (926, 430 + breath)], fill=CREAM, w=9)
    ctx.dot((932, 431 + breath), 19, fill=CREAM)
    ctx.circle((hx, hy), 40, outline=CREAM, w=10)
    face(ctx, (hx, hy), 40, look=look, closed=closed, brow=brow,
         mouth=mouth, w=4.5)


# ------------------------------------------------------------------ 5: fix


class FixScene(Scene):
    id = "fix"
    X, Y, S = 900.0, 560.0, 3.1
    PHONE = [978, 416, 1052, 448]

    def build(self):
        self.bg = bedroom("night")

    def draw(self, ctx, lt):
        reach_t, sit_t = self.beat(6, 1), self.beat(7, 0)
        calm_t = self.beat(7, 2)

        # the phone, glowing next to him
        glow_a = lerp(1.0, 0.22, ramp(lt, reach_t, reach_t + 0.6))
        ctx.glow((1015, 432), 76, BLUE, alpha=int(100 * glow_a), rings=5)
        ctx.rrect(list(self.PHONE), 8, fill=(16, 18, 40), outline=(66, 78, 124), w=3)
        ctx.rrect([986, 422, 1044, 442], 4,
                  fill=(74, 116, 208, int(235 * glow_a)))
        clock_text(ctx, "2:00")

        # pose chain: reaching -> arm back -> hand on chest
        if lt < reach_t:
            pose = POSE_REACH
        elif lt < sit_t:
            pose = blend_pose(POSE_REACH, POSE_SIT, ramp(lt, reach_t, reach_t + 0.45))
        else:
            pose = blend_pose(POSE_SIT, POSE_CHEST, ramp(lt, sit_t, sit_t + 0.6))
        br = 0.0
        if lt >= sit_t:
            br = -2.4 * (0.5 - 0.5 * math.cos(2 * math.pi * (lt - sit_t) / 1.6))
        figure(ctx, self.X, self.Y + br, self.S, pose, w=7)

        hx = self.X + pose["head"][0] * self.S
        hy = self.Y + pose["head"][1] * self.S + br
        if lt < sit_t:
            closed = False
            look, brow = (0.6, 0.15), ("up" if lt < reach_t else "flat")
            mouth = "smile" if lt >= reach_t else "flat"
        else:
            closed = True
            look, brow = (0, 0), "flat"
            mouth = "smile" if lt >= calm_t + 0.5 else "flat"
        face(ctx, (hx, hy), 12 * self.S, look=look, closed=closed,
             brow=brow, mouth=mouth, color=CREAM, w=5.5)

        # red X over the phone on "Not your phone."
        p = ramp(lt, reach_t + 0.12, reach_t + 0.32)
        if p > 0:
            xmark(ctx, [962, 400, 1068, 464], p, w=10)

        # breathing ring
        if lt >= sit_t:
            osc = 0.5 - 0.5 * math.cos(2 * math.pi * (lt - sit_t) / 1.6)
            ctx.circle((912, 384 + br), 46 + 20 * osc,
                       fill=tuple(GREEN) + (28,), outline=tuple(GREEN) + (175,), w=6)

        # "Name it." the memory shows up; "Let it pass." it dissolves
        g1, g2 = self.beat(7, 1), self.beat(7, 2)
        if lt >= g1:
            rise = 56 * ramp(lt, g1, g2 + 1.1)
            a = 232 * clamp((lt - g1) / 0.4) * (1 - ramp(lt, g2, g2 + 0.9))
            gx = 1052 + 10 * math.sin(lt * 2.0)
            ghost(ctx, (gx, 258 - rise), 44, alpha=a)
            pr = ramp(lt, g2, g2 + 1.0)
            if 0 < pr < 1:
                for k in range(8):
                    sp = polar(gx, 258 - rise, 30 + 76 * pr, k * 45 + 22)
                    sparkle(ctx, sp, 9 - 5 * pr,
                            color=tuple(GOLD) + (int(235 * (1 - pr)),))


# ------------------------------------------------------------------ 6: dawn


class DawnScene(Scene):
    id = "dawn"
    zoom_range = (1.05, 1.02)   # slow pull-out on the exhale

    def build(self):
        self.bg = bedroom("dawn")

    def draw(self, ctx, lt):
        p = clamp(lt / max(0.5, self.t1 - self.t0))
        b80, b90, b91 = self.beat(8, 0), self.beat(9, 0), self.beat(9, 1)
        b81 = self.beat(8, 1)

        # morning coming through the window
        ctx.glow((196, 300), 310, (255, 214, 168), alpha=int(10 + 34 * p), rings=5)
        ctx.poly([(110, 324), (282, 324), (436, 566), (142, 566)],
                 fill=(255, 214, 150, int(10 + 46 * p)))

        # him: eyes close on cue
        breath = 2.2 * math.sin(2 * math.pi * lt / 3.6)
        closed = lt >= b80 or ((lt + 0.5) % 1.6) < 0.07
        lying_figure(ctx, breath, closed,
                     (0.4, -0.5) if not closed else (0, 0),
                     "up" if lt < b80 else "flat",
                     "flat" if lt < b81 + 0.8 else "smile")

        # clock flips 2:00 -> 6:58
        txt, a = ("2:00", 255) if lt < b80 else ("6:58", 255)
        f = lt - b80
        if 0 <= f < 0.45:
            a = 140 + 115 * abs(math.sin(f * 42))
            txt = "6:58" if f > 0.22 else "2:00"
        clock_text(ctx, txt, a)

        # "It's just a memory." -> the cringe floats off into sparkles
        g_in = b80 + 0.2
        if lt >= g_in:
            rise = 52 * ramp(lt, g_in, b81 + 1.1)
            a = 225 * clamp((lt - g_in) / 0.4) * (1 - ramp(lt, b81, b81 + 0.9))
            gx = 1034 + 9 * math.sin(lt * 1.7)
            ghost(ctx, (gx, 272 - rise), 46, alpha=a)
            pr = ramp(lt, b81, b81 + 1.0)
            if 0 < pr < 1:
                for k in range(8):
                    sp = polar(gx, 272 - rise, 32 + 74 * pr, k * 45 + 18)
                    sparkle(ctx, sp, 9 - 5 * pr,
                            color=tuple(GOLD) + (int(235 * (1 - pr)),))

        # Zzz
        if lt >= b90:
            for i in range(3):
                ph = (lt * 44 + i * 36) % 112
                ctx.text((845 + i * 42, 348 - ph), "Z", size=26 + i * 9,
                         fill=tuple(CREAM) + (int(240 * (1 - ph / 112)),),
                         anchor="mm")

        # "your brain picks better." -> the brain itself says goodnight
        if lt >= b91:
            sc = ease_out_back(ramp(lt, b91, b91 + 0.5))
            bx, by = 1086.0, 214.0
            draw_brain(ctx, bx, by, 34, kind="smile", limbs=False,
                       scale=max(0.05, sc))
            if sc > 0.6:
                wig = 7 * math.sin(lt * 7)
                ctx.line([(bx + 30, by - 4), (bx + 52, by - 26 + wig)],
                         fill=PINK, w=6)
                ctx.dot((bx + 55, by - 29 + wig), 14, fill=PINK)
                sparkle(ctx, (bx + 58, by - 66), 11,
                        color=tuple(GOLD) + (240,))


# ------------------------------------------------------------------ registry

SCENES = {cls.id: cls for cls in
          (BedScene, WaveScene, BouncerScene, StageScene, FixScene, DawnScene)}


