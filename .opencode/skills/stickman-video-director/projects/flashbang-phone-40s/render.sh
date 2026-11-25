#!/usr/bin/env bash
# Render this project -> renders/<folder-name>.mp4
#
#   0 dependencies  1 narration (Kokoro TTS, free/open source, no API key)
#   2 timeline      3 frames (Pillow, 2x -> downscale)   4 audio (re-time + sfx)
#   5 encode (ffmpeg) + self-check
#
# Runs on ubuntu-latest (GitHub Actions) or any machine with python3 + ffmpeg.
# Nothing here needs a paid service or an API key.
set -euo pipefail
cd "$(dirname "$0")"

SLUG="$(basename "$PWD")"
OUT="renders/${SLUG}.mp4"
PY="$(command -v python3 || command -v python)"

echo "== 0/5 dependencies"
pkgs=""
"$PY" -c "import PIL" 2>/dev/null || pkgs="$pkgs pillow"
"$PY" -c "import numpy" 2>/dev/null || pkgs="$pkgs numpy"
"$PY" -c "import kokoro_onnx" 2>/dev/null || pkgs="$pkgs kokoro-onnx"
if [ -n "$pkgs" ]; then
  echo "installing python packages:${pkgs}"
  "$PY" -m pip install --quiet --disable-pip-version-check ${pkgs}
fi
command -v ffmpeg >/dev/null 2>&1 || { echo "::error::ffmpeg not found in PATH"; exit 1; }

echo "== 1/5 narration"
"$PY" src/voice.py .

echo "== 2/5 timeline + captions"
"$PY" src/plan.py .

FPS="$("$PY" -c "import json;print(json.load(open('build/timeline.json'))['fps'])")"
DUR="$("$PY" -c "import json;print(json.load(open('build/timeline.json'))['duration'])")"
WANT="$("$PY" -c "import json;t=json.load(open('build/timeline.json'));print(int(round(t['duration']*t['fps'])))")"

echo "== 3/5 frames ($WANT frames @ ${FPS}fps)"
rm -rf build/frames
"$PY" src/frames.py .
GOT="$(find build/frames -name 'frame_*.png' | wc -l | tr -d ' ')"
if [ "$GOT" -ne "$WANT" ]; then
  echo "::error::expected $WANT frames, got $GOT"
  exit 1
fi

echo "== 4/5 audio"
"$PY" src/audio.py .

echo "== 5/5 encode"
mkdir -p renders
ffmpeg -y -loglevel error \
  -framerate "$FPS" -start_number 0 -i "build/frames/frame_%05d.png" \
  -i build/mix.wav \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 160k -ar 48000 \
  -movflags +faststart -t "$DUR" "$OUT"

GOT_DUR="$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$OUT")"
"$PY" - "$DUR" "$GOT_DUR" <<'CHECK'
import sys
want, got = float(sys.argv[1]), float(sys.argv[2])
assert abs(got - want) < 0.4, f"duration {got:.3f}s != {want}s"
print(f"duration OK: {got:.2f}s (target {want}s)")
CHECK
echo "OK -> $OUT"
