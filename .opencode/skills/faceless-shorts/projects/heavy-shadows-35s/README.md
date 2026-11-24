# heavy-shadows-35s — "What if shadows suddenly weighed 50 kilograms?"

A ready-to-render `stick-story` faceless short: 8 shots, 90 spoken words, ~34.5 s,
voice `am_michael`, procedural music bed + pop/thud/rumble/slide/crash/sparkle/slam SFX.

One street, one hero, all video: the sun climbs to noon (the shadow is a puddle),
drops to 4:00 PM (the shadow stretches ten feet and yanks him flat), an umbrella
deletes the weight, a cloud slams all 50 kg back onto his heels.

Nothing heavy runs on your phone — everything (TTS → alignment → frames → mix) happens
in GitHub Actions via `.github/workflows/faceless-shorts.yml`.

## Render

- Actions → **Faceless Short (stick-story)** → *Run workflow* (`topic` = `heavy-shadows-35s`,
  the workflow default), or push a change under `projects/` — with no topic given the
  workflow falls back to the first project folder that exists in `projects/`.
- Pipeline on `ubuntu-latest`: `voice.py` (Kokoro TTS) → `words.py` (Whisper word alignment)
  → `capture.mjs check` → `capture.mjs cues` → `mix.py` → `capture.mjs video` → artifact
  `heavy-shadows-35s-mp4` = `renders/heavy-shadows-35s.mp4` (1080×1920, 30 fps, with audio).

## Files

| file | role |
|---|---|
| `script.json` | narration, caption chunks (`*` = the gold word), `speed` 1.1, per-line `gap` 0.45 → 0.35, lead 0.45 / outro 1.5 → 34.3 s |
| `src/shots.js` | the street set (sky, buildings, sidewalk, curb, road) + 8 shots and their sound cues |
| `src/main.js` | boot + `draw(t)`, camera punch/drift, four light washes (noon white, 4 PM gold, relief glow, cloud dim) + word-timed shakes |
| `src/sheet.js` | style sheet `HEAVY SHADOWS: 50 KG` drawn with the style's own kit |
| `src/core/*` | shared drawing kit, timing (`L/Le/Wd`), captions |
| `tools/capture.mjs` | headless-Chrome `check · cues · sheet · frames · video · preview` |
| `tools/mix.py` | narration + ducked bed + SFX (incl. `rumble` and `crash`) → `data/mix.wav` |

`data/*` is intentionally **not** committed: CI regenerates `lines.json`, `words.json`,
`cues.json` and `mix.wav` from the current script, so timings always match the narration.
For a local preview run `python3 ../../scripts/estimate.py .` first (it writes
`data/lines.json` + `data/words.json`), then open `index.html`.

## Beats

| t | line | picture | cues |
|---|---|---|---|
| 0.0–5.0 | Just step outside at noon and fifty kilograms locks right onto your ankles. | hero strides out, `SHADOW: 50 KG`, ankle cuffs snap on | `pop` 0.2, `pop` @fifty, `thud` @locks |
| 5.0–9.2 | At high noon, the sun hangs almost straight above your head. | sun overhead, dashed drop line, `12:00 NOON` | `whoosh`, `tock`, `pop` |
| 9.2–13.5 | That leaves your shadow as a small dark puddle under your shoes. | boots close-up, tiny shadow, `50 KG · STRAIGHT DOWN` | `whoosh`, `tock`, `pop` |
| 13.5–19.0 | By four o'clock the sun drops low, and stretches your shadow ten feet behind you. | low sun, shadow grows, `10 FEET`, `4:00 PM` | `rumble` @drops, `slide` @stretches |
| 19.0–22.3 | Then that weight yanks you flat onto the sidewalk. | shadow jerks, hero lands flat, cinema bars | `slide`, `rumble`, `crash` @sidewalk |
| 22.3–27.7 | Slip under an umbrella or into a dark room, and the weight drops to zero. | umbrella opens, shadow + cuffs vanish, `SHADOW: 0 KG` | `pop`, `tock`, `sparkle` @zero |
| 27.7–32.9 | But the second a cloud drifts over, all fifty kilograms slam back onto your heels. | cloud covers the sun, weight slams back | `boing` @cloud, `slam` @slam, `thud` |
| 32.9–34.3 | (end card) | flat under the long shadow, `HEAVY SHADOWS: 50 KG` | `whoosh`, `pop`, `gulp` |

## Verified locally (no Chrome / TTS / ffmpeg)

- `node --check` on every JS module; headless boot of the real modules with a stub
  canvas: 8 shots ≥ 1.4 s, 31 captions each with exactly one gold word, 28 cues in
  range, `draw(t)` clean for every 0.1 s from 0 to 34.31 s.
- `tools/mix.py` executed end to end with `scipy` stubbed: all 18 FX generators
  (with and without `dur`) return finite 1-D buffers of the requested length, and
  `data/mix.wav` comes out `(N, 2)` int16.
