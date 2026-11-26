"""Shared constants, easing, JSON I/O and font lookup for the 40 s episode.

Design 04 — "Neon key on the counter": a locked front door at night, an
unlit hallway and one brass key glinting on the kitchen counter behind the
glass. Every scene is drawn in near-black with sharp silhouettes edged by
double-offset rim light — CYAN from the street outside, MAGENTA from the
neon seen through the windows and AMBER from the lock cylinder and the key
itself. A soft halo pass sits behind every neon stroke, so the three accents
read as real light sources.

Palette roles in this episode:
    CYAN      the street outside, the hero's leading rim, the way out
    MAGENTA   neon spill through glass, the shadows that give you away
    AMBER     the lock, the key, the counter edge you are racing toward
    NEON_RED  the panic beats (empty pockets, the creak shock)

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
CYAN = (0, 235, 255)          # street outside / active state
MAGENTA = (255, 40, 196)      # neon sign spill
NEON_RED = (255, 46, 64)      # panic beats, alerts
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
AMBER = (255, 176, 84)        # lamps, lock cylinders, night windows

# sketch FX
SKETCH = 1.6                  # default hand-drawn jitter, 1x px
GLOW_HALO = 3.2               # halo multiplier for neon strokes
NEON_CYCLE = (CYAN, MAGENTA, NEON_RED, GREEN, WARM)

# ---- forgotten-key-on-the-counter: cinematic neon interior ---------------
NEON_CYAN = CYAN              # rim light / street side / the way out
NEON_MAGENTA = MAGENTA        # neon seen through the glass
NEON_AMBER = AMBER            # lock cylinder + brass key
NIGHT_WALL = (13, 15, 30)     # exterior / interior wall
NIGHT_DEEP = (5, 6, 13)       # deepest interior black
WALL_DEEP = (17, 19, 36)      # hallway wall panel
HALL_FLOOR = (17, 18, 34)     # floor boards
HALL_SHADOW = (6, 7, 15)      # the deep stretched shadows
DOOR_PANEL = (24, 17, 28)     # the heavy front door slab
DOOR_FRAME = (34, 28, 50)     # door frame / glass door frame
DOOR_GAP = (0, 156, 186)      # cyan night flooding the open doorway
PANE = (20, 30, 50)           # glass pane body
PANE_CYAN = (10, 66, 84)      # cyan neon seen through glass
PANE_MAGENTA = (78, 14, 66)   # magenta neon seen through glass
INTERIOR_DARK = (8, 9, 18)    # the unlit room behind the glass
COUNTER_TOP = (42, 31, 34)    # kitchen counter worktop
COUNTER_BODY = (21, 16, 27)   # counter cupboards
KEY_BRASS = (255, 200, 100)   # the key
KEY_GLOW = (255, 232, 150)    # key glint core
LOCK_RING = (255, 190, 90)    # lock cylinder face
TABLE_SIL = (14, 13, 26)      # table silhouette
CHAIR_SIL = (12, 11, 22)      # chair silhouette
REFLECT_WHITE = (236, 248, 255)  # blown-out reflection / glare
DUST = (150, 170, 200)        # dust motes in the light

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
