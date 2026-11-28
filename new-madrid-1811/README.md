# Episode 4 — New Madrid Earthquake Reverses the Mississippi (1811–1812)

House-style vertical story video built **only** from `/storage/emulated/0/animated-3d-story-video`
(`SKILL.md` + `starter-kit/`): `720x1280` (9:16), **30 fps**, Remotion + Three.js, ink `#351f22`,
3-band toon shading, weathered flat-colour canvas textures, `#e9decb` fog/sky,
`#f4ebd9` 0.4 s location dips, in-world signs only, 2D flat characters from `src/char3.js`
(ground contact shadows, yaw clamped ±0.7 rad), locations spaced at `x = 0, 40, … 360` in
`src/worlds.js`, `warpU` camera motion in `src/Full.jsx`, Kokoro TTS voice **`am_fenrir`**.

## Contents

| File | Purpose |
|------|---------|
| `script.md` | 10-shot script, shot table, full voice-over text (143 words ≈ 45 s), beat + fact check |
| `camera_plan.md` | Every camera move and per-shot animation |
| `src/sentence_times.json` | `voice: am_fenrir`, 10 sentences, 11 cut timestamps |
| `src/worlds.js` | 10 locations: levee · fissure/sand blow · falling chimneys · belfry · reversed river · abandoned town · **sinking land** · Reelfoot Lake filling · depth gauge · the lake today |
| `src/Full.jsx` | `warpU` camera travel, per-frame camera rig, `#f4ebd9` 0.4 s dips |
| `src/kit.js`, `src/char3.js` | Unchanged house-style primitives and character builder |
| `scripts/generate_voiceover.py` | `VOICE_NAME = "am_fenrir"` → `public/voiceover.wav` + exact `start`/`end`/`cuts` |
| `scripts/verify_project.py` | Pipeline verifier (passes) |
| `.github/workflows/render-video.yml` | House render workflow (Kokoro + Remotion + FFmpeg + artifact) |

## Facts used
- Great shocks of **16 Dec 1811** and **7 Feb 1812**, strongest ≈ **M 7.5–7.9**.
- The Mississippi ran **backwards** for hours; liquefaction sand blows, toppled chimneys,
  shaking felt as far as Boston; New Madrid emptied.
- **Reelfoot Lake: 15,000–25,000 acres**, **5–18 ft** deep, in Tennessee.

## Render (two paths)
1. **Your computer:** double-click `render.bat` (uses your computer's graphics card), or run
   `test_render.bat` for a 30-frame check.
2. **GitHub (free runner):** push, open the **Actions** tab and run
   **Render 3D Story Video (Kokoro am_fenrir + Remotion)** (root workflow
   `.github/workflows/render-new-madrid-1811.yml`) → download `final.mp4` from the artifacts.

Before the first render, generate the narration locally if `kokoro-onnx` is installable:
`python scripts/generate_voiceover.py` (otherwise the workflow does it and rewrites
`sentence_times.json` with exact timestamps; the checked-in values are the sanctioned
3.35 words/sec + 0.22 s estimates).
