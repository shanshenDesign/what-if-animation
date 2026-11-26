# last-charge-1-percent — 40 s episode · Cinematic Neon

**Topic:** *What if your phone died at 1% with one urgent message left to send?*

A neon night-run in six beats: one message that has to go out, a battery
stuck at **1 %**, and a screen that is already dimming. Sharp black
silhouettes edged in **cyan / magenta / amber** rim light run past a glowing
neon streetlamp, a convenience-store window, a dark hallway with a creaking
doorway, a puddle that throws the neon sign back at your face — then the
final dive to the outlet as the battery icon flashes red.

- **Length:** exactly 40.0 s · 1280×720 · 30 fps (1200 frames)
- **Narration:** 105 words, Kokoro-82M (`af_heart`) via `kokoro-onnx`
  — Apache-2.0, fully local, **no API key, no account, no paid service**
- **Captions:** phrase-level, burned in, timed from the real synthesized audio
  (sidecar `build/captions.srt` for QA)
- **Sound:** narration + 12 code-generated SFX (battery drain, streetlamp buzz,
  door creak, puddle ripple, charger click, …)
- **Output:** `renders/last-charge-1-percent.mp4`

## Obstacle flow

| scene | line(s) | beat |
|---|---|---|
| `hook_1pct` | 0 | hook — close-up phone, `1 %`, one message typed, screen dimming |
| `street_glare` | 1 | obstacle 1 — neon streetlamp + `NEON MART` window glare whites out the glass |
| `hallway_creak` | 2–3 | obstacle 2 — dark corridor, the door creaks open at the house corner |
| `puddle_neon` | 4–5 | obstacle 3 — a puddle throws the neon sign back; snatch, battery turns red |
| `outlet_run` | 6 | three steps to the glowing outlet, charger still on the floor |
| `outlet_reach` | 7–8 | dive, screen dies mid-air, plug — 1 % comes back, `MESSAGE SENT` |

Every visual beat is keyed to a caption chunk (`beat(line, chunk)`), so
picture changes land on the spoken words even if the voice runs long or
short: `plan.py` picks one uniform tempo factor and rescales speech, gaps and
captions together.

## Render

GitHub Actions (this is what the workflow expects):

| input | value |
|---|---|
| workflow | **Stickman Director** (`stickman-director.yml`) |
| `project` | `last-charge-1-percent` |

Artifact: **`last-charge-1-percent-mp4`** → `renders/last-charge-1-percent.mp4`.

CLI / ubuntu-latest:

```bash
bash render.sh          # deps -> TTS -> timeline -> frames -> audio -> mp4
python3 src/frames.py . --only 3,12,20,27,33,38   # quick still-frame QA (no encode)
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
src/audio.py         atempo fit + procedural sfx -> build/mix.wav (40.0 s)
src/common.py        neon palette, easing, colour helpers, JSON I/O, fonts
src/stick.py         canvas, stickman rig, faces, walk cycle
src/scenes.py        the six scenes + rim-lit silhouette / phone / battery HUD
build/  renders/     generated (gitignored)
```

## Look

Design 03 — *cinematic neon silhouettes*: each figure is drawn as a black
body pass over two offset colour passes, so only a crescent of rim survives
(leading edge cyan, trailing edge magenta or amber). Neon sources — streetlamp,
`NEON MART` sign, outlet, charger LED — each get a halo pass, and the camera
pushes, tracks and shakes per beat (`zoom_range` / `shake()` on every scene).
