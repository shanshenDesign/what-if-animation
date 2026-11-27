# Audio handling for Stickman Director
import wave
import struct
import time
import numpy as np

def generate_tone(frequency, duration, volume=0.5, sample_rate=44100):
    """Generate a sine wave tone."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = volume * np.sin(2 * np.pi * frequency * t)
    return tone.astype(np.float32)

def generate_silence(duration, sample_rate=44100):
    """Generate silence."""
    return np.zeros(int(sample_rate * duration), dtype=np.float32)

def mix_audio(segments):
    """Mix audio segments (simple addition with clipping)."""
    max_val = 32767.0
    mixed = np.zeros_like(segments[0])
    for seg in segments:
        mixed += seg
    # Clip to int16 range
    mixed = np.clip(mixed, -1.0, 1.0)
    return (mixed * max_val).astype(np.int16)

def generate_mix_wav(filename="build/mix.wav"):
    """Generate mix.wav with procedural SFX."""
    sample_rate = 44100
    total_duration = 40.0  # match video duration
    segments = []

    # Continuous hum (low frequency)
    hum = generate_tone(110, total_duration, volume=0.2)
    segments.append(hum)

    # Tap at 5s
    tap = generate_tone(880, 0.2, volume=0.5)
    segments.append(tap)

    # Swipe at 10s
    swipe = generate_tone(440, 0.2, volume=0.5)
    segments.append(swipe)

    # Tick at 15s
    tick = generate_tone(1000, 0.1, volume=0.5)
    segments.append(tick)

    # Hum continues (already added)

    # Chime at 20s
    chime = generate_tone(1568, 0.3, volume=0.6)
    segments.append(chime)

    # Whoosh at 25s (white noise sweep)
    whoosh = np.random.normal(0, 0.3, int(sample_rate * 0.5))
    segments.append(whoosh)

    # Ensure total length matches
    # Mix all segments
    mixed = mix_audio(segments)

    # Write WAV file
    os.makedirs("build", exist_ok=True)
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(mixed.tobytes())
    print(f"[Audio] Generated {filename}")

if __name__ == "__main__":
    generate_mix_wav()