"""Shared constants, easing, JSON I/O and font lookup for the 40 s episode.

Design 07 — "Hours spent scrolling": a female stickman behind the glass of
your screen breaks the fourth wall, taps the glass, counts the hours you
have burned scrolling, and finally reaches for the switch that turns the
screen off. Every scene is drawn in near-black with sharp silhouettes
edged by double-offset rim light — CYAN from the screen frame, MAGENTA
from the drifting short-video cards and AMBER from the hour counters and
the timeline switch. A soft halo pass sits behind every neon stroke, so
the three accents read as real light sources.

Palette roles in this episode:
    CYAN      the screen frame, her leading rim, the UI you cannot leave
    MAGENTA   the glow of the endless short-video cards
    AMBER     the 1H / 3H / 5H+ counters, the horizon, the power switch
    NEON_RED  reserved for alerts (unused beats keep the alias)

All scene code draws in 1x design space (1280x720); the Canvas in stick.py
multiplies by SS (supersample factor) so the final downscale gives clean
anti-aliased lines.
"""
import glob
import json
import math
import os
from pathlib import Path

from PIL import ImageFont

SS = 2  # supersample: render at 2x, downscale to 1280x720
W, H = 1280, 720          # 1x design space
W2, H2 = W * SS, H * SS   # render space

# ---------------------------------------------------------------- palette
BG_TOP = (4, 6, 14)           # canvas, top
BG_BOT = (12, 16, 32)         # canvas, bottom
NIGHT_TOP = BG_TOP            # back-compat alias
NIGHT_BOT = BG_BOT

CREAM = (234, 250, 255)       # primary figure stroke: ice-white neon
CYAN = (0, 235, 255)          # screen light / active state
MAGENTA = (255, 40, 196)      # card glow spill
NEON_RED = (255, 46, 64)      # alerts
RED = NEON_RED                # back-compat alias
GREEN = (126, 255, 158)       # calm / breathe
LIME = GREEN
BLUE = (92, 150, 255)         # phone glow
PINK = MAGENTA                # back-compat alias
PINK_DEEP = (196, 0, 148)
WARM = (255, 196, 64)         # lamp / horizon glow
GOLD = (255, 226, 130)
INK = (4, 5, 10)              # outlines and text on bright fills
WHITE = (255, 255, 255)
DIM = (86, 110, 140)          # secondary text
GRID = (18, 26, 44)           # unlit construction grid
PAPER = (16, 20, 34)          # dark card / panel fill

# environment layers (deliberately duller than the figures)
STEEL = (104, 140, 176)       # handles, mullions, furniture edges
STEEL_DIM = (54, 76, 104)     # trim, seams, far detail
GLASS = (24, 38, 60)          # window / screen interiors
CHALK = (168, 196, 214)       # secondary labels on props
AMBER = (255, 176, 84)        # lamps, counters, the switch

# sketch FX
SKETCH = 1.6                  # default hand-drawn jitter, 1x px
GLOW_HALO = 3.2               # halo multiplier for neon strokes
NEON_CYCLE = (CYAN, MAGENTA, NEON_RED, GREEN, WARM)

# ---- hours-spent-scrolling: screen-lit room ------------------------------
NEON_CYAN = CYAN              # the screen frame / her leading rim
NEON_MAGENTA = MAGENTA        # drifting video cards
NEON_AMBER = AMBER            # hour counters + timeline switch

SCREEN_TOP = (7, 11, 24)      # wall behind the glass
SCREEN_GLASS = (11, 22, 38)   # glass body inside the frame
SCREEN_EDGE = (0, 214, 244)   # frame stroke core
SCREEN_SHEEN = (120, 235, 255)  # diagonal glass sheen
SCANLINE = (0, 150, 180)      # faint LCD scanlines

CARD_BODY = (17, 15, 36)      # video card fill
CARD_CYAN = (0, 205, 236)     # cyan card glow
CARD_MAGENTA = (255, 54, 182)  # magenta card glow
CARD_FROST = (74, 96, 128)    # frozen / dimmed card

HOUR_AMBER = (255, 168, 60)   # the 1H / 3H / 5H+ counters
HOUR_GLOW = (255, 216, 138)   # counter core
CLOCK_RING = (92, 66, 44)     # unlit clock face on the wall

SWITCH_TRACK = (22, 18, 30)   # timeline switch bed
SWITCH_AMBER = (255, 176, 84)  # switch glow while on
SWITCH_OFF = (46, 52, 70)     # switch bed after power-off

ROOM_WALL = (18, 22, 40)      # lit room wall
ROOM_DESK = (24, 20, 34)      # desk slab
ROOM_FLOOR = (15, 17, 32)     # floor boards
ROOM_MIDNIGHT = (3, 4, 10)    # the room after the lights drop
HORIZON_AMBER = (255, 170, 70)  # warm closing horizon line

HAIR_LOCK = (6, 7, 14)        # hair body fill (same as silhouette body)
DUST = (150, 170, 200)        # dust motes in the screen light

# ---------------------------------------------------------------- easing


def clamp(x, a=0.0, b=1.0):
    return a if x < a else (b if x > b else x)


def lerp(a, b, t):
    return a + (b - a) * t


def ramp(t, a, b):
    """0 before a, 1 after b, linear between."""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return clamp((t - a) / (b - a))


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp(t)
    return t ** 3


def ease_in_out(t):
    t = clamp(t)
    return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def ease_out_back(t, s=1.70158):
    t = clamp(t)
    t -= 1
    return 1 + t * t * ((s + 1) * t + s)


def smoothstep(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def wobble(t, freq=1.0, phase=0.0):
    """-1..1 sine."""
    return math.sin(2 * math.pi * freq * t + phase)


def pulse(t, hz=1.0):
    """0..1 smooth pulse, for glints and frozen rims."""
    return 0.5 + 0.5 * math.sin(2 * math.pi * hz * t)


# ---------------------------------------------------------------- colour


def rgba(color, a=255):
    """RGB tuple -> RGBA with a clamped alpha."""
    return tuple(color[:3]) + (int(clamp(a, 0, 255)),)


def mix(a, b, t):
    """Linear RGB mix between two colours."""
    t = clamp(t)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def dim(color, factor):
    """Scale a colour toward black, keeping the neon hue."""
    return tuple(max(0, min(255, int(round(c * factor)))) for c in color[:3])


# ---------------------------------------------------------------- io


def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def dump_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)


# ---------------------------------------------------------------- fonts

_FONT_CACHE = {}

_FONT_DIRS = [
    "/usr/share/fonts",
    "/usr/local/share/fonts",
    "/data/data/com.termux/files/usr/share/fonts",
    str(Path.home() / ".fonts"),
]

_FONT_NAMES = {
    True: ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "NotoSans-Bold.ttf"],
    False: ["DejaVuSans.ttf", "LiberationSans-Regular.ttf", "NotoSans-Regular.ttf"],
}


def _find_font(bold):
    for root in _FONT_DIRS:
        if not os.path.isdir(root):
            continue
        for name in _FONT_NAMES[bold]:
            hits = glob.glob(os.path.join(root, "**", name), recursive=True)
            if hits:
                return sorted(hits)[0]
    return None


def font(size_1x, bold=True):
    """TrueType font at 1x size, cached (rendered at SS scale internally)."""
    key = (int(size_1x), bool(bold))
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    path = _find_font(bold) or _find_font(not bold)
    if not path:
        raise RuntimeError(
            "No usable TTF font found (looked for DejaVu/Liberation/Noto under "
            + ", ".join(_FONT_DIRS)
            + "). On Ubuntu install: sudo apt-get install -y fonts-dejavu-core"
        )
    f = ImageFont.truetype(path, max(8, int(round(size_1x * SS))))
    _FONT_CACHE[key] = f
    return f


def text_width(draw, s, size_1x, bold=True, stroke=0):
    """Width of text in 1x pixels."""
    f = font(size_1x, bold)
    box = draw.textbbox((0, 0), s, font=f, stroke_width=int(stroke * SS))
    return (box[2] - box[0]) / SS
