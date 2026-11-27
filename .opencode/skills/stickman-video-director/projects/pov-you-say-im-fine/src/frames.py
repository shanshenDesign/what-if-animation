# -*- coding: utf-8 -*-
# Frame handling utilities for Stickman Director
import os
import json
from PIL import Image, ImageDraw, ImageFont

def rgba(r, g, b, a):
    return (int(r), int(g), int(b), int(a))

def safe_shake(crop, slack):
    x, y, w, h = crop
    dx, dy, dw, dh = slack
    x = max(0, min(x + dx, 1280 - w))
    y = max(0, min(y + dy, 720 - h))
    w = max(1, min(w + dw, 1280 - x))
    h = max(1, min(h + dh, 720 - y))
    return (x, y, w, h)

def ui_snap_pop(frame):
    if isinstance(frame, dict):
        frame.setdefault("effects", {})["ui_snap"] = True
    return frame

def ghost_reflection(frame, original):
    if isinstance(frame, dict):
        frame.setdefault("effects", {})["ghost"] = True
    return frame

def crt_vignette_pulse(frame, intensity=0.2):
    if isinstance(frame, dict):
        frame.setdefault("effects", {})["vignette"] = intensity
    return frame

def rim_light_shift(frame, shift_x=0, shift_y=0):
    if isinstance(frame, dict):
        frame.setdefault("effects", {})["rim_light"] = (shift_x, shift_y)
    return frame

def apply_effects(frame, scene_id):
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
    """Create a supersampled (or base) frame for the 40s POV video."""
    img = Image.new("RGBA", (width, height), (12, 12, 18, 255))
    draw = ImageDraw.Draw(img)

    # Neon color palette depending on scene
    neon_cyan = (0, 240, 255, 255)
    neon_pink = (255, 0, 128, 255)
    neon_white = (240, 245, 255, 255)
    dim_white = (160, 165, 180, 255)

    color = neon_cyan if scene_id in ["you_good_hook", "crowd_noise_blur"] else (neon_pink if scene_id == "door_click_shut" else neon_white)
    if scene_id in ["quiet_room_honesty", "take_a_breath_end"]:
        color = dim_white

    cx, cy = width // 2, height // 2 - 20

    # Stickman proportions
    head_r = 45
    body_len = 120
    arm_len = 80
    leg_len = 100

    # Breathing sway offset
    sway = int(3 * __import__("math").sin(frame_idx * 0.1))

    # Head
    draw.ellipse([cx - head_r, cy - body_len - head_r * 2 + sway, cx + head_r, cy - body_len + sway], outline=color, width=4)
    # Eyes / Expression
    if scene_id == "you_good_hook":
        # Polite smile eyes ^ ^
        draw.arc([cx - 25, cy - body_len - head_r - 15 + sway, cx - 10, cy - body_len - head_r + sway], 180, 360, fill=color, width=3)
        draw.arc([cx + 10, cy - body_len - head_r - 15 + sway, cx + 25, cy - body_len - head_r + sway], 180, 360, fill=color, width=3)
        # Smile
        draw.arc([cx - 20, cy - body_len - head_r + 10 + sway, cx + 20, cy - body_len - head_r + 30 + sway], 0, 180, fill=color, width=3)
    elif scene_id in ["mask_drop_breath", "quiet_room_honesty", "take_a_breath_end"]:
        # Tired / honest closed eyes - -
        draw.line([cx - 25, cy - body_len - head_r - 5 + sway, cx - 10, cy - body_len - head_r - 5 + sway], fill=color, width=3)
        draw.line([cx + 10, cy - body_len - head_r - 5 + sway, cx + 25, cy - body_len - head_r - 5 + sway], fill=color, width=3)
        # Flat mouth
        draw.line([cx - 15, cy - body_len - head_r + 20 + sway, cx + 15, cy - body_len - head_r + 20 + sway], fill=color, width=3)
    else:
        # Neutral dots
        draw.ellipse([cx - 20, cy - body_len - head_r - 5 + sway, cx - 12, cy - body_len - head_r + 3 + sway], fill=color)
        draw.ellipse([cx + 12, cy - body_len - head_r - 5 + sway, cx + 20, cy - body_len - head_r + 3 + sway], fill=color)
        draw.line([cx - 10, cy - body_len - head_r + 20 + sway, cx + 10, cy - body_len - head_r + 20 + sway], fill=color, width=3)

    # Spine
    draw.line([cx, cy - body_len + sway, cx, cy + sway], fill=color, width=4)
    # Arms
    arm_drop = 20 if scene_id not in ["mask_drop_breath", "quiet_room_honesty"] else 40
    draw.line([cx, cy - body_len + 30 + sway, cx - arm_len, cy - body_len + 50 + arm_drop + sway], fill=color, width=4)
    draw.line([cx, cy - body_len + 30 + sway, cx + arm_len, cy - body_len + 50 + arm_drop + sway], fill=color, width=4)
    # Legs
    draw.line([cx, cy + sway, cx - 35, cy + leg_len + sway], fill=color, width=4)
    draw.line([cx, cy + sway, cx + 35, cy + leg_len + sway], fill=color, width=4)

    # Load script for captions
    try:
        with open("script.json", "r") as f:
            script_data = json.load(f)
        scene_map = {
            "you_good_hook": 0,
            "crowd_noise_blur": 1,
            "door_click_shut": 2,
            "mask_drop_breath": 3,
            "quiet_room_honesty": 4,
            "take_a_breath_end": 5
        }
        line_idx = scene_map.get(scene_id, 0)
        line_text = script_data["lines"][line_idx]["text"]
    except Exception:
        line_text = "You good?"

    # Draw caption box at bottom
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
    except IOError:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        except IOError:
            font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), line_text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (width - tw) // 2
    ty = height - 100

    # Semi-transparent background pill for caption
    draw.rectangle([tx - 20, ty - 10, tx + tw + 20, ty + th + 10], fill=(0, 0, 0, 180), outline=color, width=2)
    draw.text((tx, ty), line_text, fill=(255, 255, 255, 255), font=font)

    frame_dict = {"width": width, "height": height, "scene_id": scene_id, "frame_idx": frame_idx, "effects": {}}
    apply_effects(frame_dict, scene_id)
    return img

def render_to_canvas(frame):
    return f"Canvas[{frame.get('width', 1280)}x{frame.get('height', 720)}]"

if __name__ == "__main__":
    os.makedirs("build/frames", exist_ok=True)
    f = create_frame(1280, 720, "you_good_hook", 0)
    f.save("build/frames/frame_00000.png")
    print("Test frame saved.")
