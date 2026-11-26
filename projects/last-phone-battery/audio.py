"""Synthesized music bed + sci-fi tech SFX for 'The Last Phone Battery on Earth', mixed under voice.mp3."""
import numpy as np, subprocess, wave

SR = 48000
DUR = 750 / 30  # 750 frames @ 30fps = 25 seconds
N = int(DUR * SR)
rng = np.random.default_rng(42)
t_all = np.arange(N) / SR

def load_voice():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", "voice.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    v = np.frombuffer(raw, np.float32).copy()
    out = np.zeros(N, np.float32); out[:min(N, len(v))] = v[:N]; return out

def env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / r)

def lp_fast(x, cutoff):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4); return np.fft.irfft(X, len(x)).astype(np.float32)

def hp_fast(x, cutoff):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 - 1 / (1 + (f / cutoff) ** 4); return np.fft.irfft(X, len(x)).astype(np.float32)

def place(buf, sig, t0, gain=1.0):
    i = int(t0 * SR); j = min(N, i + len(sig))
    if i < N and j > i: buf[i:j] += sig[: j - i] * gain

midi = lambda m: 440 * 2 ** ((m - 69) / 12)

# ---------------- ambient sci-fi music bed ----------------
music = np.zeros(N, np.float32)
BPM = 88; beat = 60 / BPM
prog = [(48, [48, 55, 58]), (44, [44, 51, 55]), (46, [46, 53, 57]), (41, [41, 48, 52])] # Cmin Abmaj Bbmaj Fmin
def synth_pad(fs, dur):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for f in fs:
        ph = 2 * np.pi * f * t + 0.005 * np.sin(2 * np.pi * 2 * t)
        s += sum(np.sin((k + 1) * ph) / (k + 1) ** 1.5 for k in range(6))
    a = np.minimum(1, t / 0.3) * np.minimum(1, (dur - t) / 0.4).clip(0)
    return lp_fast((s * a).astype(np.float32), 1200) / len(fs)

MUSIC_END = 20.0  # music builds up to the firmware reboot twist
bar = 0; tt = 0.0
while tt < MUSIC_END:
    root, ch = prog[bar % 4]
    place(music, synth_pad([midi(m) for m in ch], beat * 4 * 0.98), tt, 0.12)
    bar += 1; tt += beat * 4

# tension synth drone towards the end
dn = int((DUR - MUSIC_END) * SR); td = np.arange(dn) / SR
drone = (np.sin(2 * np.pi * 73.4 * td) + 0.6 * np.sin(2 * np.pi * 110 * td)) * np.minimum(1, td / 2.0)
drone = lp_fast(drone.astype(np.float32), 500)
place(music, drone, MUSIC_END, 0.1)

# ---------------- sfx ----------------
sfx = np.zeros(N, np.float32)
def noise(d): return rng.standard_normal(int(d * SR)).astype(np.float32)
def beep(f0=1200, d=0.15):
    n = int(d * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f0 * t) * np.exp(-t * 12)).astype(np.float32)
def click(d=0.08):
    n = int(d * SR); t = np.arange(n) / SR
    return (hp_fast(noise(d), 2000) * np.exp(-t * 40)).astype(np.float32)
def hum(d=1.5):
    n = int(d * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 60 * t) * 0.5 + np.sin(2 * np.pi * 120 * t) * 0.25) * np.sin(np.pi * t / d) * 0.4
def power_up():
    d = 1.2; n = int(d * SR); t = np.arange(n) / SR
    f = 150 + 800 * (t / d) ** 2
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2) * 0.5).astype(np.float32)
def reboot_sting():
    d = 2.0; n = int(d * SR); t = np.arange(n) / SR
    low = np.sin(2 * np.pi * 55 * t) * np.exp(-t * 1.2) * 1.5
    sweep = np.sin(2 * np.pi * (2000 - 800 * t) * t) * np.exp(-t * 3) * 0.8
    return (low + sweep).astype(np.float32)
def whoosh(d=0.5):
    n = int(d * SR); t = np.arange(n) / SR
    return (lp_fast(noise(d), 1800) * np.sin(np.pi * t / d) ** 2 * 0.5).astype(np.float32)

F = lambda f: f / 30
place(sfx, whoosh(0.6), F(10), 0.4)           # hook reveal
place(sfx, hum(2.0), F(80), 0.5)              # ruins atmosphere
place(sfx, click(), F(255), 0.8)              # power button click
place(sfx, power_up(), F(270), 0.7)           # screen flickers to life
place(sfx, beep(1760, 0.2), F(420), 0.6)      # notification popup
place(sfx, reboot_sting(), F(605), 0.9)       # firmware update reboot

voice = load_voice()
ve = np.abs(voice); k = int(0.05 * SR)
ve = np.convolve(ve, np.ones(k) / k, "same"); duck = 1 - 0.45 * np.clip(ve / (ve.max() * 0.25), 0, 1)
mix = voice + music * duck * 1.4 + sfx * 0.5
mix = np.tanh(mix * 0.95) / np.tanh(0.95)
fade = int(0.04 * SR); mix[-fade:] *= np.linspace(1, 0, fade)
pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
with wave.open("mix_raw.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("ok audio.py", len(pcm) / SR)
