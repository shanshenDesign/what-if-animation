# gravity-35s — "What if gravity turned off for 35 seconds?"

A ready-to-render `stick-story` faceless short: 7 shots, 91 spoken words, ~35 s,
voice `am_michael`, procedural music bed + whoosh/rumble/crash/alarm SFX.

Nothing heavy runs on your phone — everything (TTS → alignment → frames → mix) happens
in GitHub Actions via `.github/workflows/faceless-shorts.yml`.

## Render

- Actions → **Faceless Short (stick-story)** → *Run workflow* (`topic` = `gravity-35s`),
  or just push a change under `projects/` — the workflow picks the first project folder.
- Pipeline on `ubuntu-latest`: `voice.py` (Kokoro TTS) → `words.py` (Whisper word alignment)
  → `capture.mjs check` → `capture.mjs cues` → `mix.py` → `capture.mjs video` → artifact
  `gravity-35s-mp4` = `renders/gravity-35s.mp4` (1080×1920, 30 fps, with audio).

## Files

| file | role |
|---|---|
| `script.json` | narration, caption chunks (`*` = the gold word), `speed` 1.1 / `gap` 0.35 → 34.6 s |
| `src/shots.js` | 8 shots (hook, lift-off, 3 gold step cards, floating objects, snap-back crash, end card) + sound cues |
| `src/main.js` | boot + `draw(t)`, camera punch/drift, the pale "float" wash that dies on the word *snaps* |
| `src/core/*` | shared drawing kit, timing (`L/Le/Wd`), captions |
| `tools/capture.mjs` | headless-Chrome `check · cues · sheet · frames · video · preview` |
| `tools/mix.py` | narration + ducked bed + SFX (incl. custom `rumble` and `crash`) → `data/mix.wav` |

`data/*` is intentionally **not** committed: CI regenerates `lines.json`, `words.json`,
`cues.json` and `mix.wav` from the current script, so timings always match the narration.

## Timing check (no TTS needed)

```
python3 ../../scripts/estimate.py .
# → estimated timing: 7 lines, 91 words, 34.62 s
```
