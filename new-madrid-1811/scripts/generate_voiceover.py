#!/usr/bin/env python3
"""
Free Kokoro TTS Voice-Over Generator (voice: am_fenrir)
Generates public/voiceover.wav and updates src/sentence_times.json with exact durations.
"""

import json
import os
import urllib.request
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

MODEL_PATH = os.path.join("scripts", "kokoro-v1.0.onnx")
VOICES_PATH = os.path.join("scripts", "voices-v1.0.bin")
TIMES_PATH = os.path.join("src", "sentence_times.json")
OUT_WAV = os.path.join("public", "voiceover.wav")

VOICE_NAME = "am_fenrir"
SPEED = 1.0


def ensure_models():
    os.makedirs("scripts", exist_ok=True)
    if not os.path.exists(MODEL_PATH):
        print(f"Downloading {MODEL_URL}...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    if not os.path.exists(VOICES_PATH):
        print(f"Downloading {VOICES_URL}...")
        urllib.request.urlretrieve(VOICES_URL, VOICES_PATH)


def main():
    ensure_models()
    with open(TIMES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    kokoro = Kokoro(MODEL_PATH, VOICES_PATH)
    audio_segments = []
    cursor = 0.0
    sample_rate = 24000
    cuts = [0.0]

    for sent in data["sentences"]:
        samples, sr = kokoro.create(
            sent["text"],
            voice=VOICE_NAME,
            speed=SPEED,
            lang="en-us",
        )
        sample_rate = sr
        pause = np.zeros(int(sr * 0.22), dtype=np.float32)
        combined = np.concatenate([samples, pause])
        dur = len(combined) / sr

        sent["start"] = round(cursor, 3)
        cursor += dur
        sent["end"] = round(cursor, 3)
        cuts.append(sent["end"])
        audio_segments.append(combined)
        print(f"[{sent['start']:.2f}s -> {sent['end']:.2f}s] {sent['text']}")

    os.makedirs("public", exist_ok=True)
    full_audio = np.concatenate(audio_segments)
    sf.write(OUT_WAV, full_audio, sample_rate)

    data["voice"] = VOICE_NAME
    data["hasAudio"] = True
    data["cuts"] = cuts
    with open(TIMES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Saved {OUT_WAV} ({cursor:.2f}s) using voice '{VOICE_NAME}'.")


if __name__ == "__main__":
    main()
