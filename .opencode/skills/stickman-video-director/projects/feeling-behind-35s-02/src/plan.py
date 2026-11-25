"""Turn raw line timings into the final 35 s timeline.

    python src/plan.py <project>

Reads script.json + build/lines.json, writes:
    build/timeline.json   tempo, scene boundaries, per-line and per-caption
                          windows (already rescaled to final video time),
                          resolved SFX cue times
    build/captions.srt    the same caption windows as a sidecar subtitle file

If the raw track is longer than the target, everything (speech + gaps) is
compressed by one uniform tempo factor and every window is divided by that
factor, so picture and audio stay perfectly aligned.
"""
import sys
from pathlib import Path

from common import dump_json, load_json

XFADE = 0.30   # scene crossfade, seconds
MARGIN = 0.10  # keep this much headroom under the target length


def words(s):
    return max(1, len(s.split()))


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: python src/plan.py <project>")
    project = Path(sys.argv[1])
    script = load_json(project / "script.json")
    raw = load_json(project / "build" / "lines.json")

    duration = float(script.get("duration", 35))
    target = duration - MARGIN

    tempo = max(1.0, raw["duration"] / target)
    tempo = round(tempo, 4)
    scale = 1.0 / tempo
    if tempo > 1.0:
        print(f"raw track {raw['duration']:.2f}s > {target:.2f}s -> atempo x{tempo}")

    # ---- line + caption windows in final video time
    out_lines = []
    for rl in raw["lines"]:
        i = rl["i"]
        spec = script["lines"][i]
        start, end = rl["start"] * scale, rl["end"] * scale
        caps = spec.get("caps") or [spec["text"]]
        weights = [words(c) for c in caps]
        total = sum(weights)
        cursor = start
        cap_out = []
        for c, w in zip(caps, weights):
            span = (end - start) * w / total
            cap_out.append({"text": c,
                            "start": round(cursor, 3),
                            "end": round(cursor + span, 3)})
            cursor += span
        out_lines.append({"i": i, "text": spec["text"],
                          "start": round(start, 3), "end": round(end, 3),
                          "caps": cap_out})

    def line(i):
        return out_lines[i]

    # ---- scene boundaries: midpoint of the silent gap between scene groups
    scenes = script["scenes"]
    boundaries = [0.0]
    for k in range(1, len(scenes)):
        prev_end = line(scenes[k - 1]["to"])["end"]
        next_start = line(scenes[k]["from"])["start"]
        boundaries.append(round((prev_end + next_start) / 2, 3))
    boundaries.append(duration)
    for k in range(1, len(scenes)):
        boundaries[k] = min(max(boundaries[k], boundaries[k - 1] + 1.0),
                            boundaries[k + 1] - 1.0)

    # ---- SFX cue times (absolute)
    sfx = []
    for cue in script.get("sfx", []):
        ln = out_lines[cue["line"]]
        caps = ln["caps"]
        j = min(cue.get("chunk", 0), len(caps) - 1)
        t = caps[j]["start"] + float(cue.get("offset", 0.0))
        t = min(t, duration - 1.7)  # keep long cues (chime) inside the video
        sfx.append({"kind": cue["kind"], "t": round(t, 3)})

    timeline = {
        "duration": duration,
        "fps": int(script.get("fps", 30)),
        "size": script.get("size", [1280, 720]),
        "tempo": tempo,
        "boundaries": boundaries,
        "scenes": [{"id": s["id"], "from": s["from"], "to": s["to"]} for s in scenes],
        "lines": out_lines,
        "sfx": sfx,
        "words": sum(words(l["text"]) for l in script["lines"]),
        "voice": raw.get("voice"),
    }
    dump_json(project / "build" / "timeline.json", timeline)

    # ---- sidecar subtitles (QA / re-use)
    srt = []
    n = 1
    for ln in out_lines:
        for cap in ln["caps"]:
            srt.append(f"{n}\n{srt_ts(cap['start'])} --> {srt_ts(cap['end'])}\n{cap['text']}\n")
            n += 1
    (project / "build").mkdir(parents=True, exist_ok=True)
    (project / "build" / "captions.srt").write_text("\n".join(srt), encoding="utf-8")

    print(f"timeline: {len(out_lines)} lines, {timeline['words']} words, "
          f"boundaries {boundaries}, tempo x{tempo}")
    if not 85 <= timeline["words"] <= 95:
        print(f"WARNING: word count {timeline['words']} outside 85-95 target")


def srt_ts(t):
    ms = int(round(t * 1000))
    h, rem = divmod(ms, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


if __name__ == "__main__":
    main()
