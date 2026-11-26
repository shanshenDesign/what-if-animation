#!/usr/bin/env bash
# Commits animation projects or skills after running lightweight syntax checks.
# Usage: bash scripts/commit-animation.sh "commit message" <path1> [path2 ...]

set -e

MSG="${1:?Commit message required}"
shift
if [ $# -eq 0 ]; then
  echo "Error: At least one target path required." >&2
  exit 1
fi

echo "==> Running lightweight syntax checks on target paths..."
for path in "$@"; do
  if [ ! -e "$path" ]; then
    echo "Warning: Path '$path' does not exist." >&2
    continue
  fi

  # Find and check python files (excluding preview_frame.png, mp4, etc.)
  while IFS= read -r -d '' f; do
    echo "Checking Python: $f"
    python3 -m py_compile "$f"
  done < <(find "$path" -type f -name "*.py" -not -name "*preview_frame.png" -print0 2>/dev/null || true)

  # Find and check JSON files
  while IFS= read -r -d '' f; do
    echo "Checking JSON: $f"
    python3 -m json.tool "$f" >/dev/null
  done < <(find "$path" -type f -name "*.json" -print0 2>/dev/null || true)

  # Find and check JavaScript files (if node is available)
  if command -v node >/dev/null 2>&1; then
    while IFS= read -r -d '' f; do
      echo "Checking JS: $f"
      node --check "$f" >/dev/null
    done < <(find "$path" -type f \( -name "*.js" -o -name "*.mjs" \) -not -path "*/node_modules/*" -print0 2>/dev/null || true)
  fi

  # Find and check Bash scripts
  while IFS= read -r -d '' f; do
    echo "Checking Bash: $f"
    bash -n "$f"
  done < <(find "$path" -type f \( -name "*.sh" -o -name "*.bash" \) -not -path "*/node_modules/*" -print0 2>/dev/null || true)
done

echo "==> Staging target paths (skipping mp4 and preview_frame.png)..."
for path in "$@"; do
  if [ -d "$path" ]; then
    git add --ignore-removal "$path"
  elif [ -f "$path" ]; then
    git add -- "$path"
  fi
done

# Unstage any accidental mp4 or preview_frame.png files if matched by broad globs
git reset HEAD -- "*.mp4" "**/preview_frame.png" "preview_frame.png" 2>/dev/null || true

echo "==> Git status:"
git status --short

echo "==> Committing..."
git commit -m "$MSG"

echo "==> Commit successful!"
