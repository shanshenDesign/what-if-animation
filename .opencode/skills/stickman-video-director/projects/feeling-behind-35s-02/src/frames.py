"""Render the episode frame by frame.

    python src/frames.py <project>                 -> build/frames/frame_%05d.png
    python src/frames.py <project> --only 1,6,12   -> preview/t_01.00.png (fast QA)

Pipeline per frame: active scene (with 0.3 s crossfade at each cut) ->
camera push-in/shake crop -> caption for the words being spoken -> global
fade in/out -> downscale from 2x (anti-aliased) -> PNG.
"""
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw

from common import SS, W, H, W2, H2, clamp, font, load_json
from scenes import SCENES
from stick import Ctx

XFADE = 0.30


def build_scenes(tl, script):
    scenes = []
    specs = script["scenes"]
    if len(specs) + 1 != len(tl["boundaries"]):
        raise SystemExit("scenes/boundaries mismatch in timeline.json")
    for k, spec in enumerate(specs):
        if spec["id"] not in SCENES:
            raise SystemExit(f"unknown scene id: {spec['id']}")
        sc = SCENES[spec["id"]](tl, script)
        sc.t0 = tl["boundaries"][k]
        sc.t1 = tl["boundaries"][k + 1]
        scenes.append(sc)
    return scenes


def scene_index(boundaries, t):
    for k in range(len(boundaries) - 1):
        if boundaries[k] <= t < boundaries[k + 1]:
            return k
    return len(boundaries) - 2


def render_scene(sc, lt):
    layer = sc.bg.copy()
    sc.draw(Ctx(layer), lt)
    z = sc.zoom(lt)
    dx, dy = sc.shake(lt)
    if z != 1.0 or dx or dy:
        cw, ch = W2 / z, H2 / z
        left = (W2 - cw) / 2 + dx * SS
        top = (H2 - ch) / 2 + dy * SS
        box = (round(left), round(top), round(left + cw), round(top + ch))
        layer = layer.crop(box).resize((W2, H2), Image.BILINEAR)
    return layer


def find_chunk(tl, t):
    for ln in tl["lines"]:
        if ln["start"] <= t < ln["end"]:
            for cap in ln["caps"]:
                if cap["start"] <= t < cap["end"]:
                    return cap
    return None


def draw_caption(layer, chunk):
    """Design 02 caption: dark glass plate, cyan hairline, crisp white text."""
    ctx = Ctx(layer)
    size, pad_x, pad_y = 40, 26, 16
    probe = ctx.d.textbbox((0, 0), chunk["text"], font=font(size, True), anchor="mm")
    x0, y0, x1, y1 = [v / SS for v in probe]
    cx = W / 2.0
    cy = H - 34 - pad_y - y1
    ctx.rrect([cx + x0 - pad_x, cy + y0 - pad_y,
               cx + x1 + pad_x, cy + y1 + pad_y], 16, fill=(2, 4, 10, 200),
              outline=(0, 235, 255, 130), w=2)
    ctx.text((cx + 2, cy + 3), chunk["text"], size=size, fill=(0, 0, 0, 175),
             anchor="mm")
    ctx.text((cx, cy), chunk["text"], size=size, fill=(255, 255, 255), anchor="mm")


def apply_fade(layer, t, duration):
    a = 0.0
    if t < 0.35:
        a = 1 - t / 0.35
    elif t > duration - 0.5:
        a = clamp((t - (duration - 0.5)) / 0.5)
    if a > 0.01:
        ImageDraw.Draw(layer, "RGBA").rectangle(
            [0, 0, W2, H2], fill=(0, 0, 0, int(255 * a)))


def composite(scenes, tl, t):
    bounds = tl["boundaries"]
    layer = None
    for j in range(1, len(bounds) - 1):
        b = bounds[j]
        if b - XFADE / 2 <= t < b + XFADE / 2:
            f = clamp((t - (b - XFADE / 2)) / XFADE)
            layer = Image.blend(render_scene(scenes[j - 1], t - bounds[j - 1]),
                                render_scene(scenes[j], t - bounds[j]), f)
            break
    if layer is None:
        k = scene_index(bounds, t)
        layer = render_scene(scenes[k], t - bounds[k])
    chunk = find_chunk(tl, t)
    if chunk:
        draw_caption(layer, chunk)
    apply_fade(layer, t, tl["duration"])
    return layer.resize((W, H), Image.LANCZOS)


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: python src/frames.py <project> [--only t1,t2,...] [--out DIR]")
    project = Path(sys.argv[1])
    only, out = None, project / "build" / "frames"
    if "--only" in sys.argv:
        i = sys.argv.index("--only")
        only = [float(x) for x in sys.argv[i + 1].split(",")]
        out = project / "preview"
    if "--out" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--out") + 1])

    tl = load_json(project / "build" / "timeline.json")
    script = load_json(project / "script.json")
    if tl.get("size") != [W, H]:
        raise SystemExit(f"script size {tl.get('size')} != {W}x{H} design space")
    scenes = build_scenes(tl, script)
    out.mkdir(parents=True, exist_ok=True)

    if only:
        for t in only:
            img = composite(scenes, tl, t)
            name = out / f"t_{t:06.2f}.png"
            img.save(name)
            print(f"preview {name}  caption={bool(find_chunk(tl, t))}")
        return

    fps = tl["fps"]
    total = int(round(tl["duration"] * fps))
    started = time.time()
    for f in range(total):
        img = composite(scenes, tl, f / fps)
        img.save(out / f"frame_{f:05d}.png")
        if f % 150 == 0:
            print(f"  frame {f}/{total}  ({time.time() - started:.0f}s)", flush=True)
    print(f"{total} frames -> {out} in {time.time() - started:.0f}s", flush=True)


if __name__ == "__main__":
    main()
