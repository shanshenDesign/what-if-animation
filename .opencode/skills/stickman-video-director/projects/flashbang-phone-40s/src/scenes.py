"""The five scenes of the "flashbang-phone-40s" episode.

Topic: What if unlocking your phone at night triggered a flashbang warning?
Style: Sci-fi Toon (heavy ink outlines, flat color, glowing tech HUD, stark night bedroom).
"""
import math

from PIL import Image

from stick import Ctx
from common import (AMBER, BG_BOT, BG_TOP, BLUE, CHALK, CREAM, CYAN, DIM,
                    FLASH_CORE, FLASH_EDGE, FLASH_RAY, GLASS, GOLD, GRID, GREEN,
                    HUD_GLITCH_CYAN, HUD_GLITCH_RED, INK, MAGENTA, NEON_RED,
                    NIGHT_BLACK, PAPER, SHEET_DEEP, SHEET_LIT, SKETCH, SS,
                    STEEL, STEEL_DIM, W, W2, H, H2, WALL_DEEP, WALL_LIT, WARM, clamp, dim,
                    ease_in, ease_in_out, ease_out, ease_out_back, font,
                    frozen_clock, lerp, mix, pulse, ramp, rgba, smoothstep)

# ------------------------------------------------------------------ fig poses

POSE_BED_SLEEP = {
    "head": (2, -88, 12),
    "spine": [(0, -76), (0, -44)],
    "armL": [(0, -72), (-24, -58), (-35, -52)],
    "armR": [(0, -72), (20, -55), (10, -38)],
    "legL": [(0, -44), (-14, -22), (-22, 0)],
    "legR": [(0, -44), (14, -22), (20, 0)],
}

POSE_BED_TAP = {
    "head": (0, -90, 12),
    "spine": [(0, -76), (0, -44)],
    "armL": [(0, -72), (-18, -62), (-25, -50)],
    "armR": [(0, -72), (22, -82), (34, -74)],
    "legL": [(0, -44), (-15, -22), (-18, 0)],
    "legR": [(0, -44), (14, -22), (18, 0)],
}

POSE_PANIC = {
    "head": (2, -94, 14),
    "spine": [(1, -76), (-1, -44)],
    "armL": [(0, -72), (-28, -90), (-36, -102)],
    "armR": [(0, -72), (28, -90), (36, -102)],
    "legL": [(0, -44), (-18, -22), (-22, 0)],
    "legR": [(0, -44), (18, -22), (22, 0)],
}

POSE_BLIND = {
    "head": (0, -82, 10),
    "spine": [(0, -66), (0, -34)],
    "armL": [(0, -60), (-30, -50), (-40, -40)],
    "armR": [(0, -60), (28, -84), (35, -96)],
    "legL": [(0, -34), (-20, -18), (-28, 0)],
    "legR": [(0, -34), (18, -18), (24, 0)],
}

# ------------------------------------------------------------------ helpers

def gradient(w, h, top, bottom):
    img = Image.new("RGB", (w, h))
    pixels = img.load()
    tr, tg, tb = top
    br, bg, bb = bottom
    for y in range(h):
        p = y / max(1, h - 1)
        r = int(tr + (br - tr) * p)
        g = int(tg + (bg - tg) * p)
        b = int(tb + (bb - tb) * p)
        for x in range(w):
            pixels[x, y] = (r, g, b)
    return img


def overlay(base, fn, angle=0.0, scale=1.0):
    return base


def scaled_box(box, s, cx=None, cy=None):
    x0, y0, x1, y1 = box
    if cx is None:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, h = (x1 - x0) * s, (y1 - y0) * s
    return [cx - w/2, cy - h/2, cx + w/2, cy + h/2]


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
                x = p0[0] + (p1[0] - p0[0]) * t
                y = p0[1] + (p1[1] - p0[1]) * t
                pts.append((x, y))
            res[k] = pts
    return res


def polar(cx, cy, r, deg):
    rad = math.radians(deg)
    return (cx + r * math.cos(rad), cy + r * math.sin(rad))


def sketchy(pts, jit=3.0, seed=0.0):
    out = []
    for i, (x, y) in enumerate(pts):
        dx = jit * math.sin(seed + i * 2.3 + x * 0.1)
        dy = jit * math.cos(seed + i * 1.7 + y * 0.1)
        out.append((x + dx, y + dy))
    return out


def nline(ctx, pts, color, w=6, a=255, halo=3.2, jit=3.0, seed=0.0):
    sp = sketchy(pts, jit=jit, seed=seed)
    if halo > 0:
        ctx.line(sp, fill=(0, 0, 0, int(a * 0.85)), w=w + int(halo * 2))
    ctx.line(sp, fill=tuple(color[:3]) + (a,), w=w)


def ncircle(ctx, c, r, color, w=6, a=255, fill=None, halo=3.2):
    if fill is not None:
        ctx.circle(c, r, fill=tuple(fill[:3]) + (int(fill[3] * (a / 255.0)) if len(fill) > 3 else a,))
    if halo > 0:
        ctx.circle(c, r, outline=(0, 0, 0, int(a * 0.85)), w=w + int(halo * 2))
    ctx.circle(c, r, outline=tuple(color[:3]) + (a,), w=w)


def nrrect(ctx, box, r, color, w=6, a=255, fill=None, halo=3.2):
    if fill is not None:
        ctx.rrect(box, r, fill=tuple(fill[:3]) + (int(fill[3] * (a / 255.0)) if len(fill) > 3 else a,))
    if halo > 0:
        ctx.rrect(box, r, outline=(0, 0, 0, int(a * 0.85)), w=w + int(halo * 2))
    ctx.rrect(box, r, outline=tuple(color[:3]) + (a,), w=w)


def ntext(ctx, xy, s, size=30, color=CREAM, a=255, anchor="mm", bold=True,
          halo=2.0):
    f = font(size, bold=bold)
    x, y = xy
    if halo > 0:
        for dx, dy in ((-halo, 0), (halo, 0), (0, -halo), (0, halo),
                       (-halo, -halo), (halo, halo), (-halo, halo), (halo, -halo)):
            ctx.text((x + dx, y + dy), s, size=size, bold=bold, fill=(0, 0, 0, int(a * 0.9)), anchor=anchor)
    ctx.text(xy, s, size=size, bold=bold, fill=tuple(color[:3]) + (a,), anchor=anchor)


def motion_lines(ctx, cx, cy, ang, n=5, r0=30, r1=110, color=NEON_RED, a=255, w=5):
    for i in range(n):
        da = (i - n / 2.0) * 12.0
        rad = math.radians(ang + da)
        x0 = cx + r0 * math.cos(rad)
        y0 = cy + r0 * math.sin(rad)
        x1 = cx + r1 * math.cos(rad)
        y1 = cy + r1 * math.sin(rad)
        nline(ctx, [(x0, y0), (x1, y1)], color, w=w, a=a, halo=2.0, jit=0)


def sweat(ctx, xy, r, color=CYAN, a=255):
    cx, cy = xy
    ctx.circle((cx, cy), r, fill=(2, 3, 8, a), outline=tuple(color[:3]) + (a,), w=3)
    ctx.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=tuple(color[:3]) + (a,), w=3)


def person(ctx, x, y, s, pose, color=CREAM, w=6, rot=0.0, outline=True,
           look=(0.0, 0.0), brow=None, mouth="flat"):
    # stick figure rendering with head, spine, limbs
    hx, hy, hr = pose["head"]
    head_center = (x + hx * s, y + hy * s)
    
    # body outline / shadow pass
    if outline:
        ncircle(ctx, head_center, hr * s, color, w=w, fill=NIGHT_BLACK, halo=3.5)
    else:
        ncircle(ctx, head_center, hr * s, color, w=w, fill=NIGHT_BLACK, halo=0)

    # spine
    spine_pts = [(x + px * s, y + py * s) for px, py in pose["spine"]]
    nline(ctx, [head_center] + spine_pts, color, w=w, halo=3.5 if outline else 0, jit=1.2)

    # limbs
    for limb_key in ("armL", "armR", "legL", "legR"):
        if limb_key in pose:
            pts = [(x + px * s, y + py * s) for px, py in pose[limb_key]]
            nline(ctx, pts, color, w=w, halo=3.5 if outline else 0, jit=1.2)

    # face details (eyes, mouth)
    fx, fy = head_center
    ex = fx + look[0] * 6 * s
    ey = fy + look[1] * 6 * s
    # vertical slit eyes for sci-fi toon style
    ctx.line([(ex - 3 * s, ey - 5 * s), (ex - 3 * s, ey + 2 * s)], fill=tuple(color[:3]) + (255,), w=max(2, int(w*0.7)))
    ctx.line([(ex + 3 * s, ey - 5 * s), (ex + 3 * s, ey + 2 * s)], fill=tuple(color[:3]) + (255,), w=max(2, int(w*0.7)))

    if mouth == "flat":
        ctx.line([(fx - 4 * s, fy + 6 * s), (fx + 4 * s, fy + 6 * s)], fill=tuple(color[:3]) + (255,), w=max(2, int(w*0.6)))
    elif mouth == "o":
        ctx.circle((fx, fy + 6 * s), 3 * s, outline=tuple(color[:3]) + (255,), w=2)
    elif mouth == "grimace":
        ctx.line([(fx - 6 * s, fy + 7 * s), (fx - 3 * s, fy + 4 * s), (fx + 3 * s, fy + 4 * s), (fx + 6 * s, fy + 7 * s)], fill=tuple(color[:3]) + (255,), w=2)


# --------------------------------------------------------- bedroom & phone props

def bedroom_room(ctx, lit_level=0.0):
    """Draws the 01:30 AM sci-fi bedroom with bed, nightstand, window, posters."""
    bg_col = mix(WALL_DEEP, WALL_LIT, lit_level)
    sheet_col = mix(SHEET_DEEP, SHEET_LIT, lit_level)
    
    # walls and floor
    ctx.poly([(0, 0), (W, 0), (W, 490), (0, 490)], fill=bg_col + (255,))
    ctx.poly([(0, 490), (W, 490), (W, H), (0, H)], fill=(12, 18, 32, 255))
    ctx.line([(0, 490), (W, 490)], fill=INK + (255,), w=6)

    # sci-fi window showing night city
    win_box = [820, 70, 1180, 390]
    ctx.rrect(win_box, 12, fill=(4, 8, 18, 255), outline=INK + (255,), w=6)
    # city skyline inside window
    for i in range(5):
        bx = 850 + i * 62
        bw = 46
        bh = 120 + (i * 33) % 110
        ctx.rrect([bx, 390 - bh, bx + bw, 390], 2, fill=(10, 18, 34, 255))
        ctx.circle((bx + 23, 390 - bh + 20), 4, fill=(255, 230, 100, int(150 * (1 - lit_level))))

    # bed frame and pillows
    bed_box = [80, 360, 640, 640]
    ctx.rrect(bed_box, 16, fill=(20, 28, 48, 255), outline=INK + (255,), w=6)
    # mattress blanket
    ctx.rrect([110, 390, 610, 620], 12, fill=sheet_col + (255,), outline=INK + (255,), w=5)
    # pillow
    ctx.rrect([130, 370, 310, 430], 8, fill=mix((35, 48, 76), (210, 230, 245), lit_level) + (255,), outline=INK + (255,), w=4)

    # nightstand with lamp & alarm clock
    ns_box = [680, 420, 780, 570]
    ctx.rrect(ns_box, 6, fill=(24, 34, 56, 255), outline=INK + (255,), w=5)
    # alarm clock displaying 01:30
    ctx.rrect([700, 440, 760, 480], 4, fill=(4, 8, 16, 255), outline=HUD_GLITCH_RED + (255,), w=2)
    ntext(ctx, (730, 460), "01:30", size=18, color=HUD_GLITCH_RED, a=255)


def phone_prop(ctx, box, brightness=1.0, active=False, blast=False):
    x0, y0, x1, y1 = box
    phone_col = (10, 14, 24) if not blast else FLASH_CORE
    outline_col = CYAN if not blast else FLASH_RAY
    
    # phone body
    ctx.rrect(box, 8, fill=phone_col, outline=outline_col + (255,), w=5)
    
    if active:
        # screen content
        screen_box = [x0 + 6, y0 + 6, x1 - 6, y1 - 6]
        screen_fill = (20, 230, 255, int(255 * brightness)) if not blast else (255, 255, 255, 255)
        ctx.rrect(screen_box, 4, fill=screen_fill)


# ------------------------------------------------------------------ scene classes

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
        return lerp(a, b, p)


class HookDarkScene(Scene):
    id = "hook_dark"
    zoom_range = (1.0, 1.04)

    def build(self):
        img = Image.new("RGB", (W2, H2))
        img.paste(gradient(W, H, (2, 3, 8), (4, 6, 14)), (0, 0))
        self.bg = img
        bedroom_room(Ctx(self.bg), lit_level=0.0)

    def draw(self, ctx, lt):
        t = lt
        b0 = self.beat(0, 0)
        b1 = self.beat(0, 1)
        b2 = self.beat(0, 2)

        # stickman in bed, sleeping peacefully then tapping phone
        tap_prog = ramp(t, b1, b1 + 0.5)
        pose = blend_pose(POSE_BED_SLEEP, POSE_BED_TAP, ease_out(tap_prog))
        person(ctx, 320, 520, 2.3, pose, color=CYAN, w=6, look=(0.2, 0.1), mouth="flat")

        # phone glowing and targeting face in scene 1 chunk 2/3
        if t >= b1:
            phone_box = [370, 460, 430, 510]
            phone_prop(ctx, phone_box, brightness=0.8, active=True)
            
            # holographic target reticle locking onto face
            reticle_a = clamp(ramp(t, b1 + 0.2, b1 + 0.6))
            if reticle_a > 0:
                rx, ry = 330, 440
                ncircle(ctx, (rx, ry), 35, CYAN, w=2, a=int(220 * reticle_a), halo=1.5)
                # corner brackets
                for sx, sy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                    ctx.line([(rx + sx * 25, ry + sy * 45), (rx + sx * 45, ry + sy * 45), (rx + sx * 45, ry + sy * 25)], fill=CYAN + (int(255 * reticle_a),), w=3)
                ntext(ctx, (rx, ry - 55), "TARGET ACQUIRED", size=12, color=CYAN, a=int(255 * reticle_a))

        # Scene 2 countdown overlay if line 1 starts
        if t >= self.line_start(1) - self.t0:
            c_prog = ramp(t, self.line_start(1) - self.t0, self.line_start(1) - self.t0 + 2.0)
            ntext(ctx, (640, 180), "TACTICAL FLASHBANG IN 3... 2... 1...", size=28, color=HUD_GLITCH_RED, a=int(255 * clamp(c_prog)))


class CountdownPanicScene(Scene):
    id = "countdown_panic"
    zoom_range = (1.02, 1.08)

    def build(self):
        img = Image.new("RGB", (W2, H2))
        img.paste(gradient(W, H, (10, 14, 26), (4, 6, 12)), (0, 0))
        self.bg = img
        bedroom_room(Ctx(self.bg), lit_level=0.15)

    def draw(self, ctx, lt):
        t = lt
        panic_prog = ramp(t, 0.0, 1.5)
        pose = blend_pose(POSE_BED_TAP, POSE_PANIC, ease_out(panic_prog))
        
        # panicking stickman trying to bash buttons
        shake_x = 4.0 * math.sin(t * 35) * (1.0 - panic_prog)
        person(ctx, 340 + shake_x, 510, 2.3, pose, color=CYAN, w=6, look=(0.0, -0.2), mouth="o")
        sweat(ctx, (300, 420), 18, color=CYAN)

        # phone with plasma charging core
        phone_box = [420, 420, 500, 480]
        phone_prop(ctx, phone_box, brightness=1.0, active=True)
        # charging core rings inside phone
        for k in range(3):
            rr = 10 + (t * 40 + k * 12) % 25
            ncircle(ctx, (460, 450), rr, HUD_GLITCH_RED, w=2, a=int(180 * (1 - rr/35)), halo=1.0)

        # sci-fi HUD warning panel
        hud_box = [720, 160, 1180, 360]
        nrrect(ctx, hud_box, 12, HUD_GLITCH_RED, w=3, fill=(10, 4, 8, 230))
        ntext(ctx, (750, 195), "BRIGHTNESS: 100%", size=20, color=HUD_GLITCH_RED, anchor="lm")
        ntext(ctx, (750, 235), "AUTO-DIM: OFFLINE", size=20, color=HUD_GLITCH_RED, anchor="lm")
        ntext(ctx, (750, 275), "OVERRIDE FAILED", size=20, color=HUD_GLITCH_RED, anchor="lm")
        
        # warning flashing banner
        if int(t * 6) % 2 == 0:
            ntext(ctx, (640, 100), "WARNING: RETINAL ANNIHILATION IMMINENT", size=24, color=HUD_GLITCH_RED, a=255)


class DetonationScene(Scene):
    id = "detonation"
    zoom_range = (1.04, 1.15)

    def build(self):
        img = Image.new("RGB", (W2, H2))
        img.paste(gradient(W, H, (200, 240, 255), (100, 220, 255)), (0, 0))
        self.bg = img
        bedroom_room(Ctx(self.bg), lit_level=1.0)

    def draw(self, ctx, lt):
        t = lt
        flash_intensity = 1.0 - 0.2 * math.sin(t * 20)
        
        # stadium bright illumination flash wash
        ctx.rrect([0, 0, W, H], 0, fill=FLASH_CORE + (int(240 * flash_intensity),))
        
        # radial light rays from phone
        for i in range(12):
            ang = i * 30 + t * 15
            p1 = polar(460, 450, 40, ang)
            p2 = polar(460, 450, 900, ang)
            nline(ctx, [p1, p2], FLASH_RAY, w=8, a=180, jit=0, halo=4.0)

        # blown away stickman silhouette/outline in blinding light
        person(ctx, 420, 510, 2.4, POSE_PANIC, color=(10, 20, 40), w=7, look=(0, 0), mouth="o")

        # floating dust particles in laser light
        for k in range(20):
            dx = (k * 137 + int(t * 80)) % W
            dy = (k * 93 + int(t * 50)) % H
            ctx.circle((dx, dy), 3 + (k % 4), fill=(255, 255, 255, 200))

        ntext(ctx, (640, 90), "100% LUMEN DETONATION", size=42, color=(10, 20, 40), halo=1.5)

    def shake(self, lt):
        # heavy orbital laser shockwave shaking
        a = 14.0 * max(0.0, 1.0 - lt * 0.3)
        return (a * math.sin(lt * 50), a * math.cos(lt * 44))


class AftermathScene(Scene):
    id = "aftermath"
    zoom_range = (1.05, 1.01)

    def build(self):
        img = Image.new("RGB", (W2, H2))
        img.paste(gradient(W, H, (4, 6, 14), (2, 3, 8)), (0, 0))
        self.bg = img
        bedroom_room(Ctx(self.bg), lit_level=0.05)

    def draw(self, ctx, lt):
        t = lt
        # stickman lying flat on the floor after the blast
        person(ctx, 360, 560, 2.4, POSE_BLIND, color=CYAN, w=6, look=(0, 0.3), mouth="grimace", rot=0.0)

        # cartoon smoke rising off head
        for k in range(3):
            sy = 520 - k * 30 - int((t * 40 + k * 15) % 80)
            sx = 350 + k * 12 + int(10 * math.sin(t * 5 + k))
            sr = 12 + k * 6
            ctx.circle((sx, sy), sr, outline=(140, 160, 180, int(180 * (1 - (sy - 300)/250))), w=3, fill=(10, 14, 24, 150))

        # red glitching HUD reading retina damage
        hud_box = [680, 180, 1180, 380]
        nrrect(ctx, hud_box, 12, HUD_GLITCH_RED, w=3, fill=(16, 4, 8, 240))
        ntext(ctx, (710, 220), "RETINA DAMAGE: 99%", size=22, color=HUD_GLITCH_RED, anchor="lm")
        ntext(ctx, (710, 270), "RECOVERY: 6 HOURS", size=22, color=HUD_GLITCH_CYAN, anchor="lm")
        ntext(ctx, (710, 320), "STATUS: LEGALLY BLIND", size=20, color=AMBER, anchor="lm")


class PunchlineScene(Scene):
    id = "punchline"
    zoom_range = (1.0, 1.05)

    def build(self):
        img = Image.new("RGB", (W2, H2))
        img.paste(gradient(W, H, (4, 6, 14), (8, 12, 24)), (0, 0))
        self.bg = img
        bedroom_room(Ctx(self.bg), lit_level=0.1)

    def draw(self, ctx, lt):
        t = lt
        # blindly reaching arm up from floor to tap screen again
        reach_prog = ease_out(ramp(t, 0.5, 2.0))
        pose = blend_pose(POSE_BLIND, POSE_BED_TAP, reach_prog)
        person(ctx, 360, 550 - int(30 * reach_prog), 2.4, pose, color=CYAN, w=6, look=(0.3, -0.1), mouth="o")

        # glowing phone tapped one more time
        if t >= 0.8:
            phone_box = [420, 380, 480, 430]
            phone_prop(ctx, phone_box, brightness=1.0, active=True)
            ntext(ctx, (450, 350), "CHECKING NOTIFICATIONS...", size=14, color=CYAN)

        # second round charging banner dropping down
        banner_prog = ease_out_back(ramp(t, 2.0, 3.2))
        if banner_prog > 0:
            bx0, by0, bx1, by1 = 280, 100, 1000, 200
            nrrect(ctx, [bx0, by0, bx1, by1], 16, HUD_GLITCH_RED, w=4, fill=(20, 6, 10, 240))
            ntext(ctx, ((bx0 + bx1)/2, (by0 + by1)/2 - 18), "ROUND 2 — CHARGING", size=32, color=HUD_GLITCH_RED)
            ntext(ctx, ((bx0 + bx1)/2, (by0 + by1)/2 + 20), "PREPARE FOR ANNIHILATION", size=16, color=CREAM)


# ------------------------------------------------------------------ registry

SCENES = {cls.id: cls for cls in
          (HookDarkScene, CountdownPanicScene, DetonationScene, AftermathScene, PunchlineScene)}
