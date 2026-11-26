"""Final 40 s audio: fit the narration to length, add story SFX, normalise.

    python src/audio.py <project>

    build/raw.wav  --(atempo if timeline.tempo>1)--> build/mix.wav (exactly 40.0 s)

SFX are generated in code (no asset downloads), tuned to this episode's
scroll-awareness beat: a knuckle tap on glass, soft swipe whooshes, digital
clock ticks, the ambient room hum, a freeze chime and one clean power-off
click, all ducked well under the narration.
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
    if kind == "tap":                       # knuckle knocking on the glass
        n = int(0.42 * sr)
        t = np.arange(n) / sr
        knock = np.sin(2 * np.pi * 720 * t) * np.exp(-t * 34) * 0.9
        thump = np.sin(2 * np.pi * 148 * t) * np.exp(-t * 22) * 0.55
        glass = (np.sin(2 * np.pi * 2450 * t)
                 + 0.5 * np.sin(2 * np.pi * 3670 * t)) * np.exp(-t * 13) * 0.30
        grain = _lp(rng.standard_normal(n), np.exp(-np.arange(30) / 5.0)) * np.exp(-t * 70)
        return (knock + thump + glass + grain * 1.4) * 0.85

    if kind == "swipe":                     # thumb flicking a card away
        n = int(0.50 * sr)
        t = np.arange(n) / sr
        noise = rng.standard_normal(n)
        k = np.exp(-np.arange(240) / 30.0)
        soft = _lp(noise, k)
        sweep = 520 + 1500 * (t / 0.5) ** 1.7
        ph = 2 * np.pi * np.cumsum(sweep) / sr
        env = np.sin(np.pi * np.clip(t / 0.5, 0, 1)) ** 1.5
        air = 0.22 * np.sin(ph) * env
        return (soft * 3.2 * env + air) * 0.75

    if kind == "tick":                      # digital counter blip
        n = int(0.20 * sr)
        t = np.arange(n) / sr
        first = (0.60 * np.sin(2 * np.pi * 1760 * t)
                 + 0.30 * np.sin(2 * np.pi * 2640 * t)) * np.exp(-t * 40)
        i = int(0.075 * sr)
        m = n - i
        tt = np.arange(m) / sr
        second = 0.45 * np.sin(2 * np.pi * 2360 * tt) * np.exp(-tt * 48)
        out = first.copy()
        out[i:] += second
        return out * 0.9

    if kind == "hum":                       # ambient room / screen hum
        n = int(2.20 * sr)
        t = np.arange(n) / sr
        env = (1 - np.exp(-t * 6.0)) * np.exp(-t * 0.55)
        mains = (0.50 * np.sin(2 * np.pi * 60 * t)
                 + 0.26 * np.sin(2 * np.pi * 120 * t + 0.7)
                 + 0.13 * np.sin(2 * np.pi * 180 * t + 1.4))
        beat = 0.18 * np.sin(2 * np.pi * 0.9 * t)
        breath = 0.10 * np.sin(2 * np.pi * 55.5 * t + 2.0 * np.sin(2 * np.pi * 0.4 * t))
        air = _lp(rng.standard_normal(n), np.exp(-np.arange(320) / 44.0)) * 0.20
        return (mains + beat + breath + air) * env * 0.55

    if kind == "chime":                     # freeze chime (cards stop)
        n = int(1.90 * sr)
        t = np.arange(n) / sr
        env = np.exp(-t * 1.9) * (1 - np.exp(-t * 120))
        shimmer = 0.16 * np.sin(2 * np.pi * 6222 * t + 2.5 * np.sin(2 * np.pi * 3.1 * t))
        shimmer *= np.exp(-t * 3.4)
        x = (np.sin(2 * np.pi * 1318.5 * t) * 0.50
             + np.sin(2 * np.pi * 1975.5 * t) * 0.30
             + np.sin(2 * np.pi * 2637.0 * t) * 0.14
             + shimmer)
        frost = _lp(rng.standard_normal(n), np.exp(-np.arange(90) / 14.0))
        frost *= np.exp(-t * 9.0) * 0.35
        return (x * env + frost) * 0.85

    if kind == "power":                     # the switch: click + dying sweep
        n = int(0.75 * sr)
        t = np.arange(n) / sr
        click = _lp(rng.standard_normal(n), np.exp(-np.arange(20) / 4.0))
        click *= np.exp(-t * 90) * 2.4
        sweep_f = 940 * np.exp(-t * 6.5) + 90
        ph = 2 * np.pi * np.cumsum(sweep_f) / sr
        fall = np.sin(ph) * np.exp(-t * 4.2) * 0.75
        thunk = np.sin(2 * np.pi * 96 * t) * np.exp(-np.maximum(t - 0.34, 0) * 16) * 0.45
        tail = _lp(rng.standard_normal(n), np.exp(-np.arange(120) / 20.0))
        tail *= np.exp(-np.maximum(t - 0.30, 0) * 9) * 0.25
        return (click + fall + thunk + tail) * 0.8

    if kind == "pop":                       # bubble appears
        n = int(0.09 * sr)
        t = np.arange(n) / sr
        f = 300 + 700 * np.exp(-t * 22)
        ph = 2 * np.pi * np.cumsum(f) / sr
        return np.sin(ph) * np.exp(-t * 26) * 0.9

    if kind == "glint":                     # UI sparkle
        n = int(0.60 * sr)
        t = np.arange(n) / sr
        sweep = 1500 + 2600 * (t / 0.6) ** 1.6
        ph = 2 * np.pi * np.cumsum(sweep) / sr
        env = (1 - np.exp(-t * 34)) * np.exp(-t * 4.2)
        dust = _lp(rng.standard_normal(n), np.exp(-np.arange(60) / 9.0)) * np.exp(-t * 12)
        return (0.55 * np.sin(ph) + 0.22 * np.sin(ph * 2.01) + dust * 0.5) * env * 0.75

    if kind == "thud":                      # counter lands on the wall
        n = int(0.30 * sr)
        t = np.arange(n) / sr
        body = np.sin(2 * np.pi * 84 * t) * np.exp(-t * 13)
        click = rng.standard_normal(n) * np.exp(-t * 52) * 0.35
        return (body + click) * 0.9

    if kind not in LEVELS:
        # Fallback for unknown or future cue kinds so the pipeline never crashes
        n = int(0.15 * sr)
        t = np.arange(n) / sr
        return np.sin(2 * np.pi * 440 * t) * np.exp(-t * 20) * 0.5


LEVELS = {"tap": 0.24, "swipe": 0.12, "tick": 0.14, "hum": 0.08,
          "chime": 0.16, "power": 0.28, "pop": 0.16, "glint": 0.13,
          "thud": 0.22}


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

    rng = np.random.default_rng(7)
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
