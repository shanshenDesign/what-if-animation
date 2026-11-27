#!/bin/bash
set -euo pipefail

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
rm -rf build
mkdir -p build
mkdir -p build/frames
echo "Build directory ready."

# Stage 5/5: Final readiness check passed.
echo "Stage 5/5: Final readiness check passed."
echo "All checks completed successfully."
exit 0