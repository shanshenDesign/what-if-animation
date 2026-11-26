#!/bin/bash
# Minimal render script for Stickman Director
# This script validates the project structure and exits without actual rendering.

echo "Running lightweight sanity check for project: $1"
if [ ! -f \"script.json\" ]; then
  echo \"Error: script.json not found!\" >&2
  exit 1
fi

# Validate JSON (basic)
if ! python3 -m json.tool script.json >/dev/null 2>&1; then
  echo \"Error: script.json is not valid JSON!\" >&2
  exit 1
fi

echo \"Sanity check passed. No actual rendering performed (Android limitation).\"
exit 0