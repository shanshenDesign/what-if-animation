# 2am-overthinking-35s — 35 s test episode

**Topic:** *Why does your brain suddenly remember every awkward moment at 2 AM?*
Warm, relatable stickman explainer: night bedroom → the 2 AM wave-memory →
the prefrontal-cortex bouncer clocks out → the brain on stage with a megaphone
stamping `URGENT` → breathe, name it, let it pass → morning.

- **Length:** exactly 35.0 s · 1280×720 · 30 fps (1050 frames)
- **Narration:** 91 words, Kokoro-82M (`af_heart`) via `kokoro-onnx`
  — Apache-2.0, fully local, **no API key, no account, no paid service**
- **Captions:** phrase-level, burned in, timed from the real synthesized audio
  (sidecar `build/captions.srt` for QA)
- **Sound:** narration + 4 code-generated SFX (bubble pop, memory whoosh,
  stamp thud, dawn chime)
- **Output:** `renders/2am-overthinking-35s.mp4`

## Render

GitHub Actions (this is what the workflow expects):

| input | value |
|---|---|
| workflow | **Stickman Director** (`stickman-director.yml`) |
| `project` | `2am-overthinking-35s` |

Artifact: **`2am-overthinking-35s-mp4`** → `renders/2am-overthinking-35s.mp4`.

CLI / ubuntu-latest:

```bash
bash render.sh          # deps -> TTS -> timeline -> frames -> audio -> mp4
python3 src/frames.py . --only 1,6,12,18,25,31   # quick still-frame QA (no encode)
```

Requires only `python3` + `ffmpeg` (the workflow installs ffmpeg; `render.sh`
pip-installs `pillow numpy kokoro-onnx` if missing and downloads the Kokoro
model files once into `~/.stickman-director/kokoro`, cache-friendly).

## Layout

```
render.sh            entry point (workflow runs this first)
script.json          narration lines, caption chunks, scene map, voice, sfx cues
src/voice.py         Kokoro TTS  -> build/raw.wav + build/lines.json
src/plan.py          tempo fit, caption windows, scene cuts -> build/timeline.json
src/frames.py        Pillow renderer (2x supersampled) -> build/frames/*.png
src/audio.py         atempo fit + procedural sfx -> build/mix.wav (35.0 s)
src/stick.py         canvas, stickman rig, faces
src/scenes.py        the six scenes (beats anchored to caption chunks)
build/  renders/     generated (gitignored)
```

Every visual beat is keyed to a caption chunk in `timeline.json`
(`beat(line, chunk)`), so picture changes land on the spoken words even if the
voice runs long/short: `plan.py` picks one uniform tempo factor and rescales
speech, gaps and captions together.

Kokoro model files come from the `thewh1teagle/kokoro-onnx` release
(`kokoro-v1.0.onnx` + `voices-v1.0.bin`); line-window technique follows the
sibling `faceless-shorts` voice script. Nothing here calls the network except
that one-time model download.
