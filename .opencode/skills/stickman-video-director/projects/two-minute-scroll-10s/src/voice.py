"""Narration: Kokoro-82M TTS (Apache-2.0) via kokoro-onnx. No account, no API key.

    python src/voice.py <project>

Reads <project>/script.json, synthesises every line, and writes:
    build/raw.wav    lead + speech with natural gaps + outro (24 kHz int16)
    build/lines.json exact start/end of each line inside raw.wav

Gaps are chosen so the whole track lands just under the target length at
tempo 1.0; if the voice runs long, plan.py squeezes everything with a small
atempo and rescales all timings together, so captions stay in sync.

Model files (~353 MB) are downloaded once into $STICKMAN_HOME/kokoro
(default ~/.stickman-director/kokoro) and reused by later runs/CI cache.

Line-window technique (per-line synthesis + silence trimming) follows the
proven approach in .opencode/skills/faceless-shorts/scripts/voice.py.
"""
import sys
import urllib.request
import wave
from pathlib import Path

import numpy as np

from common import dump_json, load_json

SR = 24000
FILES = {
    "kokoro-v1.0.onnx": (
        "https://github.com/thewh1teagle/kokoro-onnx/releases/"
        "download/model-files-v1.0/kokoro-v1.0.onnx"
    ),
    "voices-v1.0.bin": (
        "https://github.com/thewh1teagle/kokoro-onnx/releases/"
        "download/model-files-v1.0/voices-v1.0.bin"
    ),
}
MIN_SIZE = {"kokoro-v1.0.onnx": 300_000_000, "voices-v1.0.bin": 20_000_000}


def model_dir():
    home = Path(__import__("os").environ.get("STICKMAN_HOME", str(Path.home() / ".stickman-director")))
    d = home / "kokoro"
    d.mkdir(parents=True, exist_ok=True)
    return d


def ensure_models():
    d = model_dir()
    for name, url in FILES.items():
        p = d / name
        if p.exists() and p.stat().st_size >= MIN_SIZE[name]:
            continue
        print(f"downloading {name} (once, ~{MIN_SIZE[name] // 1_000_000} MB)...", flush=True)
        tmp = p.with_suffix(".part")
        urllib.request.urlretrieve(url, tmp)
        if tmp.stat().st_size < MIN_SIZE[name]:
            tmp.unlink(missing_ok=True)
            raise RuntimeError(f"download of {name} looks truncated")
        tmp.rename(p)
        print(f"  saved {p}", flush=True)
    return d


def trim(x, thr=0.008):
    """Cut leading/trailing silence so line windows are tight."""
    idx = np.where(np.abs(x) > thr)[0]
    if not len(idx):
        return x
    a = max(0, idx[0] - int(0.01 * SR))
    b = min(len(x), idx[-1] + int(0.03 * SR))
    return x[a:b]


def write_wav(path, y):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(y, -1.0, 1.0) * 32767.0).astype("<i2").tobytes())


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: python src/voice.py <project>")
    project = Path(sys.argv[1])
    script = load_json(project / "script.json")
    v = script["voice"]
    lines = script["lines"]

    try:
        from kokoro_onnx import Kokoro
    except ImportError:
        raise SystemExit(
            "kokoro-onnx is not installed. Run:\n"
            "    python -m pip install kokoro-onnx pillow numpy"
        )

    d = ensure_models()
    k = Kokoro(str(d / "kokoro-v1.0.onnx"), str(d / "voices-v1.0.bin"))

    speech = []
    for i, ln in enumerate(lines):
        samples, sr = k.create(ln["text"], voice=v["id"], speed=v["speed"], lang=v["lang"])
        if sr != SR:
            raise RuntimeError(f"unexpected sample rate {sr} from kokoro")
        x = trim(np.asarray(samples, dtype=np.float64))
        speech.append(x)
        print(f"  line {i:02d}  {len(x) / SR:5.2f}s  {ln['text'][:52]}", flush=True)

    speech_sum = sum(len(x) for x in speech) / SR
    lead, outro = float(v["lead"]), float(v["outro"])
    n_gaps = max(0, len(speech) - 1)
    if n_gaps:
        want = (float(v["gap_target"]) - lead - outro - speech_sum) / n_gaps
        gap = min(float(v["gap_max"]), max(float(v["gap_min"]), want))
    else:
        gap = 0.0

    parts = [np.zeros(int(lead * SR))]
    t = lead
    line_windows = []
    for i, x in enumerate(speech):
        start = t
        parts.append(x)
        t += len(x) / SR
        line_windows.append({"i": i, "text": lines[i]["text"],
                             "start": round(start, 4), "end": round(t, 4)})
        if i < n_gaps:
            parts.append(np.zeros(int(gap * SR)))
            t += gap
    parts.append(np.zeros(int(outro * SR)))
    t += outro

    y = np.concatenate(parts)
    y = y / (np.abs(y).max() + 1e-9) * 0.92
    write_wav(project / "build" / "raw.wav", y)

    dump_json(project / "build" / "lines.json", {
        "sr": SR,
        "duration": round(t, 4),
        "voice": v["id"],
        "speed": v["speed"],
        "lead": lead,
        "outro": outro,
        "gap": round(gap, 4),
        "speech_sum": round(speech_sum, 4),
        "lines": line_windows,
    })
    print(f"build/raw.wav  {t:.2f}s total (speech {speech_sum:.2f}s, gap {gap:.2f}s)", flush=True)


if __name__ == "__main__":
    main()
