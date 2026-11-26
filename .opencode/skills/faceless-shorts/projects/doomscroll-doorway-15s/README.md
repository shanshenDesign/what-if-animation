# doomscroll-doorway-15s — "Just two minutes… and the wall opens a door"

A ready-to-render `tall-tale` faceless short: 12 shots in 3 beats, 36 spoken words, exactly 15.0 s,
voice `am_michael` ×1.05, procedural `bounce` music bed + whoosh/sparkle/ding/zip/slam SFX.

**Story** — Beat 1 (0–4.2 s): a kid sits on the edge of the bed scrolling, "just two minutes,"
then taps one more video. Beat 2 (4.2–11 s): a seam of light splits the wallpaper, the wall swings
open like a door, he steps through into a sunset world where a giant clock makes a minute last an
hour. Beat 3 (11–15 s): he snaps back on the bed, watches the wall clock rip from 10:00 to 10:30 —
thirty minutes gone.

Nothing heavy runs on your phone — everything (TTS → alignment → frames → mix) happens
in GitHub Actions via `.github/workflows/faceless-shorts.yml`.

## Render

- Actions → **Faceless Short (stick-story)** → *Run workflow* (`topic` = `doomscroll-doorway-15s`,
  `length` = `15`).
- Pipeline on `ubuntu-latest`: `voice.py` (Kokoro TTS) → `words.py` (Whisper word alignment)
  → `capture.mjs check` → `capture.mjs cues` → `capture.mjs sheet` → `mix.py`
  → `capture.mjs video` → artifact `doomscroll-doorway-15s-mp4` = `renders/doomscroll-doorway-15s.mp4`
  (1080×1920, 30 fps, with audio).

## Files

| file | role |
|---|---|
| `script.json` | narration (5 lines, 36 words), caption chunks (`*` = the gold word), `speed` 1.05 / `outro` 0.565 → 15.00 s |
| `src/shots.js` | 12 shots across the 3 beats + sound cues: bedroom sets (bed, phone prop, wall-panel door, wall clock), other world (sunset meadow, giant clock, floating clocks, the doorway in the grass) |
| `src/main.js` | boot + `draw(t)` (pure function of t), shot cut lookup, fades, captions |
| `src/core/*` | shared engine: Three.js sets, Toon cut-outs, timing (`L/Le/Wd`), captions (1-word, y 1340, safe margins) |
| `vendor/` | pinned three.js module + postprocessing addons (import map in `index.html`) |
| `tools/capture.mjs` | headless-Chrome `check · cues · sheet · frames · video · preview` (needs Chrome; runs in CI) |
| `tools/mix.py` | narration + ducked `bounce` bed + SFX → `data/mix.wav` |

`data/*` is intentionally **not** committed: CI regenerates `lines.json`, `words.json`, `cues.json`
and `mix.wav` from the current script, so timings always match the narration.

## Timing check (no TTS needed)

```
python3 ../../scripts/estimate.py .
# → estimated timing: 5 lines, 36 words, 15.00 s
```
