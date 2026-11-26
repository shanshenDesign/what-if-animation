# scifi-toon-10s — 10 s trial · Sci-Fi Toon

**Topic:** *What if a glowing probability meter popped up every time you hesitated?*

A tight two-scene trial in the **Sci-Fi Toon** style (thick toon linework, flat
colour, a near-black corridor and glowing cyan/magenta HUD panels): the hero
hovers at a glowing doorway, a probability meter pops in and climbs, then the
number crashes to four percent and the mission aborts in red alert.

- **Length:** exactly 10.0 s · 1280×720 · 30 fps
- **Narration:** Kokoro (`af_heart`) through `kokoro-onnx` — local, no API key
- **Captions:** phrase-level, burned in and timed from the synthesized audio
- **Output:** `renders/scifi-toon-10s.mp4`

## The two shots

| scene | line | beat |
|---|---|---|
| `hesitate` | 0 | hero dithers at the portal; `PROBABILITY` HUD pops in and climbs |
| `abort` | 1 | meter crashes to 4 %, red alert, `ABORT MISSION`, hero recoils |

## Style

Adapted from `styles/scifi-toon/` (fetched from `shanshenDesign/lemo-opuscar`):
flat colour bands, near-black toon ink lines, a glowing doorway, and chunky
angle-bracketed HUD panels in cyan (calm) and red (alert). The characters stay
bright cyan with a dark separation stroke so they read over the detailed room.

## Render

```bash
bash render.sh
python3 src/frames.py . --only 2.6,6.6   # quick still-frame QA
```

Requires only `python3` + `ffmpeg`. `render.sh` pip-installs
`pillow numpy kokoro-onnx` if missing.

## Layout

```
render.sh            entry point
script.json          narration, caption chunks, scene map, voice, SFX cues
src/voice.py         Kokoro TTS -> build/raw.wav + build/lines.json
src/plan.py          tempo fit, caption windows, scene cuts -> build/timeline.json
src/frames.py        Pillow renderer (2x supersampled) -> build/frames/*.png
src/audio.py         atempo fit + procedural SFX -> build/mix.wav
src/common.py        palette, easing, colour helpers, JSON I/O, fonts
src/stick.py         canvas, stickman rig, faces
src/scenes.py        sci-fi room, HUD meter and the two scenes
preview_frame.png    single trial still (hesitation beat, 68 %)
build/  renders/     generated (gitignored)
```
