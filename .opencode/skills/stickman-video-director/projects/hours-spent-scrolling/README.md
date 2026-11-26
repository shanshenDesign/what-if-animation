# hours-spent-scrolling — 40 s episode · Screen-lit Silhouette

**Topic:** *A girl behind the glass of your screen breaks the fourth wall,
counts the hours you have spent scrolling, and reaches for the switch.*

A scroll-awareness callout in six beats: knuckles tapping on the glass
right in front of you, a thumb that keeps the feed's rhythm on its own,
tall amber `1H / 3H / 5H+` counters stacking up behind her, the room
sinking to midnight while the cyan monitor light stays stuck on her face,
one quiet beat where the cards freeze and she asks what you actually
remember — then a hand reaching for the amber switch and one clean swipe.

- **Length:** exactly 40.0 s · 1280×720 · 30 fps (1200 frames)
- **Narration:** 93 words, Kokoro-82M (`af_bella`) via `kokoro-onnx`
  — Apache-2.0, fully local, **no API key, no account, no paid service**
- **Captions:** phrase-level, burned in, timed from the real synthesized audio
  (sidecar `build/captions.srt` for QA)
- **Sound:** narration + 16 code-generated SFX (glass tap ×3, swipe whoosh ×4,
  digital clock tick ×3, room hum ×3, freeze chime ×2, power-off click)
- **Output:** `renders/hours-spent-scrolling.mp4`

## Beat flow

| scene | line(s) | beat |
|---|---|---|
| `glass_tap_hook` | 0–1 | close-up behind the cyan screen frame — knocks on the glass, tilts her head, calls you out |
| `thumb_loop_mirror` | 2 | medium shot, translucent cards drift and jump on every swipe, her thumb keeps the rhythm |
| `clock_numbers_drop` | 3 | amber `1H` / `3H` / `5H+` counters drop in and stack behind her, brows lift in deadpan disbelief |
| `room_fade_shadow` | 4 | slow push-in, the room drops to midnight shadow, cyan/magenta rim left on her face and hair |
| `pause_quiet_beat` | 5 | cards freeze and dim, intimate framing, she asks what you remember from the last hour |
| `screen_off_choice` | 6–8 | shrug, reach, swipe the amber switch off — clean amber-and-cyan closing frame |

Every visual beat is keyed to a caption chunk (`beat(line, chunk)`), so
picture changes land on the spoken words even if the voice runs long or
short: `plan.py` picks one uniform tempo factor and rescales speech, gaps and
captions together. The face rides the same timeline — `talk()` turns the
active caption into a mouth shape + openness, `blink_closed()` keeps the
eyes alive, and the brows move through curious / skeptical / deadpan /
empathetic per beat.

## Render

GitHub Actions (this is what the workflow expects):

| input | value |
|---|---|
| workflow | **Stickman Director** (`stickman-director.yml`) |
| `project` | `hours-spent-scrolling` |

Artifact: **`hours-spent-scrolling-mp4`** → `renders/hours-spent-scrolling.mp4`.

CLI / ubuntu-latest:

```bash
bash render.sh          # deps -> TTS -> timeline -> frames -> audio -> mp4
python3 src/frames.py . --only 2,9,15,21,27,34   # one still per scene (no encode)
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
src/common.py        screen-lit palette, easing, colour helpers, JSON I/O, fonts
src/stick.py         canvas, female rig (ponytail + face), blink / brows / mouth
src/scenes.py        the six scenes + scroll-time HUD, cards, counters, switch
build/  renders/     generated (gitignored)
```

## Look

Design 07 — *screen-lit silhouettes*: each figure is drawn as a black
body pass over two offset colour passes, so only a crescent of rim survives
(leading edge cyan, trailing edge magenta or amber) — hair cap, side lock
and ponytail included, with the tail lagging every head move. Neon sources —
the screen frame, the drifting cards, the hour counters, the amber switch —
each get a halo pass, and the camera pushes, tracks and shakes per beat
(`zoom_range` / `shake()` on every scene, clamped to the crop slack by
`safe_shake` so a micro-shake can never pull black edges into frame). The
`SCROLL TIME` HUD runs 4H00M → 6H00M across the 40 s and inverts the camera
transform so it stays pinned to the frame.
