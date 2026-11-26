# forgotten-key-on-the-counter — 40 s episode · Cinematic Neon

**Topic:** *You get home late, the front door is locked, and the key is on
the kitchen counter — behind the glass, out of reach.*

A locked-door night run in six beats: a heavy latch that will not turn, a
pocket that comes back empty, and one brass key glinting far inside the dark
house. Sharp black silhouettes edged in **cyan / magenta / amber** rim light
slip through a pitch-dark hallway, freeze on a creaking floorboard, get
blinded by cyan-and-magenta street neon in the glass door, then crouch-sprint
past table and chair silhouettes to the counter — snatch, slide back, one
clean click, and step through.

- **Length:** exactly 40.0 s · 1280×720 · 30 fps (1200 frames)
- **Narration:** 113 words, Kokoro-82M (`af_heart`) via `kokoro-onnx`
  — Apache-2.0, fully local, **no API key, no account, no paid service**
- **Captions:** phrase-level, burned in, timed from the real synthesized audio
  (sidecar `build/captions.srt` for QA)
- **Sound:** narration + 17 code-generated SFX (latch click, pocket pat,
  floorboard creak, neon hum, hushed footstep, key jingle, clean unlock, …)
- **Output:** `renders/forgotten-key-on-the-counter.mp4`

## Obstacle flow

| scene | line(s) | beat |
|---|---|---|
| `door_lock_panic` | 0–1 | hook — latch clicks, every pocket patted, the distant glint behind glass |
| `hallway_shadow` | 2 | slip into the dark hallway, deep shadows stretching across the walls |
| `floorboard_creak` | 3 | one sharp creak freezes the figure mid-step, then listening |
| `window_neon_glare` | 4 | cyan + magenta street neon slices the room, blinds the reflection |
| `counter_dash` | 5 | crouch-sprint past table/chair silhouettes to the counter edge |
| `key_grab_unlock` | 6–8 | snatch the key, slide back, turn the cylinder, one clean click, step through |

Every visual beat is keyed to a caption chunk (`beat(line, chunk)`), so
picture changes land on the spoken words even if the voice runs long or
short: `plan.py` picks one uniform tempo factor and rescales speech, gaps and
captions together.

## Render

GitHub Actions (this is what the workflow expects):

| input | value |
|---|---|
| workflow | **Stickman Director** (`stickman-director.yml`) |
| `project` | `forgotten-key-on-the-counter` |

Artifact: **`forgotten-key-on-the-counter-mp4`** → `renders/forgotten-key-on-the-counter.mp4`.

CLI / ubuntu-latest:

```bash
bash render.sh          # deps -> TTS -> timeline -> frames -> audio -> mp4
python3 src/frames.py . --only 3,12,16,21,26,36   # one still per scene (no encode)
```

Requires only `python3` + `ffmpeg` (the workflow installs ffmpeg; `render.sh`
pip-installs `pillow numpy kokoro-onnx` if missing and downloads the Kokoro
model files once into `~/.stickman-director/kokoro`, cache-friendly).

> **Android / no-render rule:** on a phone, run only the lightweight checks —
> `python3 -m py_compile src/*.py`, `python3 -m json.tool script.json`,
> `bash -n render.sh`, plus a single-digit `--only` preview. Never run the
> full frame loop, Kokoro synthesis or ffmpeg encoding locally, and never
> commit `.mp4`, `.wav` or `build/frames/*`.

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
src/scenes.py        the six scenes + rim-lit silhouette / key / lock HUD
build/  renders/     generated (gitignored)
```

## Look

Design 04 — *cinematic neon silhouettes*: each figure is drawn as a black
body pass over two offset colour passes, so only a crescent of rim survives
(leading edge cyan, trailing edge magenta or amber). Neon sources — the
street outside, the sign through the glass, the lock cylinder, the brass key
— each get a halo pass, and the camera pushes, tracks and shakes per beat
(`zoom_range` / `shake()` on every scene, clamped to the crop slack by
`safe_shake` so a micro-shake can never pull black edges into frame).
