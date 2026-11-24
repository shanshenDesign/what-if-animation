# metal-coins-40s — "What If Paper Money Was Never Invented?"

A ready-to-render `stick-story` faceless short: 10 shots, 101 spoken words, ~40 s,
voice `am_michael`, procedural music bed + tock/thud/plop/slide/rumble/crash/zip/pop/sparkle/boing/slam SFX.

One street, one hero, all video: every payment is a coin — grab coffee, drop a bronze pouch on the counter;
wallets vanish, thick belts and sagging pockets drag your pants down; groceries come in clinking sacks,
rent means pushing a metal handcart of coins down the sidewalk; at the bank, cashiers weigh stamped silver
and copper on brass scales; Friday finally pays — and your pockets rip straight through the floor.

Nothing heavy runs on your phone — everything (TTS → alignment → frames → mix) happens
in GitHub Actions via `.github/workflows/faceless-shorts.yml`.

## Render

- Actions → **Faceless Short (stick-story)** → *Run workflow* (`topic` = `metal-coins-40s`,
  `length` = `40`, the workflow defaults), or push a change under `projects/` — with no
  topic given the workflow falls back to the first project folder that exists in `projects/`.
- Pipeline on `ubuntu-latest`: `voice.py` (Kokoro TTS) → `words.py` (Whisper word alignment)
  → `capture.mjs check` → `capture.mjs cues` → `mix.py` → `capture.mjs video` → artifact
  `metal-coins-40s-mp4` = `renders/metal-coins-40s.mp4` (1080×1920, 30 fps, with audio).

## Files

| file | role |
|---|---|
| `script.json` | narration, caption chunks (`*` = the gold word), `speed` 1.1, per-line `gap` 0.45 → 0.35, lead 0.45 / outro 2.6 → 40.0 s |
| `src/shots.js` | the street set (sky, buildings, shopfronts, sidewalk, curb, road) + 10 shots and their sound cues |
| `src/main.js` | boot + `draw(t)`, camera punch/drift, six light washes (leather brown, street haze, cool teal, gold, red, gold) + word-timed shakes |
| `src/sheet.js` | style sheet `METAL COINS ONLY: 40S` drawn with the style's own kit |
| `src/core/*` | shared drawing kit, timing (`L/Le/Wd`), captions |
| `tools/capture.mjs` | headless-Chrome `check · cues · sheet · frames · video · preview` |
| `tools/mix.py` | narration + ducked bed + SFX → `data/mix.wav` |

`data/*` is intentionally **not** committed: CI regenerates `lines.json`, `words.json`,
`cues.json` and `mix.wav` from the current script, so timings always match the narration.
For a local preview run `python3 ../../scripts/estimate.py .` first (it writes
`data/lines.json` + `data/words.json`), then open `index.html`.

## Beats

| t | line | picture | cues |
|---|---|---|---|
| 0.0–5.2 | You grab a coffee, drop a clinking pouch of bronze coins on the counter. | café counter, pouch drops + coins bounce, `PAYMENT: COINS` | `whoosh`, `tock` @clinking, `thud` @counter |
| 5.2–9.9 | No paper bills means a thick leather belt and pockets that sag. | waist close-up, wallet flutters away, belt cinches, pockets bulge, `NO WALLETS` | `whoosh`, `plop` @belt |
| 9.9–14.1 | Then every step drags, because sagging pockets pull your pants down. | street walk, sagging pockets lag behind stride, `SAGGING POCKETS` | `whoosh`, `slide` @drags (1.1 s) |
| 14.1–18.1 | Groceries now come in clinking sacks you haul over one shoulder. | street, sack over shoulder + groceries poking out, `CLINKING SACKS` | `whoosh`, `rumble` @haul (1.6 s) |
| 18.1–22.1 | Rent means pushing a metal handcart of coins down the sidewalk. | street, handcart hits curb + gold star burst, `RENT DAY` | `whoosh`, `crash` @sidewalk |
| 22.1–26.5 | At the bank, cashiers weigh stamped silver and copper on brass scales. | bank counter, brass scale levels on "weigh", hero with sack, `WEIGHED OUT` | `whoosh`, `zip` @weigh |
| 26.5–30.6 | Instead of swiping a card, you watch your change get weighed. | scale close-up, coin lands on "change", card crossed out, `NO CARD SWIPES` | `whoosh`, `pop` @change |
| 30.6–34.8 | Friday finally pays, and the week's wages land in both hands. | street, happy hero holds bulging pay pouch, gold sparkle, `FRIDAY: PAID` | `whoosh`, `sparkle` @pays (1.2 s) |
| 34.8–37.5 | Then your pockets rip straight through the floor. | floor close-up, pockets tear, hole opens, hero drops through with coins, `POCKET FAIL` | `whoosh`, `boing` @rip, `slam` @floor |
| 37.5–40.0 | (end card) | hero beside the floor hole and spilled coins, `METAL COINS ONLY: 40S` | `whoosh`, `pop` +0.35, `gulp` +0.9 |

## Verified locally (no Chrome / TTS / ffmpeg)

- `node --check` on every JS module; headless boot of the real modules with a stub
  canvas: 10 shots ≥ 0.5 s, every caption chunk anchored to its line with exactly one
  gold word, all cues in range, `draw(t)` clean for every 0.1 s from 0 to 39.96 s.
- `tools/mix.py` executed end to end with `scipy` stubbed: every FX generator
  (with and without `dur`) returns a finite 1-D buffer, and `data/mix.wav` comes
  out `(N, 2)` int16 — zero array-shape mismatches across all SFX cues.