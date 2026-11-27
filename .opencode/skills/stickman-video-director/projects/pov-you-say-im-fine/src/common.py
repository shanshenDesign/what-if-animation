# -*- coding: utf-8 -*-
# Common utilities for Stickman Director

def rgba(r, g, b, a):
    """Return a tuple (r, g, b, a) with validation."""
    return (int(r), int(g), int(b), int(a))

def safe_shake(crop, slack):
    """Clamp crop values to safe ranges."""
    x, y, w, h = crop
    dx, dy, dw, dh = slack
    x = max(0, min(x + dx, 1280 - w))
    y = max(0, min(y + dy, 720 - h))
    w = max(1, min(w + dw, 1280 - x))
    h = max(1, min(h + dh, 720 - y))
    return (x, y, w, h)

def ui_snap_pop(frame):
    """Trigger a subtle UI pop effect."""
    if isinstance(frame, dict):
        frame.setdefault("effects", {})["ui_snap"] = True
    return frame

def ghost_reflection(frame, original):
    """Create a faint ghost reflection of the original frame."""
    if isinstance(frame, dict):
        frame.setdefault("effects", {})["ghost"] = True
    return frame

def crt_vignette_pulse(frame, intensity=0.2):
    """Apply a CRT vignette pulse."""
    if isinstance(frame, dict):
        frame.setdefault("effects", {})["vignette"] = intensity
    return frame

def rim_light_shift(frame, shift_x=0, shift_y=0):
    """Shift rim lighting."""
    if isinstance(frame, dict):
        frame.setdefault("effects", {})["rim_light"] = (shift_x, shift_y)
    return frame

def apply_effects(frame, scene_id):
    """Apply visual effects to a frame based on scene."""
    if isinstance(frame, dict):
        frame.setdefault("scene_id", scene_id)
        if scene_id == "you_good_hook":
            crt_vignette_pulse(frame, 0.1)
            ghost_reflection(frame, frame)
        elif scene_id == "crowd_noise_blur":
            crt_vignette_pulse(frame, 0.15)
        elif scene_id == "door_click_shut":
            crt_vignette_pulse(frame, 0.2)
        elif scene_id == "mask_drop_breath":
            crt_vignette_pulse(frame, 0.3)
            ghost_reflection(frame, frame)
            ui_snap_pop(frame)
        elif scene_id == "quiet_room_honesty":
            rim_light_shift(frame, 5, 5)
        elif scene_id == "take_a_breath_end":
            crt_vignette_pulse(frame, 0.1)
    return frame

def create_frame(width, height, scene_id, frame_idx):
    """Create a new frame (stub or wrapper used by tests/stages)."""
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGBA", (width, height), (15, 15, 25, 255))
    draw = ImageDraw.Draw(img)
    # Draw simple neon stickman
    cx, cy = width // 2, height // 2
    draw.ellipse([cx - 40, cy - 120, cx + 40, cy - 40], outline=(0, 255, 255, 255), width=3)
    draw.line([cx, cy - 40, cx, cy + 60], fill=(0, 255, 255, 255), width=3)
    draw.line([cx, cy - 10, cx - 50, cy + 30], fill=(0, 255, 255, 255), width=3)
    draw.line([cx, cy - 10, cx + 50, cy + 30], fill=(0, 255, 255, 255), width=3)
    draw.line([cx, cy + 60, cx - 40, cy + 150], fill=(0, 255, 255, 255), width=3)
    draw.line([cx, cy + 60, cx + 40, cy + 150], fill=(0, 255, 255, 255), width=3)
    
    frame_dict = {"width": width, "height": height, "scene_id": scene_id, "frame_idx": frame_idx, "effects": {}}
    apply_effects(frame_dict, scene_id)
    return img

def play_sound(sfx_type, volume=0.5):
    """Play sound helper stub."""
    import numpy as np
    sr = 44100
    t = np.linspace(0, 0.2, int(sr * 0.2), False)
    return (np.sin(2 * np.pi * 440 * t) * 32767 * volume).astype(np.int16)

def synthesize():
    """Synthesize speech stub."""
    print("[Common] synthesize() invoked.")

if __name__ == "__main__":
    synthesize()
