# locked-doors-45s — "What if every door on Earth locked itself for 1 hour?"

A ready-to-render `stick-story` faceless short: 12 shots, 112 spoken words, ~45 s,
voice `am_michael`, procedural music bed + tock/thud/sizzle/rumble/alarm/sparkle/boing/slam SFX.

One street, one hero, all video: every door clicks shut at once (gold padlocks pop),
lifts freeze between floors, shoppers are on the wrong side of the glass, a kettle
simmers behind the kitchen door, drivers wait beside idling vans, the sixty-minute
countdown ticks down — then at 1:00 every lock opens together except one stuck
bathroom latch.

Nothing heavy runs on your phone — everything (TTS → alignment → frames → mix) happens
in GitHub Actions via `.github/workflows/faceless-shorts.yml`.

## Render

- Actions → **Faceless Short (stick-story)** → *Run workflow* (`topic` = `locked-doors-45s`,
  `length` = `45`, the workflow defaults), or push a change under `projects/` — with no
  topic given the workflow falls back to the first project folder that exists in `projects/`.
- Pipeline on `ubuntu-latest`: `voice.py` (Kokoro TTS) → `words.py` (Whisper word alignment)
  → `capture.mjs check` → `capture.mjs cues` → `mix.py` → `capture.mjs video` → artifact
  `locked-doors-45s-mp4` = `renders/locked-doors-45s.mp4` (1080×1920, 30 fps, with audio).

## Files

| file | role |
|---|---|
| `script.json` | narration, caption chunks (`*` = the gold word), `speed` 1.1, per-line `gap` 0.45 → 0.35, lead 0.45 / outro 3.6 → 45.0 s |
| `src/shots.js` | the street set (sky, buildings, shop doors, sidewalk, curb, road) + 12 shots and their sound cues |
| `src/main.js` | boot + `draw(t)`, camera punch/drift, eight light washes (steel, kettle, diesel, red, dusk, gold) + word-timed shakes |
| `src/sheet.js` | style sheet `LOCKED DOORS: 45S` drawn with the style's own kit |
| `src/core/*` | shared drawing kit, timing (`L/Le/Wd`), captions |
| `tools/capture.mjs` | headless-Chrome `check · cues · sheet · frames · video · preview` |
| `tools/mix.py` | narration + ducked bed + SFX (incl. `alarm` and `sizzle`) → `data/mix.wav` |

`data/*` is intentionally **not** committed: CI regenerates `lines.json`, `words.json`,
`cues.json` and `mix.wav` from the current script, so timings always match the narration.
For a local preview run `python3 ../../scripts/estimate.py .` first (it writes
`data/lines.json` + `data/words.json`), then open `index.html`.

## Beats

| t | line | picture | cues |
|---|---|---|---|
| 0.0–4.9 | You step outside, and every door on Earth clicks shut at once. | street, hero strides out, doors slam + gold padlocks pop, `DOORS: LOCKED` | `whoosh`, `tock` @clicks, `thud` @once |
| 4.9–8.6 | Elevators freeze right between floors with both doors sealed shut. | shaft cutaway, car jolts between floors, doors slide shut, `BETWEEN FLOORS` | `whoosh`, `thud` @freeze, `tock` @sealed |
| 8.6–13.2 | Shoppers and commuters end up standing on the wrong side of the glass. | shopfront close-up, palms on glass, `WRONG SIDE` | `whoosh`, `pop`, `tock` @glass |
| 13.2–17.6 | A kettle simmers away behind a kitchen door that nobody can open. | kitchen, steam over the kettle, padlocked door, `DOOR: LOCKED` | `whoosh`, `sizzle` @simmers, `tock` @door |
| 17.6–21.6 | Delivery drivers wait beside idling vans with packages still in hand. | van idling at the curb, exhaust puffs, drivers with boxes, `WAITING...` | `whoosh`, `rumble` @idling, `pop` @packages |
| 21.6–25.7 | Everyone checks the ground-floor windows, and every one of them holds. | two people rattling windows, red crosses, `ALL LOCKED` | `whoosh`, `tock` @checks, `thud` @holds |
| 25.7–29.7 | A sixty-minute countdown ticks down on every screen across the city. | countdown pills on every shop screen, `59:59` | `whoosh`, `alarm` @countdown, `tock` @ticks |
| 29.7–34.6 | With ten minutes left, the whole street goes quiet, and everybody just waits. | everyone frozen on the sidewalk, cinema bars creep in, clock races to 00:00 | `whoosh`, `heartbeat` @quiet, `tock`, `heartbeat` @waits |
| 34.6–38.7 | At one hour exactly, every lock on Earth clicks open together. | all doors fling open, padlocks fall off, gold sparkle, `EVERY DOOR: OPEN` | `whoosh`, `sparkle` @open, `pop` @together |
| 38.7–42.4 | Except one stuck bathroom latch that won't budge. | bathroom door, gold bolt shivering, red cross, `STUCK` | `whoosh`, `boing` @stuck, `slam` @budge |
| 42.4–45.0 | (end card) | hero happy among open doors, `LOCKED DOORS: 45S` | `whoosh`, `pop`, `gulp` |

## Verified locally (no Chrome / TTS / ffmpeg)

- `node --check` on every JS module; headless boot of the real modules with a stub
  canvas: 12 shots ≥ 1.4 s, every caption chunk anchored to its line with exactly one
  gold word, all cues in range, `draw(t)` clean for every 0.1 s from 0 to 44.98 s.
- `tools/mix.py` executed end to end with `scipy` stubbed: every FX generator
  (with and without `dur`) returns a finite 1-D buffer, and `data/mix.wav` comes
  out `(N, 2)` int16 — zero array-shape mismatches across all SFX cues.
