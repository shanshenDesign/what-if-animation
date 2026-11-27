#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Stage 0/5: Verify required files
echo "Stage 0/5: Verifying required files..."
if [ ! -f "script.json" ]; then
  echo "Error: script.json not found" >&2
  exit 1
fi
for f in src/*.py; do
  if [ ! -f "$f" ]; then
    echo "Error: $f missing" >&2
    exit 1
  fi
done
echo "Required files present."

# Stage 1/5: Validate JSON
echo "Stage 1/5: Validating JSON..."
if ! python3 -m json.tool script.json >/dev/null 2>&1; then
  echo "Error: script.json is not valid JSON" >&2
  exit 1
fi
echo "JSON is valid."

# Stage 2/5: Python syntax check
echo "Stage 2/5: Checking Python syntax..."
python3 -m py_compile src/*.py
echo "Python syntax OK."

# Stage 3/5: Check required functions exist
echo "Stage 3/5: Checking required effect functions..."
required_functions=(
  "rgba"
  "safe_shake"
  "ui_snap_pop"
  "ghost_reflection"
  "crt_vignette_pulse"
  "rim_light_shift"
  "apply_effects"
  "create_frame"
  "play_sound"
  "synthesize"
)
for func in "${required_functions[@]}"; do
  if ! grep -r "^[[:space:]]*def[[:space:]]\+$func" src/ >/dev/null; then
    echo "Error: function $func not defined in src/*.py" >&2
    exit 1
  fi
done
echo "All required functions present."

# Stage 4/5: Prepare build directory
echo "Stage 4/5: Preparing build directory..."
rm -rf build renders
mkdir -p build
mkdir -p build/frames
mkdir -p renders
echo "Build directory ready."

# Stage 5/5: Build pipeline execution (Narration, Timeline, Frames, Audio, MP4)
echo "Stage 5/5: Executing full build pipeline..."

# 1. Run plan.py to generate lines.json, timeline.json, captions.srt, and frames/frame_*.png
python3 -c "from src.plan import Plan; Plan().run('script.json')"

# Verify frames were generated
FRAME_COUNT=$(find build/frames -name "frame_*.png" | wc -l)
echo "Generated $FRAME_COUNT frames."
if [ "$FRAME_COUNT" -eq 0 ]; then
  echo "Error: No frames generated!" >&2
  exit 1
fi

# Verify build/mix.wav exists
if [ ! -f "build/mix.wav" ]; then
  echo "Generating fallback mix.wav..."
  python3 -c "from src.audio import generate_mix_wav; generate_mix_wav('build/mix.wav')"
fi

# Encode final MP4 via ffmpeg
echo "Encoding final MP4 via ffmpeg..."
ffmpeg -y -framerate 30 -i build/frames/frame_%05d.png -i build/mix.wav \
  -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k \
  -shortest renders/pov-you-say-im-fine.mp4

if [ ! -f "renders/pov-you-say-im-fine.mp4" ] || [ ! -s "renders/pov-you-say-im-fine.mp4" ]; then
  echo "Error: MP4 render failed or is empty." >&2
  exit 1
fi

echo "All checks and render pipeline completed successfully!"
exit 0
