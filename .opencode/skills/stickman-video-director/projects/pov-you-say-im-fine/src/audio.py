# -*- coding: utf-8 -*-
# Audio handling for Stickman Director
import os
import wave
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
    if not segments:
        return np.zeros(44100, dtype=np.int16)
    max_len = max(len(s) for s in segments)
    mixed = np.zeros(max_len, dtype=np.float32)
    for seg in segments:
        mixed[:len(seg)] += seg
    mixed = np.clip(mixed, -1.0, 1.0)
    return (mixed * 32767.0).astype(np.int16)

def play_sound(sfx_type, volume=0.5):
    """Play or generate a sound effect helper matching render.sh requirement."""
    if sfx_type == "tap":
        return generate_tone(880, 0.2, volume=volume)
    elif sfx_type == "swipe":
        return generate_tone(440, 0.2, volume=volume)
    elif sfx_type == "tick":
        return generate_tone(1000, 0.1, volume=volume)
    elif sfx_type == "hum":
        return generate_tone(110, 0.5, volume=volume)
    elif sfx_type == "whoosh":
        sample_rate = 44100
        return np.random.normal(0, 0.3, int(sample_rate * 0.5)).astype(np.float32) * volume
    elif sfx_type == "chime":
        return generate_tone(1568, 0.3, volume=volume)
    else:
        return generate_tone(440, 0.2, volume=volume)

def generate_mix_wav(filename="build/mix.wav"):
    """Generate mix.wav with procedural SFX and narration placeholder."""
    sample_rate = 44100
    total_duration = 40.0  # 40 seconds
    segments = [generate_tone(110, total_duration, volume=0.15)]

    # Add procedural SFX from script.json timing / markers
    # e.g. taps, whooshes, chimes
    taps = [0.15, 5.1, 12.3, 22.0, 31.5]
    for t_off in taps:
        start_idx = int(t_off * sample_rate)
        sfx = play_sound("tap", 0.4)
        if start_idx + len(sfx) <= len(segments[0]):
            seg = np.zeros_like(segments[0])
            seg[start_idx:start_idx+len(sfx)] = sfx
            segments.append(seg)

    mixed = mix_audio(segments)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(mixed.tobytes())
    print(f"[Audio] Generated {filename}")

if __name__ == "__main__":
    generate_mix_wav()
