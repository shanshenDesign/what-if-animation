"""The six scenes of the "hours-spent-scrolling" episode.

Topic: a girl behind the glass of your screen breaks the fourth wall, taps
on the glass, counts the hours you have burned scrolling, and finally
reaches for the switch that turns the screen off.
Style: screen-lit cinematic — sharp black silhouettes edged with
double-offset cyan, magenta and amber rim light, a room that sinks to
midnight while the monitor keeps glowing, floating short-video cards and
tall amber hour counters.

Beat flow:
    glass_tap_hook    close-up behind the cyan screen frame, knocks, calls you out
    thumb_loop_mirror medium shot, cards drift, her thumb keeps the rhythm
    clock_numbers_drop 1H / 3H / 5H+ counters stack behind her, deadpan
    room_fade_shadow  slow push-in, the room drops to shadow, rim on her face
    pause_quiet_beat  cards freeze and dim, she asks what you remember
    screen_off_choice reaches for the amber switch, one swipe, screen off

Every visual beat is keyed to a caption chunk via beat(line, chunk), so the
picture lands on the spoken words even if the narration runs long or short.
"""
import math

from PIL import Image

from stick import (Ctx, POSE_CALM, POSE_GESTURE_OPEN, POSE_HIP, POSE_POINT,
                   POSE_REACH, POSE_SOFT, POSE_SWIPE_DOWN, POSE_SWIPE_UP,
                   POSE_TAP, blink_closed, girl_silhouette)
from common import (CARD_BODY, CARD_CYAN, CARD_FROST, CARD_MAGENTA, CLOCK_RING,
                    CREAM, DUST, HORIZON_AMBER, HOUR_AMBER, HOUR_GLOW,
                    INK, NEON_AMBER, NEON_CYAN, NEON_MAGENTA, PAPER,
                    ROOM_DESK, ROOM_FLOOR, ROOM_MIDNIGHT, ROOM_WALL,
                    SCANLINE, SCREEN_SHEEN, SCREEN_TOP, STEEL, SWITCH_AMBER,
                    SWITCH_OFF, SWITCH_TRACK, W, H, W2, H2, WHITE,
                    clamp, dim, ease_in_out, ease_out, lerp, pulse, ramp)

# ------------------------------------------------------------------ poses
# Local units: feet / anchor at (0, 0), y negative = up. Poses face right.


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


# ---------------------------------------------------------------- speech

def speech_act(sc, t):
    """0..1 narration envelope: rises and falls inside the active caption."""
    for ln in sc.tl["lines"]:
        if ln["start"] <= t < ln["end"]:
            for cp in ln["caps"]:
                if cp["start"] <= t < cp["end"]:
                    u = (t - cp["start"]) / max(0.05, cp["end"] - cp["start"])
                    return math.sin(math.pi * clamp(u)) ** 0.4
    return 0.0


def talk(lt, sc, closed=False, idle="flat"):
    """Lip-sync: (openness 0..1, mouth shape) for the current caption."""
    if closed:
        return 0.0, idle
    t = sc.t0 + lt
    act = speech_act(sc, t)
    if act < 0.06:
        return 0.0, idle
    s1 = 0.5 + 0.5 * math.sin(2 * math.pi * 6.7 * t + 1.1)
    s2 = 0.5 + 0.5 * math.sin(2 * math.pi * 9.3 * t + 0.4)
    o = clamp(act * (0.30 + 0.70 * (0.62 * s1 + 0.38 * s2)))
    if o < 0.20:
        shape = "flat"
    elif s2 > 0.68:
        shape = "o"
    elif s1 > 0.62:
        shape = "wide"
    elif s1 < 0.28:
        shape = "u"
    else:
        shape = "open"
    return o, shape


# ---------------------------------------------------------------- props

def screen_frame(ctx, a=255, color=NEON_CYAN, inset=56, w=9, glow=True):
    """The bezel of the screen you are looking through."""
    box = [inset, inset, W - inset, H - inset]
    if glow:
        ctx.glow((W / 2, H / 2), 620, color, alpha=int(26 * a / 255))
    ctx.rrect(box, 26, outline=(0, 0, 0, int(a * 0.85)), w=w + 8)
    ctx.rrect(box, 26, outline=tuple(color[:3]) + (a,), w=w)
    for cx, cy, sx, sy in ((inset, inset, 1, 1), (W - inset, inset, -1, 1),
                           (inset, H - inset, 1, -1), (W - inset, H - inset, -1, -1)):
        ctx.line([(cx, cy + sy * 44), (cx, cy), (cx + sx * 44, cy)],
                 fill=tuple(color[:3]) + (a,), w=w + 3)


def scanlines(ctx, a=16, step=8, color=SCANLINE):
    """LCD scanlines on the glass surface (drawn above everything)."""
    for y in range(0, H, step):
        ctx.line([(0, y), (W, y)], fill=tuple(color) + (a,), w=1)


def video_card(ctx, x, y, w, h, color, a=255, fill_f=0.4, seed=0.0):
    """Floating translucent short-video card: body, glow, play glyph, bar."""
    aa = int(clamp(a, 0, 255))
    ctx.glow((x + w / 2, y + h / 2), max(w, h) * 0.8, color,
             alpha=int(34 * aa / 255))
    ctx.rrect([x, y, x + w, y + h], 14, fill=CARD_BODY + (int(150 * aa / 255),),
              outline=tuple(color[:3]) + (aa,), w=4)
    cx, cy = x + w / 2, y + h / 2 - 8
    t = 15
    ctx.poly([(cx - t * 0.55, cy - t), (cx - t * 0.55, cy + t), (cx + t, cy)],
             fill=tuple(color[:3]) + (aa,))
    bw = w - 28
    ctx.line([(x + 14, y + h - 22), (x + 14 + bw, y + h - 22)],
             fill=(64, 74, 104, int(aa * 0.8)), w=4)
    ctx.line([(x + 14, y + h - 22), (x + 14 + bw * clamp(fill_f), y + h - 22)],
             fill=tuple(color[:3]) + (aa,), w=4)
    # tiny heart in the corner
    hx, hy = x + w - 24, y + 24
    ctx.circle((hx - 5, hy - 4), 6, fill=tuple(color[:3]) + (aa,))
    ctx.circle((hx + 5, hy - 4), 6, fill=tuple(color[:3]) + (aa,))
    ctx.poly([(hx - 10, hy), (hx + 10, hy), (hx, hy + 13)],
             fill=tuple(color[:3]) + (aa,))


def hour_label(ctx, x, y, text, size, a=255, color=HOUR_AMBER):
    aa = int(clamp(a, 0, 255))
    ctx.glow((x, y), size * 1.15, color, alpha=int(52 * aa / 255))
    ntext(ctx, (x, y), text, size=size, color=color, a=aa, halo=3)


def scroll_hud(ctx, t, at=(52, 40), on=True):
    """Persistent readout: SCROLL TIME 4H00M -> 6H00M across the 40 s."""
    x, y = at
    mins = 240 + int(max(0.0, t) * 3)
    label = f"{mins // 60}H{mins % 60:02d}M"
    bw, bh = 236, 46
    col = NEON_AMBER if on else SWITCH_OFF
    if on:
        ctx.glow((x + bw / 2, y + bh / 2), bw * 0.8, col, alpha=34)
    ctx.rrect([x, y, x + bw, y + bh], 10, fill=(3, 5, 12, 226),
              outline=tuple(col) + (255,), w=4)
    # little phone glyph
    gx, gy = x + 26, y + bh / 2
    ctx.rrect([gx - 9, gy - 13, gx + 9, gy + 13], 3, outline=tuple(col) + (255,), w=3)
    ctx.line([(gx - 4, gy + 9), (gx + 4, gy + 9)], fill=tuple(col) + (255,), w=3)
    ntext(ctx, (x + 52, y + 16), "SCROLL TIME", size=15,
          color=CREAM if on else SWITCH_OFF, anchor="lm", halo=1.2)
    ntext(ctx, (x + 52, y + 34), label, size=22, color=col,
          anchor="lm", halo=1.4)
    # minutes crawling along the bottom edge
    frac = (t % 1.0) if on else 0.0
    ctx.line([(x + 168, y + bh - 9), (x + 168 + 54 * frac, y + bh - 9)],
             fill=tuple(col) + (230,), w=4)


def viewer_hand(ctx, x, y, s=1.0, color=NEON_CYAN, a=255, point=True):
    """Foreshortened hand pushed at the camera: palm + index finger (point)
    or four fingers up (open). Silhouette body with a neon outline."""
    aa = int(clamp(a, 0, 255))
    col = tuple(color[:3]) + (aa,)
    ink = (5, 7, 14, aa)
    r = 44 * s
    ctx.ellipse([x - r, y - r * 0.92, x + r, y + r * 0.92],
                fill=ink, outline=col, w=max(3, int(6 * s)))
    if point:
        ctx.line([(x + 12 * s, y - 4 * s), (x - 62 * s, y - 72 * s)],
                 fill=ink, w=int(21 * s))
        ctx.line([(x + 12 * s, y - 4 * s), (x - 62 * s, y - 72 * s)],
                 fill=col, w=max(3, int(4.5 * s)))
        ctx.circle((x - 62 * s, y - 72 * s), 10.5 * s, fill=ink,
                   outline=col, w=max(3, int(4.5 * s)))
        for i in range(3):
            fx = x - 20 * s + i * 17 * s
            ctx.rrect([fx - 8 * s, y - 2 * s, fx + 8 * s, y + 26 * s],
                      8 * s, fill=ink, outline=col, w=max(2, int(3.5 * s)))
    else:
        for i in range(4):
            fx = x - 25 * s + i * 17 * s
            ctx.line([(fx, y - 6 * s), (fx - 3 * s, y - 46 * s)],
                     fill=ink, w=int(14 * s))
            ctx.line([(fx, y - 6 * s), (fx - 3 * s, y - 46 * s)],
                     fill=col, w=max(2, int(4 * s)))
        ctx.line([(x + 30 * s, y + 6 * s), (x + 48 * s, y - 22 * s)],
                 fill=ink, w=int(14 * s))
        ctx.line([(x + 30 * s, y + 6 * s), (x + 48 * s, y - 22 * s)],
                 fill=col, w=max(2, int(4 * s)))


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

    def zoom(self, lt):
        p = clamp(lt / self.span())
        a, b = self.zoom_range
        return lerp(a, b, p)

    def hud(self, ctx, lt, on=True):
        """Scroll-time HUD pinned to the frame, undoing pan + zoom."""
        z = self.zoom(lt)
        dx, dy = self.shake(lt)
        left = 640.0 * (1.0 - 1.0 / z) + dx
        top = 360.0 * (1.0 - 1.0 / z) + dy
        scroll_hud(ctx, self.t0 + lt, on=on,
                   at=(52.0 / z + left, 40.0 / z + top))


# ------------------------------------- 1 · the hook: knocking on the glass

class GlassTapHook(Scene):
    id = "glass_tap_hook"
    zoom_range = (1.03, 1.08)

    def build(self):
        self.bg = make_bg((7, 11, 24), (3, 4, 10))
        ctx = Ctx(self.bg)
        # the room behind the glass
        ctx.poly([(0, 0), (W, 0), (W, H), (0, H)], fill=SCREEN_TOP + (255,))
        ctx.glow((640, 250), 560, NEON_CYAN, alpha=44)
        ctx.glow((1140, 640), 380, NEON_MAGENTA, alpha=30)
        for k in range(7):
            ctx.line([(0, 74 + k * 92), (W, 74 + k * 92)],
                     fill=(9, 13, 26, 255), w=7)
        # desk slab along the bottom
        ctx.poly([(0, 636), (W, 618), (W, H), (0, H)], fill=ROOM_DESK + (255,))
        ctx.line([(0, 636), (W, 618)], fill=(46, 40, 64, 255), w=5)
        # faint monitor glow spilling from the right
        ctx.glow((1180, 420), 300, NEON_CYAN, alpha=52)
        # diagonal glass sheen
        ctx.poly([(150, 0), (368, 0), (128, H), (0, H)],
                 fill=SCREEN_SHEEN + (15,))
        ctx.poly([(905, 0), (985, 0), (772, H), (694, H)],
                 fill=SCREEN_SHEEN + (10,))

    def draw(self, ctx, lt):
        t = lt
        b0 = self.beat(0, 0)          # "Quick question:"
        b1 = self.beat(0, 1)          # "how many hours ..."
        c0 = self.beat(1, 0)          # "Don't look away -"
        c1 = self.beat(1, 1)          # "I can see you through this screen"

        taps = (b0, b1, c0)
        jab = max(0.0, max((1.0 - abs(lt - te) / 0.42) for te in taps))
        jab = jab * jab

        # ---- her: close-up, knuckles on the glass, then pointing at you
        x, y, s = 540.0, 884.0, 6.7
        rot = 0.035 * math.sin(lt * 1.7) + 0.05 * jab
        if t >= c0:
            k = ease_out(clamp(ramp(t, c0, c0 + 0.45)))
            pose = blend_pose(POSE_TAP, POSE_POINT, k)
        else:
            pose = POSE_TAP
        lid = blink_closed(lt, seed=0.4, period=3.1)
        if t < b1:
            brow = "curious"
        elif t < c0:
            brow = "skeptical"
        elif t < c1:
            brow = "deadpan"
        else:
            brow = "curious"
        mouth, shape = talk(lt, self, closed=(t < 0.15), idle="flat")
        look = (0.10 + 0.06 * math.sin(lt * 1.1), 0.02)
        T = girl_silhouette(ctx, x, y, s, pose, rim=NEON_CYAN,
                            rim2=NEON_MAGENTA, w=11, rot=rot,
                            sway=0.55 * math.sin(lt * 2.1 + 0.6) + 0.5 * jab,
                            look=look, lid=lid, brow=brow, mouth=shape,
                            openness=mouth)
        hand = T((33, -93)) if t < c0 else T((47, -75))

        # ---- the knuckle ripples on the glass
        for te in taps:
            k = clamp((t - te) / 1.15)
            if 0 < k < 1:
                for i in range(3):
                    kk = clamp(k * 1.25 - i * 0.18)
                    if 0 < kk < 1:
                        rr = 30 + 240 * kk
                        ctx.arc([hand[0] - rr, hand[1] - rr,
                                 hand[0] + rr, hand[1] + rr],
                                300, 60 if i % 2 else 120,
                                fill=(*NEON_CYAN[:3], int(215 * (1 - kk)),), w=5)

        # ---- her hand pushed at the glass while she calls you out
        if t >= c0:
            a = int(255 * ease_out(clamp(ramp(t, c0, c0 + 0.35))))
            viewer_hand(ctx, hand[0], hand[1], s=1.15, color=NEON_CYAN,
                        a=a, point=True)

        # ---- glass surface on top of everything
        scanlines(ctx, a=15)
        screen_frame(ctx, a=255)

        # ---- one-word callout
        if b0 <= t < b1 + 1.2:
            a = int(225 * (1 - clamp(ramp(t, b1 + 0.4, b1 + 1.2))))
            ntext(ctx, (980, 170), "HEY.", size=54, color=NEON_CYAN, a=a)

        self.hud(ctx, lt)

    def shake(self, lt):
        b0, c0 = self.beat(0, 0), self.beat(1, 0)
        a = 9.0 * max(0.0, 1.0 - abs(lt - b0) / 0.5)
        b = 12.0 * max(0.0, 1.0 - abs(lt - c0) / 0.6)
        amp = a + b
        dx = amp * math.sin(lt * 58) + 1.3 * math.sin(lt * 2.1)
        dy = amp * 0.65 * math.cos(lt * 51) + 1.1 * math.cos(lt * 1.7)
        return safe_shake(self.zoom(lt), dx, dy)


# ------------------------------- 2 · the mirror: your thumb knows the beat

class ThumbLoopMirror(Scene):
    id = "thumb_loop_mirror"
    zoom_range = (1.06, 1.14)

    CARDS = [
        (96, 0, 214, 136, CARD_CYAN, 0),
        (946, 150, 220, 140, CARD_MAGENTA, 190),
        (330, 320, 200, 128, CARD_CYAN, 380),
        (690, 60, 206, 132, CARD_MAGENTA, 570),
        (540, 470, 196, 124, CARD_CYAN, 760),
    ]

    def build(self):
        self.bg = make_bg((6, 9, 20), (3, 4, 11))
        ctx = Ctx(self.bg)
        ctx.glow((640, 400), 620, NEON_CYAN, alpha=40)
        ctx.glow((140, 620), 340, NEON_MAGENTA, alpha=36)
        # wall + desk
        ctx.poly([(0, 0), (W, 0), (W, 596), (0, 596)], fill=ROOM_WALL + (255,))
        for k in range(5):
            ctx.line([(0, 96 + k * 104), (W, 96 + k * 104)],
                     fill=(13, 17, 33, 255), w=4)
        ctx.poly([(0, 596), (W, 596), (W, H), (0, H)], fill=ROOM_FLOOR + (255,))
        ctx.line([(0, 596), (W, 596)], fill=INK + (255,), w=5)
        # desk slab she sits behind
        ctx.poly([(0, 646), (W, 632), (W, H), (0, H)], fill=ROOM_DESK + (255,))
        ctx.line([(0, 646), (W, 632)], fill=(44, 38, 60, 255), w=5)

    def draw(self, ctx, lt):
        t = lt
        b0 = self.beat(2, 0)          # "Up, up, down."
        b1 = self.beat(2, 1)          # "Your thumb knows the rhythm"
        b2 = self.beat(2, 2)          # "better than you do."

        # ---- the feed: cards drift up, jump on every swipe beat
        sp = lt
        for be in (b0, b1, b2):
            if t > be:
                sp += 2.3 * ease_out(clamp((t - be) / 0.55))
        for i, (cx, cy0, cw, ch, col, off) in enumerate(self.CARDS):
            y = 812 - ((sp * 44 + off) % 980)
            fill_f = 0.25 + 0.6 * ((i * 0.37 + sp * 0.18) % 1.0)
            video_card(ctx, cx, y, cw, ch, col, a=232, fill_f=fill_f, seed=i)

        # ---- her: medium shot, thumb keeping the rhythm
        x, y, s = 636.0, 682.0, 3.45
        rate = 0.85
        if t > b0:
            rate += 0.75 * ease_out(clamp((t - b0) / 0.6))
        if t > b1:
            rate += 0.55 * ease_out(clamp((t - b1) / 0.6))
        tri = abs(((lt * rate) % 1.0) * 2.0 - 1.0)
        pose = blend_pose(POSE_SWIPE_DOWN, POSE_SWIPE_UP, tri)
        sway = 0.5 * math.sin(lt * 2.4 + 1.2) + 0.35 * (tri - 0.5)
        lid = blink_closed(lt, seed=1.7, period=2.9)
        brow = "deadpan" if t < b2 else "skeptical"
        mouth, shape = talk(lt, self, idle="flat")
        # eyes ride the feed upward
        look = (-0.35 - 0.2 * math.sin(lt * 1.4), -0.30 - 0.15 * math.sin(lt * 0.9))
        T = girl_silhouette(ctx, x, y, s, pose, rim=NEON_CYAN,
                            rim2=NEON_MAGENTA, w=8, sway=sway,
                            look=look, lid=lid, brow=brow, mouth=shape,
                            openness=mouth)
        hand = T((31, -76))

        # ---- swipe streaks off the thumb
        for be in (b0, b1, b2):
            k = clamp((t - be) / 0.7)
            if 0 < k < 1:
                for i in range(3):
                    rr = 26 + 120 * k + i * 26
                    ctx.arc([hand[0] - rr, hand[1] - rr * 1.15,
                             hand[0] + rr, hand[1] + rr * 1.15],
                            200 if i % 2 else 250, 340 if i % 2 else 40,
                            fill=(*NEON_MAGENTA[:3], int(190 * (1 - k)),), w=4)

        # ---- the rhythm labels
        if b0 <= t < b1 + 0.6:
            a = int(230 * (1 - clamp(ramp(t, b1, b1 + 0.6))))
            ntext(ctx, (1020, 300), "UP", size=44, color=NEON_CYAN, a=a)
            ntext(ctx, (1020, 366), "UP", size=36, color=NEON_CYAN,
                  a=int(a * 0.7))
            ntext(ctx, (1020, 424), "DOWN", size=44, color=NEON_MAGENTA, a=a)
        if t >= b2:
            ntext(ctx, (250, 240), "AUTOPLAY", size=24, color=NEON_MAGENTA,
                  a=int(165 + 70 * pulse(t, 2.4)))

        self.hud(ctx, lt)

    def shake(self, lt):
        b0 = self.beat(2, 0)
        p = clamp(lt / self.span())
        k = max(0.0, 1.0 - abs(lt - b0) / 0.6)
        dx = 16 * p + 5.5 * k * k * math.sin(lt * 56)
        dy = 2.6 * math.sin(lt * 5.0) + 3.4 * k * k * math.cos(lt * 48)
        return safe_shake(self.zoom(lt), dx, dy)


# ------------------------------------- 3 · the counter: 1H, 3H, 5H+

class ClockNumbersDrop(Scene):
    id = "clock_numbers_drop"
    zoom_range = (1.06, 1.16)

    COUNTERS = [
        ("1H", 782, 168, 76, 0),        # (text, x, y, size, beat offset s)
        ("3H", 880, 336, 92, 0.95),
        ("5H+", 992, 516, 110, None),   # None -> beat(3, 1)
    ]

    def build(self):
        self.bg = make_bg((8, 10, 22), (3, 4, 10))
        ctx = Ctx(self.bg)
        ctx.glow((1040, 250), 460, NEON_AMBER, alpha=44)
        ctx.glow((140, 560), 320, NEON_CYAN, alpha=34)
        # wall + floor
        ctx.poly([(0, 0), (W, 0), (W, 584), (0, 584)], fill=ROOM_WALL + (255,))
        for k in range(5):
            ctx.line([(0, 84 + k * 104), (W, 84 + k * 104)],
                     fill=(13, 17, 33, 255), w=4)
        ctx.poly([(0, 584), (W, 584), (W, H), (0, H)], fill=ROOM_FLOOR + (255,))
        ctx.line([(0, 584), (W, 584)], fill=INK + (255,), w=5)
        # unlit wall clock
        ctx.circle((1046, 148), 92, fill=(9, 11, 22, 255),
                   outline=CLOCK_RING + (255,), w=7)
        for i in range(12):
            ang = math.radians(i * 30 - 90)
            ctx.line([(1046 + 76 * math.cos(ang), 148 + 76 * math.sin(ang)),
                      (1046 + 88 * math.cos(ang), 148 + 88 * math.sin(ang))],
                     fill=CLOCK_RING + (255,), w=4)
        # desk edge
        ctx.poly([(0, 640), (W, 626), (W, H), (0, H)], fill=ROOM_DESK + (255,))
        ctx.line([(0, 640), (W, 626)], fill=(44, 38, 60, 255), w=5)

    def draw(self, ctx, lt):
        t = lt
        b0 = self.beat(3, 0)          # "One hour. Three hours."
        b1 = self.beat(3, 1)          # "Five plus,"
        b2 = self.beat(3, 2)          # "and the counter just keeps glowing"

        # ---- the wall clock hands race
        ang = math.radians(-90 + lt * 42)
        ctx.line([(1046, 148), (1046 + 52 * math.cos(ang),
                                148 + 52 * math.sin(ang))],
                 fill=HOUR_GLOW + (235,), w=6)
        ang2 = math.radians(-90 + lt * 340)
        ctx.line([(1046, 148), (1046 + 70 * math.cos(ang2),
                                148 + 70 * math.sin(ang2))],
                 fill=HOUR_AMBER + (215,), w=4)
        ctx.circle((1046, 148), 7, fill=HOUR_GLOW + (255,))

        # ---- the hour counters drop in and stack behind her
        landings = []
        for text, cx, cy, size, off in self.COUNTERS:
            te = b1 if off is None else b0 + off
            landings.append(te)
            if t < te - 0.02:
                continue
            k = ease_out(clamp((t - te) / 0.55))
            drop = (1.0 - k) * 460
            y = cy + drop
            a = int(255 * clamp(ramp(t, te, te + 0.18)))
            squash = 1.0 + 0.10 * math.sin(math.pi * clamp((t - te) / 0.45))
            hour_label(ctx, cx, y, text, size * squash, a=a)
            # landing ring
            rk = clamp((t - te) / 0.8)
            if 0 < rk < 1:
                rr = 40 + 200 * rk
                ctx.arc([cx - rr, y - rr * 0.55, cx + rr, y + rr * 0.55],
                        200, 340, fill=(*HOUR_AMBER[:3], int(200 * (1 - rk)),), w=5)

        # ---- the counters keep glowing after the last one lands
        if t >= b2:
            g = 0.5 + 0.5 * pulse(t, 1.6)
            ctx.glow((890, 340), 420, NEON_AMBER, alpha=int(26 + 30 * g))

        # ---- her: hands on hips, deadpan disbelief
        x, y, s = 452.0, 686.0, 3.85
        sway = 0.42 * math.sin(lt * 1.9 + 0.4)
        lid = blink_closed(lt, seed=2.6, period=3.4)
        brow = "deadpan" if t < b1 else "skeptical"
        mouth, shape = talk(lt, self, idle="flat")
        look = (0.45 + 0.12 * math.sin(lt * 1.2), -0.12)
        T = girl_silhouette(ctx, x, y, s, POSE_HIP, rim=NEON_AMBER,
                            rim2=NEON_CYAN, w=9, sway=sway,
                            look=look, lid=lid, brow=brow, mouth=shape,
                            openness=mouth)
        head = T((0, -88))

        # ---- ticks of disbelief above her head
        if t >= b0:
            for i in range(3):
                k = ((lt - b0) * 1.4 + i / 3.0) % 1.0
                ctx.line([(head[0] + 34 + i * 22, head[1] - 66 - 30 * k),
                          (head[0] + 44 + i * 22, head[1] - 96 - 30 * k)],
                         fill=(*HOUR_AMBER[:3], int(190 * (1 - k)),), w=4)

        self.hud(ctx, lt)

    def shake(self, lt):
        b0 = self.beat(3, 0)
        b1 = self.beat(3, 1)
        amp = 0.0
        for te, gain in ((b0, 9.0), (b0 + 0.95, 8.0), (b1, 12.0)):
            amp += gain * max(0.0, 1.0 - abs(lt - te) / 0.55)
        dx = amp * math.sin(lt * 60) + 1.2 * math.sin(lt * 2.0)
        dy = amp * 0.6 * math.cos(lt * 52) + 1.0 * math.cos(lt * 1.6)
        return safe_shake(self.zoom(lt), dx, dy)


# ------------------------------ 4 · the room sinks, the light stays on her

class RoomFadeShadow(Scene):
    id = "room_fade_shadow"
    zoom_range = (1.05, 1.18)

    def build(self):
        self.bg = make_bg((16, 20, 40), (7, 9, 20))
        ctx = Ctx(self.bg)
        ctx.glow((300, 250), 420, NEON_CYAN, alpha=40)
        ctx.glow((1160, 600), 340, NEON_MAGENTA, alpha=30)
        # wall
        ctx.poly([(0, 0), (W, 0), (W, 560), (0, 560)], fill=ROOM_WALL + (255,))
        for k in range(5):
            ctx.line([(0, 78 + k * 104), (W, 78 + k * 104)],
                     fill=(14, 18, 36, 255), w=4)
        # window with a cold moon sliver
        nrrect(ctx, [86, 96, 336, 400], 8, STEEL, w=5, fill=(10, 15, 30, 255))
        ctx.line([(211, 100), (211, 396)], fill=(24, 30, 52, 255), w=6)
        ctx.line([(90, 248), (332, 248)], fill=(24, 30, 52, 255), w=6)
        ctx.circle((276, 168), 34, fill=(206, 226, 244, 235))
        ctx.circle((262, 160), 30, fill=(10, 15, 30, 255))
        # floor
        ctx.poly([(0, 560), (W, 560), (W, H), (0, H)], fill=ROOM_FLOOR + (255,))
        ctx.line([(0, 560), (W, 560)], fill=INK + (255,), w=5)
        # desk + monitor + keyboard
        ctx.poly([(640, 520), (W, 508), (W, H), (640, H)],
                 fill=ROOM_DESK + (255,))
        ctx.poly([(664, 300), (1104, 292), (1104, 508), (664, 518)],
                 fill=(14, 16, 30, 255), outline=STEEL + (255,), w=6)
        ctx.poly([(684, 318), (1084, 311), (1084, 488), (684, 497)],
                 fill=(16, 60, 78, 255))
        for k in range(6):
            ctx.line([(706, 344 + k * 24), (706 + (k * 97) % 300, 344 + k * 24)],
                     fill=(86, 220, 244, 150), w=5)
        ctx.poly([(846, 508), (930, 508), (946, 536), (832, 536)],
                 fill=(20, 22, 40, 255))
        ctx.poly([(700, 546), (1040, 540), (1054, 574), (690, 580)],
                 fill=(22, 24, 44, 255), outline=(52, 58, 84, 255), w=4)
        # poster on the wall
        nrrect(ctx, [420, 120, 620, 320], 6, (52, 58, 84), w=5,
               fill=(20, 22, 42, 255))
        ntext(ctx, (520, 220), "03:00", size=44, color=(120, 140, 170),
              a=255, halo=1.5)
        # dust in the light
        for i in range(24):
            px = (i * 173) % W
            py = 70 + (i * 97) % 520
            ctx.circle((px, py), 1.6 + (i % 3) * 0.7, fill=DUST + (80,))

    def draw(self, ctx, lt):
        t = lt
        b0 = self.beat(4, 0)          # "The room goes dark,"
        b1 = self.beat(4, 1)          # "but that cyan light"
        b2 = self.beat(4, 2)          # "stays stuck on your face"

        # ---- the room drops to midnight shadow
        k = ease_in_out(clamp(ramp(t, b0, b0 + 2.4)))
        if k > 0.001:
            ctx.poly([(0, 0), (W, 0), (W, H), (0, H)],
                     fill=ROOM_MIDNIGHT + (int(214 * k),))

        # ---- the monitor is the only light left (drawn after the shadow)
        m = 0.55 + 0.45 * pulse(t, 1.3)
        ctx.glow((884, 400), 330 * (0.5 + 0.5 * k), NEON_CYAN,
                 alpha=int((40 + 60 * k) * m))
        ctx.poly([(684, 318), (1084, 311), (1084, 488), (684, 497)],
                 fill=(16, 60, 78, int(255 - 60 * k)))
        for kk in range(5):
            ctx.line([(706, 348 + kk * 26),
                      (706 + (kk * 113) % 290, 348 + kk * 26)],
                     fill=(86, 220, 244, int((170 - 70 * k) * m)), w=5)
        # window sliver dims to nothing
        if k > 0.2:
            ctx.poly([(90, 100), (332, 100), (332, 396), (90, 396)],
                     fill=ROOM_MIDNIGHT + (int(200 * k),))

        # ---- her: slow push-in, cyan rim left on face and hair
        x, y, s = 512.0, 796.0, 4.55
        sway = 0.5 * math.sin(lt * 1.6 + 0.9)
        lid = blink_closed(lt, seed=3.9, period=3.2)
        brow = "empathetic" if t < b2 else "soft"
        mouth, shape = talk(lt, self, idle="flat")
        # gaze drifts from the dark room back to the camera
        g = ease_out(clamp(ramp(t, b1, b2)))
        look = (lerp(-0.4, 0.05, g), lerp(-0.1, 0.0, g))
        T = girl_silhouette(ctx, x, y, s, POSE_CALM, rim=NEON_CYAN,
                            rim2=NEON_MAGENTA, w=10, sway=sway,
                            look=look, lid=lid, brow=brow, mouth=shape,
                            openness=mouth)
        head = T((0, -88))

        # ---- the cyan light stuck on her face
        if k > 0.05:
            ctx.glow((head[0] + 18, head[1] + 6), 92 * s / 4.55, NEON_CYAN,
                     alpha=int(58 * k * m))

        # ---- dust keeps drifting in the monitor light
        for i in range(14):
            kk = ((lt * 0.12) + i / 14.0) % 1.0
            px = 340 + (i * 89) % 800
            py = 620 - 420 * kk
            ctx.circle((px, py), 2.2, fill=DUST + (int(120 * (1 - abs(kk - 0.5) * 2) * (0.35 + 0.65 * k)),))

        # ---- the beat label
        if t >= b2:
            ntext(ctx, (980, 176), "STUCK ON YOU", size=27, color=NEON_CYAN,
                  a=int(150 + 70 * pulse(t, 2.0)))

        self.hud(ctx, lt)

    def shake(self, lt):
        p = clamp(lt / self.span())
        dx = 22 * p
        dy = 2.4 * math.sin(lt * 4.2) + 1.6 * math.sin(lt * 1.9)
        return safe_shake(self.zoom(lt), dx, dy)


# -------------------------------- 5 · the quiet beat: what do you remember

class PauseQuietBeat(Scene):
    id = "pause_quiet_beat"
    zoom_range = (1.10, 1.16)

    CARDS = [
        (84, 120, 224, 142, CARD_FROST, 0.55),
        (940, 96, 232, 148, CARD_FROST, 0.30),
        (300, 430, 206, 132, CARD_FROST, 0.42),
        (760, 452, 214, 138, CARD_FROST, 0.62),
        (540, 60, 198, 126, CARD_FROST, 0.24),
    ]

    def build(self):
        self.bg = make_bg((5, 7, 17), (3, 4, 10))
        ctx = Ctx(self.bg)
        ctx.glow((640, 360), 560, NEON_CYAN, alpha=30)
        ctx.glow((1180, 640), 320, NEON_MAGENTA, alpha=26)
        # the room is already dark: wall line, desk, nothing else
        ctx.poly([(0, 0), (W, 0), (W, 572), (0, 572)], fill=(9, 11, 24, 255))
        ctx.line([(0, 572), (W, 572)], fill=(20, 24, 44, 255), w=5)
        ctx.poly([(0, 648), (W, 636), (W, H), (0, H)], fill=ROOM_DESK + (255,))
        ctx.line([(0, 648), (W, 636)], fill=(38, 34, 54, 255), w=5)

    def draw(self, ctx, lt):
        t = lt
        b0 = self.beat(5, 0)          # "So tell me -"
        b1 = self.beat(5, 1)          # "what do you actually remember"
        b2 = self.beat(5, 2)          # "from the last hour?"

        # ---- the feed has frozen: cards hang dim and still
        for i, (cx, cy, cw, ch, col, ff) in enumerate(self.CARDS):
            video_card(ctx, cx, cy, cw, ch, col, a=150 - i * 12,
                       fill_f=ff, seed=i)
        # one slow scanline crawling over the frozen feed
        sy = 60 + ((lt * 26) % 620)
        ctx.line([(60, sy), (W - 60, sy)], fill=(120, 150, 180, 60), w=3)

        # ---- the freeze chime rings off the cards
        k = clamp((t - b0) / 1.6)
        if 0 < k < 1:
            for i in range(3):
                kk = clamp(k * 1.3 - i * 0.22)
                if 0 < kk < 1:
                    rr = 60 + 420 * kk
                    ctx.arc([640 - rr, 340 - rr * 0.7, 640 + rr, 340 + rr * 0.7],
                            300, 60, fill=(170, 210, 235, int(150 * (1 - kk))),
                            w=4)

        # ---- her: intimate framing, hand up, asking you directly
        x, y, s = 618.0, 830.0, 5.55
        if t < b1:
            pose = POSE_SOFT
        else:
            k2 = ease_out(clamp(ramp(t, b1, b1 + 0.5)))
            pose = blend_pose(POSE_SOFT, POSE_GESTURE_OPEN, k2)
        sway = 0.40 * math.sin(lt * 1.5 + 1.4)
        lid = blink_closed(lt, seed=5.2, period=3.6)
        brow = "empathetic" if t < b1 else "soft"
        mouth, shape = talk(lt, self, idle="smile")
        look = (0.02, -0.02)          # straight down the lens
        T = girl_silhouette(ctx, x, y, s, pose, rim=NEON_CYAN,
                            rim2=NEON_MAGENTA, w=11, sway=sway,
                            look=look, lid=lid, brow=brow, mouth=shape,
                            openness=mouth)
        hand = T((42, -72))

        # ---- an open palm offered at the glass
        if t >= b1:
            a = int(255 * ease_out(clamp(ramp(t, b1, b1 + 0.4))))
            viewer_hand(ctx, hand[0], hand[1], s=0.92, color=NEON_CYAN,
                        a=a, point=False)

        # ---- the question hanging in the dark
        if t >= b2:
            a = int(200 + 55 * pulse(t, 1.8))
            ntext(ctx, (905, 250), "?", size=96, color=NEON_CYAN, a=a)
        elif t >= b0:
            ntext(ctx, (905, 250), "...", size=64, color=NEON_CYAN,
                  a=int(170 + 60 * pulse(t, 1.4)))

        self.hud(ctx, lt)

    def shake(self, lt):
        dy = 1.7 * math.sin(lt * 1.5) + 1.1 * math.sin(lt * 0.8)
        dx = 1.2 * math.sin(lt * 1.1)
        return safe_shake(self.zoom(lt), dx, dy)


# --------------------------- 6 · the choice: swipe the timeline off

class ScreenOffChoice(Scene):
    id = "screen_off_choice"
    zoom_range = (1.06, 1.14)

    SWITCH = (846, 372, 1064, 470)   # track box

    def build(self):
        self.bg = make_bg((7, 9, 21), (3, 4, 10))
        ctx = Ctx(self.bg)
        ctx.glow((950, 420), 420, NEON_AMBER, alpha=54)
        ctx.glow((180, 300), 360, NEON_CYAN, alpha=36)
        # wall + floor
        ctx.poly([(0, 0), (W, 0), (W, 566), (0, 566)], fill=ROOM_WALL + (255,))
        for k in range(5):
            ctx.line([(0, 84 + k * 104), (W, 84 + k * 104)],
                     fill=(13, 17, 33, 255), w=4)
        ctx.poly([(0, 566), (W, 566), (W, H), (0, H)], fill=ROOM_FLOOR + (255,))
        ctx.line([(0, 566), (W, 566)], fill=INK + (255,), w=5)
        # the panel the switch lives on
        nrrect(ctx, [790, 300, 1130, 540], 14, (60, 54, 78), w=6,
               fill=PAPER + (255,))
        for k in range(3):
            ctx.line([(816, 344 + k * 74), (1104, 344 + k * 74)],
                     fill=(28, 26, 44, 255), w=4)
        # the switch bed (glows amber while it is on)
        x0, y0, x1, y1 = self.SWITCH
        ctx.rrect([x0, y0, x1, y1], 49, fill=SWITCH_TRACK + (255,),
                  outline=(74, 62, 48, 255), w=5)
        # desk edge
        ctx.poly([(0, 646), (W, 634), (W, H), (0, H)], fill=ROOM_DESK + (255,))
        ctx.line([(0, 646), (W, 634)], fill=(44, 38, 60, 255), w=5)
        # dust
        for i in range(18):
            px = (i * 151) % W
            py = 70 + (i * 89) % 480
            ctx.circle((px, py), 1.6 + (i % 3) * 0.6, fill=DUST + (70,))

    def draw(self, ctx, lt):
        t = lt
        a0 = self.beat(6, 0)          # "Nothing? Thought so."
        s0 = self.beat(7, 0)          # "The switch is right here,"
        s1 = self.beat(7, 1)          # "glowing amber,"
        s2 = self.beat(7, 2)          # "waiting for your hand."
        p0 = self.beat(8, 0)          # "Swipe it off."
        p1 = self.beat(8, 1)          # "I'll be here when you come back."

        on = t < p0 + 0.12
        x0, y0, x1, y1 = self.SWITCH
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2

        # ---- the amber switch
        if t >= s0 - 0.6:
            appear = ease_out(clamp(ramp(t, s0 - 0.6, s0 + 0.2)))
            g = (0.55 + 0.45 * pulse(t, 1.7)) if on else 0.0
            if on:
                ctx.glow((cx, cy), 210 * appear * (0.7 + 0.5 * g),
                         NEON_AMBER, alpha=int(70 * appear * (0.6 + 0.6 * g)))
            k = ease_out(clamp(ramp(t, p0 + 0.05, p0 + 0.75)))
            knob_x = lerp(x1 - 58, x0 + 58, k)
            track_col = SWITCH_AMBER if on else SWITCH_OFF
            ctx.rrect([x0, y0, x1, y1], 49,
                      fill=tuple(SWITCH_TRACK) + (255,),
                      outline=tuple(track_col) + (int(255 * appear),),
                      w=int(6 * appear) or 1)
            if on:
                ctx.rrect([x0 + 6, y0 + 6, x1 - 6, y1 - 6], 43,
                          fill=tuple(dim(SWITCH_AMBER, 0.16 * g * appear)) + (255,))
            ctx.circle((knob_x, cy), 40, fill=(10, 10, 16, 255),
                       outline=tuple(track_col) + (int(255 * appear),), w=6)
            if on:
                ctx.circle((knob_x, cy), 15, fill=tuple(SWITCH_AMBER) + (255,))
            ntext(ctx, (cx, y0 - 34), "SCREEN" if on else "OFF", size=26,
                  color=NEON_AMBER if on else SWITCH_OFF,
                  a=int(appear * (255 if on else 200) *
                        (1 if not on or pulse(t, 3.0) > 0.15 else 0.85)))

        # ---- her: shrug, then reach, then swipe
        x, y, s = 500.0, 694.0, 3.62
        if t < s2:
            k = ease_out(clamp(ramp(t, a0, a0 + 0.5))) if t >= a0 else 0.0
            pose = blend_pose(POSE_HIP, POSE_SOFT, k) if t >= a0 else POSE_CALM
        elif t < p0:
            k = ease_out(clamp(ramp(t, s2, s2 + 0.6)))
            pose = blend_pose(POSE_SOFT, POSE_GESTURE_OPEN, k)
        else:
            k = ease_in_out(clamp(ramp(t, p0, p0 + 0.55)))
            pose = blend_pose(POSE_GESTURE_OPEN, POSE_REACH, k)
        # drift toward the switch as she commits
        x += 150 * ease_in_out(clamp(ramp(t, s2, p0 + 0.4)))
        sway = 0.45 * math.sin(lt * 1.8 + 0.7)
        lid = blink_closed(lt, seed=6.4, period=3.3)
        if t < a0:
            brow, idle = "deadpan", "flat"
        elif t < s0:
            brow, idle = "skeptical", "smile"
        elif t < p1:
            brow, idle = "curious", "flat"
        else:
            brow, idle = "soft", "smile"
        mouth, shape = talk(lt, self, idle=idle)
        # eyes: camera -> switch -> camera
        if t < s0:
            look = (0.05, 0.0)
        elif t < p0:
            look = (0.55, 0.05)
        else:
            g = ease_out(clamp(ramp(t, p0 + 0.6, p1)))
            look = (lerp(0.55, 0.03, g), 0.0)
        rot = 0.02 * math.sin(lt * 12) * (1.0 if p0 <= t < p0 + 0.6 else 0.25)
        T = girl_silhouette(ctx, x, y, s, pose,
                            rim=NEON_CYAN if on else NEON_AMBER,
                            rim2=NEON_AMBER if on else NEON_CYAN,
                            w=9, sway=sway, rot=rot,
                            look=look, lid=lid, brow=brow, mouth=shape,
                            openness=mouth)

        # ---- the swipe: her hand crosses the switch
        if p0 - 0.2 <= t < p0 + 0.9:
            k = clamp((t - (p0 - 0.2)) / 1.1)
            hx = lerp(x0 - 60, x1 + 90, ease_in_out(k))
            ctx.line([(hx - 120, cy + 70), (hx, cy + 10)],
                     fill=(*NEON_AMBER[:3], int(210 * (1 - k)),), w=8)
            ctx.glow((hx, cy), 90, NEON_AMBER, alpha=int(120 * (1 - k)))

        # ---- power off: the picture collapses into one bright line
        if t >= p0:
            k = ease_out(clamp((t - p0 - 0.05) / 0.85))
            if k < 1.0:
                hh = (1.0 - k) * 380 + 3
                ctx.poly([(0, 360 - hh), (W, 360 - hh), (W, 360 + hh),
                          (0, 360 + hh)],
                         fill=(*NEON_CYAN[:3], int(120 * (1 - k)),))
                ctx.line([(0, 360), (W, 360)],
                         fill=(*WHITE[:3], int(235 * (1 - k * k)),),
                         w=max(2, int(3 + 12 * (1 - k))))
            # the room settles into a clean amber-and-cyan closing frame
            dk = ease_in_out(clamp((t - p0 - 0.5) / 1.4))
            if dk > 0.001:
                ctx.poly([(0, 0), (W, 0), (W, H), (0, H)],
                         fill=ROOM_MIDNIGHT + (int(150 * dk),))
                ctx.glow((640, 664), 300, HORIZON_AMBER,
                         alpha=int(46 * dk * (0.7 + 0.3 * pulse(t, 1.2))))
                ctx.line([(40, 664), (W - 40, 664)],
                         fill=(*HORIZON_AMBER[:3], int(230 * dk)), w=5)
                ctx.line([(40, 674), (W - 40, 674)],
                         fill=(*NEON_CYAN[:3], int(120 * dk)), w=3)
                ctx.glow((640, 360), 520, NEON_CYAN, alpha=int(26 * dk))

        # ---- closing words
        if t >= p1:
            ntext(ctx, (640, 176), "COME BACK LATER", size=34,
                  color=NEON_CYAN, a=int(175 + 60 * pulse(t, 1.5)))

        self.hud(ctx, lt, on=on)

    def shake(self, lt):
        p0 = self.beat(8, 0)
        a0 = self.beat(6, 0)
        amp = 6.0 * max(0.0, 1.0 - abs(lt - a0) / 0.5)
        amp += 16.0 * max(0.0, 1.0 - abs(lt - (p0 + 0.1)) / 0.7)
        dx = amp * math.sin(lt * 62) + 1.4 * math.sin(lt * 2.2)
        dy = amp * 0.6 * math.cos(lt * 54) + 1.2 * math.cos(lt * 1.8)
        return safe_shake(self.zoom(lt), dx, dy)


# ------------------------------------------------------------------ registry

SCENES = {cls.id: cls for cls in
          (GlassTapHook, ThumbLoopMirror, ClockNumbersDrop, RoomFadeShadow,
           PauseQuietBeat, ScreenOffChoice)}
