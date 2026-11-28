# How the AI Adapts This Starter Kit for Any Story

For every new video after Step 2 (Script approval), follow these 4 exact edits:

1. **`src/sentence_times.json`**:
   - Replace `"sentences"` with the approved script lines.
   - Run `python scripts/generate_voiceover.py` to generate `public/voiceover.wav` using **Kokoro `am_fenrir`** and populate real `start`, `end`, and `cuts` timestamps.
2. **`src/worlds.js`**:
   - Place each shot's location at `x = 0, 40, 80, 120, 160...`.
   - Combine `kit.js` primitives (`createFacade`, `createCribJack`, `createElevatedDeck`, `createStoneArch`, `createLampPost`, `createCrate`, `createPlankSidewalk`, `createBarrel`, `createWorldSign`) to build each scene.
   - Spawn 2D characters via `createCharacter({ coatColor, vestColor, hat, glasses })` (`hat`: `'tophat' | 'bowler' | 'cap' | 'engineer' | 'none'`).
   - Add one entry in `shots` per cut (`camStart`, `camEnd`, `lookAt`).
3. **`scripts/verify_project.py`**:
   - Run `python scripts/verify_project.py` to confirm zero missing files, valid `am_fenrir` voice config, CRLF batch files, and valid GitHub Actions workflow.
4. **Render**:
   - Local Windows GPU: double-click `render.bat`.
   - Cloud GitHub Actions: push to GitHub and trigger `.github/workflows/render-video.yml` to download `final.mp4`.
