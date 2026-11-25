# what-if-pause-35s — 35 s episode · Design 02

**Topic:** *What if you could pause time for 10 seconds whenever you mess up?*

A dry stickman short in **Design 02 — “Neon-on-black sketch, detailed rooms”**:
you fumble a coffee, freeze the world, strike a flawless pose, quietly repair a
wrong meeting and a bad haircut, then let time resume just before the cup lands.
The security camera in the corner, naturally, never freezes.

- **Length:** exactly 35.0 s · 1280×720 · 30 fps (1050 frames)
- **Narration:** 87 words, Kokoro (`af_heart`) through `kokoro-onnx` — local,
  Apache-2.0, no API key and no paid service
- **Captions:** phrase-level, burned in and timed from the synthesized audio;
  sidecar `build/captions.srt` for QA
- **Sound:** narration plus 12 procedural SFX cues (`freeze`, `tick`, `splash`,
  `record`, `pop`, `whoosh`, `thud`, `chime`) generated in `src/audio.py`
- **Output:** `renders/what-if-pause-35s.mp4`

## Freeze language

The episode adds a reusable freeze kit on top of the original neon helpers:

| helper | role |
|---|---|
| `pause_badge` | 10.0 → 0.0 countdown ring, pause glyph and `TIME PAUSED / RESUMED` |
| `frozen_clock` | maps the story’s ten seconds onto the freeze window |
| `freeze_ripple` / `freeze_frame` | snap-in ripple and frosted edge shards |
| `hanging_splash` / `coffee_puddle` | suspended coffee and the eventual landing |
| `wall_clock` | a clock that stops, clicks and starts again |

The rooms are baked once per scene in `cafe_bg`, `conference_panel`,
`barber_panel` and `party_bg`: brickwork, night-city windows, pendant lamps,
shelves, a menu board, an espresso machine, a barber chair, a CCTV monitor and
a staff-party table. Figures stay bright cyan/cream with a dark separation
stroke so they remain readable against all that detail.

## The five shots

| scene | lines | beat |
|---|---|---|
| `spill` | 0–1 | cup slips, coffee hangs, 10-second ring snaps in |
| `pose` | 2–3 | ignore the mess, chin up, hand on counter, `FLAWLESS` |
| `fixes` | 4–6 | wrong meeting → cat slide; bad haircut → backwards exit; 10 s strip |
| `resume` | 7–8 | clock clicks, frost breaks, coffee lands, nobody saw |
| `camera` | 9–11 | CCTV replays everything at 1.0× for the staff party |

## Render

GitHub Actions — **Stickman Director** (`stickman-director.yml`):

| input | value |
|---|---|
| `project` | `what-if-pause-35s` |

Artifact: **`what-if-pause-35s-mp4`** → `renders/what-if-pause-35s.mp4`.

CLI / ubuntu-latest:

```bash
bash render.sh
python3 src/frames.py . --only 1,6,12,18,25,31   # quick still-frame QA
```

Requires only `python3` + `ffmpeg`. `render.sh` pip-installs
`pillow numpy kokoro-onnx` if missing and caches the Kokoro model files in
`~/.stickman-director/kokoro`.

## Layout

```
render.sh            entry point (workflow runs this first)
script.json          narration, caption chunks, scene map, voice, SFX cues
src/voice.py         Kokoro TTS -> build/raw.wav + build/lines.json
src/plan.py          tempo fit, caption windows, scene cuts -> build/timeline.json
src/frames.py        Pillow renderer (2x supersampled) -> build/frames/*.png
src/audio.py         atempo fit + procedural SFX -> build/mix.wav (35.0 s)
src/common.py        palette, easing, colour/freeze helpers, JSON I/O, fonts
src/stick.py         canvas, stickman rig, faces
src/scenes.py        detailed rooms, freeze kit, poses and the five scenes
build/  renders/     generated (gitignored)
```

Every visual beat is keyed to a caption chunk in `timeline.json`
(`beat(line, chunk)`), so picture changes land on the words even when the voice
runs long or short: `plan.py` applies one tempo factor and rescales speech, gaps
and captions together.
