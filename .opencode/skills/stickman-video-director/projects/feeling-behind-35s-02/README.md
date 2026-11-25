# feeling-behind-35s-02 — 35 s episode · Design 02

**Topic:** *Why does everyone else's life look effortless while yours feels behind?*
Dry, relatable stickman explainer in **Design 02 — "Neon-on-black sketch"**:
your feed scrolls past effortless wins → their highlight reel vs your raw
footage → the edit that deletes the panic → everyone behind the scenes is
guessing → stop refreshing, do the next small thing → effort nobody filmed,
keep going.

- **Length:** exactly 35.0 s · 1280×720 · 30 fps (1050 frames)
- **Narration:** 88 words, Kokoro-82M (`af_heart`) via `kokoro-onnx`
  — Apache-2.0, fully local, **no API key, no account, no paid service**
- **Captions:** phrase-level, burned in, timed from the real synthesized audio
  (sidecar `build/captions.srt` for QA), dark glass plate with a cyan hairline
- **Sound:** narration + 4 code-generated SFX (feed pop, reel whoosh,
  checkbox tick, closing chime)
- **Output:** `renders/feeling-behind-35s-02.mp4`

## Design 02 — Neon-on-black sketch

Palette lives in `src/common.py`; the look is built from the neon stroke
helpers in `src/scenes.py` (`nline`, `ncircle`, `nrrect`, `ntext`,
`motion_lines`, `scribble`, `xmark`, `checkmark`).

| token | colour | role |
|---|---|---|
| `BG_TOP` / `BG_BOT` | `#04060E → #0C1020` | black canvas + faint `GRID` |
| `CREAM` | `#EAF9FF` | figure strokes, core text |
| `CYAN` | `#00EBFF` | you, active state, ticks |
| `MAGENTA` | `#FF28C4` | everyone else's highlight reel |
| `NEON_RED` | `#FF2E40` | motion lines, X marks, alerts |
| `GREEN` / `WARM` | `#7EFF9E` / `#FFC440` | calm, horizon, sparkles |
| `PAPER` | `#101422` | dark card / panel fill |

Every stroke is drawn three times (wide low-alpha halo → mid halo → bright
core) plus a deterministic hand-drawn jitter, so lines look marker-sketched
and lit by neon rather than vector-clean. The AI animation prompts for the
style and for each of the six shots are at the top of `src/scenes.py`
(`DESIGN_PROMPT` / `SCENE_PROMPTS`).

### The six shots

| scene | lines | beat |
|---|---|---|
| `scroll` | 0 | feed cards pop in, then neon-red "3 STEPS BEHIND" |
| `reel` | 1 | their smooth reel vs your trip and scribble |
| `edit` | 2–3 | clips struck out, drafts into NEVER POSTED |
| `guess` | 4–5 | row of shrugs, timeline glitches smooth out |
| `next` | 6–7 | chapter writes itself, refresh X'd, one tick |
| `keep` | 8–9 | climb the line, camera X'd, KEEP GOING |

## Render

GitHub Actions (this is what the workflow expects):

| input | value |
|---|---|
| workflow | **Stickman Director** (`stickman-director.yml`) |
| `project` | `feeling-behind-35s-02` |

Artifact: **`feeling-behind-35s-02-mp4`** → `renders/feeling-behind-35s-02.mp4`.

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
src/common.py        design 02 palette/constants, easing, JSON I/O, fonts
src/stick.py         canvas, stickman rig, faces
src/scenes.py        design 02 prompts + the six scenes (beats on caption chunks)
build/  renders/     generated (gitignored)
```

Every visual beat is keyed to a caption chunk in `timeline.json`
(`beat(line, chunk)`), so picture changes land on the spoken words even if the
voice runs long/short: `plan.py` picks one uniform tempo factor and rescales
speech, gaps and captions together.

Cloned from `projects/2am-overthinking-35s/`; the narration, caption sync,
scene timing and SFX plumbing are unchanged — only the script, the palette and
the drawing changed.
