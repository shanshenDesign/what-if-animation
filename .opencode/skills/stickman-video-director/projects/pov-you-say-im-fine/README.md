# POV - You Say You're Fine

A 40-second stickman video exploring the relatable moment when someone asks "you good?" and you respond "yeah, just tired" before the weight of the day hits once you're alone.

## Project Structure

- `script.json` – Scene and line definitions
- `render.sh` – Render pipeline entry (sanity check only)
- `README.md` – This file
- `.gitignore` – Excludes rendered files and caches
- `src/` – Source code files

## Usage

This project follows the Stickman Director workflow. On a desktop environment, run:

```bash
bash render.sh
```

On Android, the workflow is limited to syntax checks; actual rendering is handled elsewhere.

## License

MIT