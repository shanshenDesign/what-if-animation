"""Final 40 s audio: fit the narration to length, add story SFX, normalise.

    python src/audio.py <project>

    build/raw.wav  --(atempo if timeline.tempo>1)--> build/mix.wav (exactly 40.0 s)

SFX are generated in code (no asset downloads), tuned for this episode's
obstacle run: a low-battery drain, a streetlamp buzz, a door creak, a puddle
ripple and the final charger click sit alongside the old pop / thud / chime /
whoosh cues, all ducked well under the narration.
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


def sfx(kind, sr, rng):
    """Return a short mono float array for the requested cue."""
    if kind == "pop":                       # bubble appears
        n = int(0.09 * sr)
        t = np.arange(n) / sr
        f = 300 + 700 * np.exp(-t * 22)
        ph = 2 * np.pi * np.cumsum(f) / sr
        return np.sin(ph) * np.exp(-t * 26) * 0.9

    if kind == "beep":                      # electronic beep / alert
        n = int(0.12 * sr)
        t = np.arange(n) / sr
        env = (1 - np.exp(-t * 120)) * np.exp(-t * 18)
        return np.sin(2 * np.pi * 1760 * t) * env * 0.8

    if kind == "charge":                    # power building / energy build
        n = int(0.5 * sr)
        t = np.arange(n) / sr
        sweep = 200 + 1200 * (t / 0.5) ** 2
        ph = 2 * np.pi * np.cumsum(sweep) / sr
        env = (1 - np.exp(-t * 30)) * np.exp(-t * 4)
        return np.sin(ph) * env * 0.85

    if kind == "alarm":                     # warning alarm pulse
        n = int(0.35 * sr)
        t = np.arange(n) / sr
        env = (1 - np.exp(-t * 80)) * np.exp(-t * 8)
        tone = np.sin(2 * np.pi * 880 * t) + 0.5 * np.sin(2 * np.pi * 1760 * t)
        return tone * env * 0.8

    if kind == "laser":                     # sci-fi beam / zap
        n = int(0.25 * sr)
        t = np.arange(n) / sr
        sweep = 1500 - 1000 * (t / 0.25)
        ph = 2 * np.pi * np.cumsum(sweep) / sr
        env = (1 - np.exp(-t * 150)) * np.exp(-t * 20)
        return np.sin(ph) * env * 0.85

    if kind == "glitch":                    # digital artifact / error
        n = int(0.2 * sr)
        t = np.arange(n) / sr
        noise = rng.standard_normal(n)
        env = np.exp(-t * 25)
        return noise * env * 0.7

    if kind == "thud":                      # URGENT stamp lands
        n = int(0.26 * sr)
        t = np.arange(n) / sr
        body = np.sin(2 * np.pi * 88 * t) * np.exp(-t * 14)
        click = rng.standard_normal(n) * np.exp(-t * 55) * 0.35
        return (body + click) * 0.9

    if kind == "chime":                     # dawn
        n = int(1.5 * sr)
        t = np.arange(n) / sr
        env = np.exp(-t * 2.4) * (1 - np.exp(-t * 90))
        x = (np.sin(2 * np.pi * 1046.5 * t) * 0.55
             + np.sin(2 * np.pi * 1318.5 * t) * 0.35
             + np.sin(2 * np.pi * 2093.0 * t) * 0.12)
        return x * env

    if kind == "whoosh":                    # memories flood out
        n = int(0.9 * sr)
        t = np.arange(n) / sr
        noise = rng.standard_normal(n)
        k = np.exp(-np.arange(600) / 90.0)
        k /= k.sum()
        soft = np.convolve(noise, k, mode="same")
        env = np.sin(np.pi * np.clip(t / 0.9, 0, 1)) ** 1.6
        return soft * env * 1.6

    if kind == "freeze":                    # time locks: cold rising shimmer
        n = int(0.72 * sr)
        t = np.arange(n) / sr
        run = np.cumsum(rng.standard_normal(n))
        run = np.diff(run, prepend=run[0]) * 0.22
        k = np.exp(-np.arange(240) / 44.0)
        k /= k.sum()
        glass = np.convolve(rng.standard_normal(n), k, mode="same")
        sweep = 420 + 1850 * (t / 0.72) ** 1.7
        ph = 2 * np.pi * np.cumsum(sweep) / sr
        env = (1 - np.exp(-t * 28)) * np.exp(-t * 3.4)
        return (0.20 * run + 0.55 * glass
                + 0.24 * np.sin(ph) + 0.10 * np.sin(ph * 2.01)) * env

    if kind == "tick":                      # wall clock click
        n = int(0.075 * sr)
        t = np.arange(n) / sr
        return (0.62 * np.sin(2 * np.pi * 1850 * t)
                + 0.30 * np.sin(2 * np.pi * 3260 * t)) * np.exp(-t * 62)

    if kind == "splash":                    # coffee cups the floor
        n = int(0.42 * sr)
        t = np.arange(n) / sr
        k = np.exp(-np.arange(180) / 28.0)
        k /= k.sum()
        wet = np.convolve(rng.standard_normal(n), k, mode="same")
        env = (1 - np.exp(-t * 90)) * np.exp(-t * 9.5)
        body = np.sin(2 * np.pi * 120 * t) * np.exp(-t * 18) * 0.30
        drops = np.zeros(n)
        for at, f in ((0.13, 720), (0.21, 980), (0.28, 610)):
            i = int(at * sr)
            m = min(n - i, int(0.055 * sr))
            tt = np.arange(m) / sr
            drops[i:i + m] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 70) * 0.35
        return (wet * 1.8 + body + drops) * env

    if kind == "record":                    # CCTV tally / tape beep
        n = int(0.22 * sr)
        t = np.arange(n) / sr
        env = (1 - np.exp(-t * 120)) * np.exp(-t * 13)
        chirp = np.sin(2 * np.pi * (1160 * t + 2400 * t * t))
        return chirp * env * 0.85

    if kind == "drain":                     # low-battery fall (descending)
        n = int(0.55 * sr)
        t = np.arange(n) / sr
        sweep = 620 * np.exp(-t * 4.4) + 90
        ph = 2 * np.pi * np.cumsum(sweep) / sr
        env = (1 - np.exp(-t * 40)) * np.exp(-t * 1.4)
        wob = 0.75 + 0.25 * np.sin(2 * np.pi * 5.0 * t)
        return (np.sin(ph) + 0.35 * np.sin(ph * 2.0)) * env * wob * 0.8

    if kind == "buzz":                      # neon streetlamp transformer hum
        n = int(0.75 * sr)
        t = np.arange(n) / sr
        env = (1 - np.exp(-t * 60)) * np.exp(-t * 3.2)
        a = 0.6 * np.sin(2 * np.pi * 100 * t) + 0.3 * np.sin(2 * np.pi * 200 * t)
        b = 0.25 * rng.standard_normal(n) * np.exp(-t * 6)
        crackle = (np.sin(2 * np.pi * 1500 * t) > 0.93) * 0.35
        return (a + b + crackle) * env * 0.75

    if kind == "creak":                     # door hinge / house corner groan
        n = int(0.85 * sr)
        t = np.arange(n) / sr
        f = 300 + 150 * np.sin(2 * np.pi * 2.3 * t) + 40 * np.sin(2 * np.pi * 7.0 * t)
        ph = 2 * np.pi * np.cumsum(f) / sr
        k = np.exp(-np.arange(90) / 16.0)
        k /= k.sum()
        grain = np.convolve(rng.standard_normal(n), k, mode="same")
        env = (1 - np.exp(-t * 22)) * np.exp(-t * 1.6)
        return (0.5 * np.sin(ph) + 0.35 * grain * (0.5 + 0.5 * np.sin(2 * np.pi * 3.1 * t))) * env * 0.7

    if kind == "ripple":                    # puddle disturbed, water rings
        n = int(0.6 * sr)
        t = np.arange(n) / sr
        k = np.exp(-np.arange(150) / 24.0)
        k /= k.sum()
        wet = np.convolve(rng.standard_normal(n), k, mode="same")
        rings = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * (3.0 + i))
                    for i, f in enumerate((520, 780, 1180)))
        env = (1 - np.exp(-t * 70)) * np.exp(-t * 3.6)
        return (wet * 1.4 + 0.45 * rings) * env * 0.8

    if kind == "plug":                      # charger click + power handshake
        n = int(0.34 * sr)
        t = np.arange(n) / sr
        click = rng.standard_normal(n) * np.exp(-t * 90) * 0.9
        latch = np.sin(2 * np.pi * 320 * t) * np.exp(-t * 40) * 0.5
        handshake = np.sin(2 * np.pi * (1400 + 900 * np.clip(t / 0.16, 0, 1)) * t)
        handshake *= np.exp(-t * 9) * 0.35
        return (click + latch + handshake) * 0.9

    if kind not in LEVELS:
        # Fallback for unknown or future cue kinds so the pipeline never crashes
        n = int(0.15 * sr)
        t = np.arange(n) / sr
        return np.sin(2 * np.pi * 440 * t) * np.exp(-t * 20) * 0.5


LEVELS = {"pop": 0.16, "thud": 0.22, "chime": 0.13, "whoosh": 0.10,
          "freeze": 0.18, "tick": 0.11, "splash": 0.17, "record": 0.14,
          "beep": 0.15, "charge": 0.18, "alarm": 0.16, "laser": 0.16,
          "glitch": 0.14, "drain": 0.15, "buzz": 0.13, "creak": 0.16,
          "ripple": 0.15, "plug": 0.20}


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
