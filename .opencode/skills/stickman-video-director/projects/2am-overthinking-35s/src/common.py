"""Shared constants, easing, JSON I/O and font lookup for the 2 AM episode.

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
NIGHT_TOP = (15, 18, 40)
NIGHT_BOT = (33, 37, 72)
CREAM = (246, 240, 228)     # stickman stroke
WARM = (255, 197, 94)       # lamp / clock glow
GOLD = (255, 220, 140)
PINK = (255, 122, 154)      # cringe memories
PINK_DEEP = (224, 84, 124)
GREEN = (112, 226, 178)     # calm / breathe
RED = (255, 92, 96)         # urgent
BLUE = (126, 170, 255)      # phone glow
INK = (10, 12, 26)
WHITE = (255, 255, 255)
DIM = (128, 134, 180)
PAPER = (242, 233, 214)     # memory card inside the thought bubble

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
