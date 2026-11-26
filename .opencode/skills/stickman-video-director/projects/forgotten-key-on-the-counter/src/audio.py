"""Final 40 s audio: fit the narration to length, add story SFX, normalise.

    python src/audio.py <project>

    build/raw.wav  --(atempo if timeline.tempo>1)--> build/mix.wav (exactly 40.0 s)

SFX are generated in code (no asset downloads), tuned to this episode's
obstacle run: a heavy latch click, pocket pats, a floorboard creak, the hum
of neon behind glass, hushed footsteps, a key jingle and one clean unlock,
all ducked well under the narration.
"""
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

from common import load_json

SR = 24000


def read_wav(path):
    with wave.open(str(path), "rb") as w:
        assert w.getnchannels() == 1 and w.getsampwidth() == 2, "expected mono 16-bit wav"
        sr = w.getframerate()
        x = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768.0
    return x, sr


def write_wav(path, y, sr):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(y, -1.0, 1.0) * 32767.0).astype("<i2").tobytes())


def _lp(noise, k):
    """Cheap low-pass by convolution with a normalised window."""
    k = np.asarray(k, dtype=np.float64)
    k /= k.sum()
    return np.convolve(noise, k, mode="same")


def sfx(kind, sr, rng):
    """Return a short mono float array for the requested cue."""
    if kind == "latch":                     # heavy door latch / lock click
        n = int(0.55 * sr)
        t = np.arange(n) / sr
        body = np.sin(2 * np.pi * 96 * t) * np.exp(-t * 16) * 0.85
        clack = _lp(rng.standard_normal(n), np.exp(-np.arange(26) / 5.0)) * np.exp(-t * 46) * 2.4
        pin = np.sin(2 * np.pi * 1750 * t) * np.exp(-t * 34) * 0.35
        spring = np.sin(2 * np.pi * (520 + 260 * np.exp(-t * 12)) * t) * np.exp(-t * 9) * 0.18
        return (body + clack + pin + spring) * 0.85

    if kind == "pat":                       # hand slapping an empty pocket
        n = int(0.30 * sr)
        t = np.arange(n) / sr
        cloth = _lp(rng.standard_normal(n), np.exp(-np.arange(120) / 16.0))
        env = (1 - np.exp(-t * 160)) * np.exp(-t * 17)
        tap = np.sin(2 * np.pi * 150 * t) * np.exp(-t * 40) * 0.35
        return (cloth * 2.6 * env + tap) * 0.8

    if kind == "creak":                     # floorboard groan + settle tick
        n = int(0.95 * sr)
        t = np.arange(n) / sr
        f = 150 + 60 * np.sin(2 * np.pi * 2.1 * t) + 26 * np.sin(2 * np.pi * 6.4 * t)
        ph = 2 * np.pi * np.cumsum(f) / sr
        grain = _lp(rng.standard_normal(n), np.exp(-np.arange(70) / 12.0))
        env = (1 - np.exp(-t * 26)) * np.exp(-t * 2.1)
        wood = (0.55 * np.sin(ph) + 0.45 * grain * (0.5 + 0.5 * np.sin(2 * np.pi * 3.4 * t)))
        tick = np.zeros(n)
        i = int(0.72 * sr)
        m = min(n - i, int(0.08 * sr))
        tt = np.arange(m) / sr
        tick[i:i + m] = (np.sin(2 * np.pi * 2300 * tt)
                         + 0.5 * np.sin(2 * np.pi * 3600 * tt)) * np.exp(-tt * 55)
        return wood * env * 0.8 + tick * 0.35

    if kind == "hum":                       # neon tube hum behind glass
        n = int(1.30 * sr)
        t = np.arange(n) / sr
        env = (1 - np.exp(-t * 45)) * np.exp(-t * 1.7)
        mains = (0.55 * np.sin(2 * np.pi * 100 * t)
                 + 0.28 * np.sin(2 * np.pi * 200 * t)
                 + 0.14 * np.sin(2 * np.pi * 300 * t))
        tube = 0.10 * np.sin(2 * np.pi * 1180 * t + 3.0 * np.sin(2 * np.pi * 7 * t))
        crackle = (np.sin(2 * np.pi * 1450 * t) > 0.955) * 0.30
        return (mains + tube + crackle) * env * 0.7

    if kind == "step":                      # hushed barefoot step
        n = int(0.34 * sr)
        t = np.arange(n) / sr
        soft = _lp(rng.standard_normal(n), np.exp(-np.arange(200) / 26.0))
        env = (1 - np.exp(-t * 90)) * np.exp(-t * 13)
        low = np.sin(2 * np.pi * 74 * t) * np.exp(-t * 26) * 0.30
        return (soft * 2.2 * env + low) * 0.7

    if kind == "jingle":                    # brass key ring
        n = int(0.75 * sr)
        t = np.arange(n) / sr
        out = np.zeros(n)
        for at, f, g in ((0.00, 3150, 1.0), (0.07, 2480, 0.8),
                         (0.14, 3960, 0.7), (0.24, 2870, 0.6),
                         (0.33, 4320, 0.45)):
            i = int(at * sr)
            m = min(n - i, int(0.30 * sr))
            tt = np.arange(m) / sr
            out[i:i + m] += (np.sin(2 * np.pi * f * tt)
                             + 0.4 * np.sin(2 * np.pi * f * 1.61 * tt)) * np.exp(-tt * 16) * g
        shimmer = _lp(rng.standard_normal(n), np.exp(-np.arange(40) / 6.0))
        out += shimmer * np.exp(-t * 24) * 0.5
        return out * 0.8

    if kind == "unlock":                    # cylinder turn + clean click
        n = int(0.70 * sr)
        t = np.arange(n) / sr
        turn = np.sin(2 * np.pi * (430 + 380 * np.clip(t / 0.22, 0, 1)) * t)
        turn *= np.exp(-t * 7.5) * 0.35
        clack = _lp(rng.standard_normal(n), np.exp(-np.arange(22) / 4.0))
        clack *= np.exp(-np.maximum(t - 0.26, 0) * 60) * 2.6
        thunk = np.sin(2 * np.pi * 118 * t) * np.exp(-np.maximum(t - 0.3, 0) * 13) * 0.55
        ring = np.sin(2 * np.pi * 1620 * t) * np.exp(-np.maximum(t - 0.28, 0) * 9) * 0.14
        return (turn + clack + thunk + ring) * 0.85

    if kind == "glint":                     # the key catches the light
        n = int(0.60 * sr)
        t = np.arange(n) / sr
        sweep = 1500 + 2600 * (t / 0.6) ** 1.6
        ph = 2 * np.pi * np.cumsum(sweep) / sr
        env = (1 - np.exp(-t * 34)) * np.exp(-t * 4.2)
        dust = _lp(rng.standard_normal(n), np.exp(-np.arange(60) / 9.0)) * np.exp(-t * 12)
        return (0.55 * np.sin(ph) + 0.22 * np.sin(ph * 2.01) + dust * 0.5) * env * 0.75

    if kind == "slide":                     # body sliding across the floor
        n = int(0.72 * sr)
        t = np.arange(n) / sr
        rub = _lp(rng.standard_normal(n), np.exp(-np.arange(260) / 34.0))
        env = np.sin(np.pi * np.clip(t / 0.72, 0, 1)) ** 1.3
        swish = 0.3 * np.sin(2 * np.pi * (240 + 420 * (t / 0.72)) * t) * env
        return (rub * 3.0 * env + swish) * 0.7

    if kind == "pop":                       # bubble appears
        n = int(0.09 * sr)
        t = np.arange(n) / sr
        f = 300 + 700 * np.exp(-t * 22)
        ph = 2 * np.pi * np.cumsum(f) / sr
        return np.sin(ph) * np.exp(-t * 26) * 0.9

    if kind == "thud":                      # heavy step / stamp lands
        n = int(0.26 * sr)
        t = np.arange(n) / sr
        body = np.sin(2 * np.pi * 88 * t) * np.exp(-t * 14)
        click = rng.standard_normal(n) * np.exp(-t * 55) * 0.35
        return (body + click) * 0.9

    if kind == "chime":                     # the door swings open
        n = int(1.5 * sr)
        t = np.arange(n) / sr
        env = np.exp(-t * 2.4) * (1 - np.exp(-t * 90))
        x = (np.sin(2 * np.pi * 1046.5 * t) * 0.55
             + np.sin(2 * np.pi * 1318.5 * t) * 0.35
             + np.sin(2 * np.pi * 2093.0 * t) * 0.12)
        return x * env

    if kind == "whoosh":                    # quick movement past camera
        n = int(0.9 * sr)
        t = np.arange(n) / sr
        noise = rng.standard_normal(n)
        k = np.exp(-np.arange(600) / 90.0)
        k /= k.sum()
        soft = np.convolve(noise, k, mode="same")
        env = np.sin(np.pi * np.clip(t / 0.9, 0, 1)) ** 1.6
        return soft * env * 1.6

    if kind == "tick":                      # small mechanical click
        n = int(0.075 * sr)
        t = np.arange(n) / sr
        return (0.62 * np.sin(2 * np.pi * 1850 * t)
                + 0.30 * np.sin(2 * np.pi * 3260 * t)) * np.exp(-t * 62)

    if kind not in LEVELS:
        # Fallback for unknown or future cue kinds so the pipeline never crashes
        n = int(0.15 * sr)
        t = np.arange(n) / sr
        return np.sin(2 * np.pi * 440 * t) * np.exp(-t * 20) * 0.5


LEVELS = {"latch": 0.26, "pat": 0.15, "creak": 0.20, "hum": 0.11,
          "step": 0.13, "jingle": 0.17, "unlock": 0.28, "glint": 0.13,
          "slide": 0.14, "pop": 0.16, "thud": 0.22, "chime": 0.13,
          "whoosh": 0.10, "tick": 0.11}


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: python src/audio.py <project>")
    project = Path(sys.argv[1])
    tl = load_json(project / "build" / "timeline.json")
    duration = float(tl["duration"])
    tempo = float(tl.get("tempo", 1.0))

    src = project / "build" / "raw.wav"
    if tempo > 1.0005:
        if not shutil.which("ffmpeg"):
            raise SystemExit("ffmpeg is required to re-time the narration (atempo)")
        fit = project / "build" / "fit.wav"
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
               "-filter:a", f"atempo={tempo:.6f}", "-c:a", "pcm_s16le", str(fit)]
        print(" ".join(cmd), flush=True)
        subprocess.run(cmd, check=True)
        src = fit

    x, sr = read_wav(src)
    target = int(round(duration * sr))
    if len(x) < target:
        x = np.pad(x, (0, target - len(x)))
    else:
        x = x[:target]

    rng = np.random.default_rng(11)
    for cue in tl.get("sfx", []):
        kind = cue["kind"]
        level = LEVELS.get(kind, 0.15)
        s = sfx(kind, sr, rng) * level
        a = int(cue["t"] * sr)
        b = min(len(x), a + len(s))
        if a < len(x):
            x[a:b] += s[: b - a]

    peak = float(np.abs(x).max()) or 1.0
    x = x / peak * 0.92
    out = project / "build" / "mix.wav"
    write_wav(out, x, sr)
    print(f"build/mix.wav  {len(x) / sr:.2f}s, {len(tl.get('sfx', []))} sfx, peak {peak:.3f} -> 0.92",
          flush=True)


if __name__ == "__main__":
    main()
