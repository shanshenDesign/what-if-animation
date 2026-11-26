"""Shared constants, easing, JSON I/O and font lookup for the 40 s episode.

Design 03 — "Cinematic neon silhouettes": every scene is a night exterior or
an unlit interior drawn in near-black, with sharp silhouetted figures edged
by bold rim light — CYAN on the hero's leading side, MAGENTA from neon signage
and AMBER from streetlamps / convenience-store windows. A soft halo pass sits
behind every stroke, so the three neon accents read as real light sources.

Palette roles in this episode:
    CYAN      the hero, the phone, the charger, safe states
    MAGENTA   neon sign / puddle reflection, the obstacles that blind you
    AMBER     streetlamp, store window, the outlet you are racing toward
    NEON_RED  the 1 % battery alarm

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
# Design 02 — Neon-on-black sketch.
BG_TOP = (4, 6, 14)           # canvas, top
BG_BOT = (12, 16, 32)         # canvas, bottom
NIGHT_TOP = BG_TOP            # back-compat alias (old gradient name)
NIGHT_BOT = BG_BOT

CREAM = (234, 250, 255)       # primary figure stroke: ice-white neon
CYAN = (0, 235, 255)          # you / active state
MAGENTA = (255, 40, 196)      # everyone else's highlight reel
NEON_RED = (255, 46, 64)      # motion lines, X marks, alerts
RED = NEON_RED                # back-compat alias
GREEN = (126, 255, 158)       # calm / breathe
LIME = GREEN
BLUE = (92, 150, 255)         # phone glow
PINK = MAGENTA                # back-compat alias
PINK_DEEP = (196, 0, 148)
WARM = (255, 196, 64)         # clock / horizon glow
GOLD = (255, 226, 130)
INK = (4, 5, 10)              # outlines and text on bright fills
WHITE = (255, 255, 255)
DIM = (86, 110, 140)          # secondary text
GRID = (18, 26, 44)           # unlit construction grid
PAPER = (16, 20, 34)          # dark card / panel fill

# sci-fi bedroom / flashbang episode (extends the scifi-toon palette in
# scenes.py: flat bands, heavy ink linework, one glowing device)
NIGHT_BLACK = (2, 3, 8)       # the 01:30 AM canvas
WALL_DEEP = (18, 26, 46)      # unlit bedroom wall panel
WALL_LIT = (58, 104, 138)     # same wall under the flashbang
SHEET_DEEP = (26, 34, 58)     # blanket / pillow in the dark
SHEET_LIT = (176, 214, 236)   # blanket / pillow, stadium lit
FLASH_CORE = (236, 255, 255)  # centre of the blast, almost white
FLASH_RAY = (128, 246, 255)   # cyan-white light rays
FLASH_EDGE = (60, 160, 220)   # bounce light on ink outlines
HUD_GLITCH_RED = (255, 46, 64)  # retina-damage readout
HUD_GLITCH_CYAN = (0, 235, 255)  # chromatic split of the glitch

# environment layers (deliberately duller than the figures)
STEEL = (104, 140, 176)       # building edges, furniture, room detail
STEEL_DIM = (54, 76, 104)     # brick courses, floor grid, far skyline
GLASS = (24, 38, 60)          # window / screen interiors
CHALK = (168, 196, 214)       # secondary labels on props
AMBER = (255, 176, 84)        # lamps, camera tally, night windows

# sketch FX
SKETCH = 1.6                  # default hand-drawn jitter, 1x px
GLOW_HALO = 3.2               # halo multiplier for neon strokes
NEON_CYCLE = (CYAN, MAGENTA, NEON_RED, GREEN, WARM)

# ---- last-charge-1-percent: cinematic neon night exteriors ----------------
NEON_CYAN = CYAN              # rim light / hero side
NEON_MAGENTA = MAGENTA        # neon sign + puddle reflection
NEON_AMBER = AMBER            # streetlamp + convenience-store window
ROAD = (10, 12, 22)           # asphalt
ROAD_WET = (20, 24, 44)       # wet asphalt streaks
SIDEWALK = (16, 18, 32)       # kerb / pavement band
BUILDING = (7, 9, 18)         # far building silhouettes
HALL_WALL = (13, 16, 30)      # hallway wall
HALL_DARK = (6, 7, 14)        # hallway shadow side
DOOR_WOOD = (22, 16, 26)      # creaking door panel
GLARE = (232, 244, 255)       # blown-out screen / lamp core
STORE_GLOW = (255, 214, 140)  # convenience-store window light
PUD_GLASS = (16, 20, 38)      # puddle body
OUTLET_METAL = (46, 54, 74)   # wall outlet plate
CHARGER = (30, 36, 56)        # charging brick
SCREEN_OFF = (5, 7, 14)       # dead phone screen
SCREEN_ON = (150, 246, 255)   # live phone screen

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
    """0..1 smooth pulse, for REC lights and frozen rims."""
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


# ---------------------------------------------------------------- time freeze


def frozen_clock(t, freeze_t, thaw_t, span=10.0):
    """Countdown state for the pause power.

    Returns (seconds_left, progress). progress runs 0 -> 1 between the moment
    time freezes and the moment it unpauses; seconds_left is a readable
    10.0 -> 0.0 countdown mapped onto that stretch of video.
    """
    if t <= freeze_t:
        return span, 0.0
    if t >= thaw_t:
        return 0.0, 1.0
    p = clamp((t - freeze_t) / max(0.001, thaw_t - freeze_t))
    return span * (1.0 - p), p


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
