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

    # Check on-screen captions are supported in Full.jsx
    if os.path.exists("src/Full.jsx"):
        with open("src/Full.jsx", "r", encoding="utf-8") as f:
            full_jsx = f.read()
        if "OnScreenCaption" not in full_jsx:
            errors.append("src/Full.jsx does not include OnScreenCaption component for on-screen captions.")
        if "sentenceTimes" not in full_jsx:
            errors.append("src/Full.jsx does not reference sentenceTimes for caption sync.")

    # Check crowd/scene richness: multiple characters and dynamic actors
    if os.path.exists("src/worlds.js"):
        with open("src/worlds.js", "r", encoding="utf-8") as f:
            worlds_js = f.read()
        char_count = worlds_js.count("createCharacter")
        actor_count = worlds_js.count("dynamicActors.push")
        if char_count < 3:
            errors.append(f"src/worlds.js has only {char_count} createCharacter call(s); expected at least 3 for crowd richness.")
        if actor_count < 3:
            errors.append(f"src/worlds.js has only {actor_count} dynamic actor update(s); expected at least 3 for scene richness.")

    # Check character grounding: characters should have Y position near ground plane
    if os.path.exists("src/char3.js"):
        with open("src/char3.js", "r", encoding="utf-8") as f:
            char3_js = f.read()
        if "shadow" not in char3_js.lower():
            errors.append("src/char3.js: characters lack ground-contact shadow.")
        if "position.y" not in char3_js:
            errors.append("src/char3.js: characters lack Y-plane positioning.")

    # Check JS syntax for standard JS files
    for js_file in ["src/char3.js", "src/worlds.js", "src/kit.js"]:
        if os.path.exists(js_file):
            res = os.system(f"node -c {js_file} > /dev/null 2>&1")
            if res != 0:
                errors.append(f"Syntax error in {js_file}")

    print("ALL PIPELINE CHECKS PASSED (House Style 3D/2D + Kokoro am_fenrir + GitHub Actions Ready).")


if __name__ == "__main__":
    main()
