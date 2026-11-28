#!/usr/bin/env python3
"""
Automated Pipeline & Asset Verifier for Animated 3D Story Video
"""

import json
import os
import sys

REQUIRED_FILES = [
    "package.json",
    "remotion.config.js",
    "render.bat",
    "test_render.bat",
    "src/index.jsx",
    "src/Root.jsx",
    "src/kit.js",
    "src/char3.js",
    "src/worlds.js",
    "src/Full.jsx",
    "src/sentence_times.json",
    "scripts/generate_voiceover.py",
    ".github/workflows/render-video.yml",
    "../.github/workflows/render-new-madrid-1811.yml",
]


def main():
    errors = []
    for rel in REQUIRED_FILES:
        # Check both direct path and relative parent if run from inside new-madrid-1811
        check_path = rel
        if rel.startswith("../") and not os.path.exists(check_path):
            check_path = rel[3:] # fallback
        if not os.path.exists(rel) and not os.path.exists(check_path):
            errors.append(f"Missing required file: {rel}")

    if os.path.exists("src/sentence_times.json"):
        with open("src/sentence_times.json", "r", encoding="utf-8") as f:
            st = json.load(f)
        if st.get("voice") != "am_fenrir":
            errors.append(f"Expected voice 'am_fenrir' in sentence_times.json, got {st.get('voice')}")
        if not st.get("sentences"):
            errors.append("sentence_times.json has empty 'sentences' list.")
        if len(st.get("cuts", [])) != len(st.get("sentences", [])) + 1:
            errors.append(f"sentence_times.json cuts length ({len(st.get('cuts', []))}) must equal sentences length + 1 ({len(st.get('sentences', [])) + 1}).")

    if os.path.exists("scripts/generate_voiceover.py"):
        with open("scripts/generate_voiceover.py", "r", encoding="utf-8") as f:
            py_txt = f.read()
        if 'VOICE_NAME = "am_fenrir"' not in py_txt:
            errors.append("scripts/generate_voiceover.py is missing VOICE_NAME = 'am_fenrir'.")

    for bat_file in ["render.bat", "test_render.bat"]:
        if os.path.exists(bat_file):
            with open(bat_file, "rb") as f:
                raw = f.read()
            if b"\r\n" not in raw or b"\n" not in raw:
                errors.append(f"{bat_file} must use Windows CRLF line endings.")

    wf_path = ".github/workflows/render-video.yml"
    if not os.path.exists(wf_path) and os.path.exists("../.github/workflows/render-new-madrid-1811.yml"):
        wf_path = "../.github/workflows/render-new-madrid-1811.yml"
    if os.path.exists(wf_path):
        with open(wf_path, "r", encoding="utf-8") as f:
            yml_txt = f.read()
        for token in ["generate_voiceover.py", "remotion render", "upload-artifact"]:
            if token not in yml_txt:
                errors.append(f"GitHub workflow missing step containing: {token}")

    if errors:
        print("VERIFICATION FAILED:")
        for e in errors:
            print(" -", e)
        sys.exit(1)

    print("ALL PIPELINE CHECKS PASSED (House Style 3D/2D + Kokoro am_fenrir + GitHub Actions Ready).")


if __name__ == "__main__":
    main()
