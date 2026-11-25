"""Final 35 s audio: fit the narration to length, add story SFX, normalise.

    python src/audio.py <project>

    build/raw.wav  --(atempo if timeline.tempo>1)--> build/mix.wav (exactly 35.0 s)

SFX are generated in code (no asset downloads): a bubble pop, a soft whoosh
for the memory flood, a stamp thud and a dawn chime, all ducked well under
the narration.
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

    raise ValueError(f"unknown sfx kind: {kind}")


LEVELS = {"pop": 0.16, "thud": 0.22, "chime": 0.13, "whoosh": 0.10}


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
        s = sfx(cue["kind"], sr, rng) * LEVELS[cue["kind"]]
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
