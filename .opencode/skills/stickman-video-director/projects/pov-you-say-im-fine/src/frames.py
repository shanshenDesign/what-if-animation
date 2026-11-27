# Frame handling utilities for Stickman Director
from .common import rgba, safe_shake, ui_snap_pop, ghost_reflection, crt_vignette_pulse, rim_light_shift
from .stick import Stickman
from PIL import Image, ImageDraw, ImageFont
import os

# Load script lines for caption text
script_lines = {}
try:
    import json
    with open("script.json", "r") as f:
        script = json.load(f)
    # Map scene_id to line text (first line of each scene)
    scene_to_line_idx = {
        "you_good_hook": 0,
        "crowd_noise_blur": 1,
        "door_click_shut": 2,
        "mask_drop_breath": 3,
        "quiet_room_honesty": 4,
        "take_a_breath_end": 5
    }
    for scene_id, idx in scene_to_line_idx.items():
        if idx < len(script["lines"]):
            script_lines[scene_id] = script["lines"][idx]["text"]
except Exception as e:
    script_lines = {}

def create_frame(width, height, scene_id, frame_idx):
    """Create a new frame with background and stickman."""
    # Determine scene ranges (equal division)
    total_frames = 1200  # 40s * 30fps
    frames_per_scene = total_frames // 6
    scene_ranges = []
    scene_ids = [
        "you_good_hook",
        "crowd_noise_blur",
        "door_click_shut",
        "mask_drop_breath",
        "quiet_room_honesty",
        "take_a_breath_end"
    ]
    for i, scene_id in enumerate(scene_ids):
        start = i * frames_per_scene
        end = (i + 1) * frames_per_scene if i < 5 else total_frames
        scene_ranges.append((scene_id, start, end))

    # Find which scene this frame belongs to
    current_scene = None
    for scene_id, start, end in scene_ranges:
        if start <= frame_idx < end:
            current_scene = scene_id
            break
    if current_scene is None:
        current_scene = "take_a_breath_end"

    # Create a blank canvas
    img = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Determine stickman expression based on scene
    expression_map = {
        "you_good_hook": "polite",
        "crowd_noise_blur": "neutral",
        "door_click_shut": "neutral",
        "mask_drop_breath": "tired",
        "quiet_room_honesty": "honest",
        "take_a_breath_end": "honest"
    }
    expr = expression_map.get(current_scene, "neutral")

    # Draw stickman (simple representation)
    x, y = width // 2, height // 2
    body_h = height * 0.6
    body_w = width * 0.2
    head_radius = width * 0.15

    # Body (line)
    draw.line([(x - body_w/2, y - body_h/2), (x + body_w/2, y - body_h/2)], fill=rgba(255,255,255,255), width=2)
    draw.line([(x - body_w/2, y - body_h/2), (x - body_w/2, y + body_h/2)], fill=rgba(255,255,255,255), width=2)
    draw.line([(x + body_w/2, y - body_h/2), (x + body_w/2, y + body_h/2)], fill=rgba(255,255,255,255), width=2)

    # Head (circle)
    draw.ellipse([(x - head_radius, y - body_h/2 - head_radius),
                  (x + head_radius, y - body_h/2 - head_radius)],
                 fill=rgba(255,255,255,255))

    # Eyes
    eye_y = y - body_h/2 - head_radius/2
    eye_w = 8
    eye_h = 4
    eye_offset = 12
    left_eye = (x - head_radius/2 - eye_offset, eye_y - eye_h/2)
    right_eye = (x + head_radius/2 - eye_offset, eye_y - eye_h/2)
    draw.ellipse([left_eye[0]-eye_w, left_eye[1]-eye_h/2, left_eye[0]+eye_w, left_eye[1]+eye_h/2],
                 fill=rgba(0,0,0,255))
    draw.ellipse([right_eye[0]-eye_w, right_eye[1]-eye_h/2, right_eye[0]+eye_w, right_eye[1]+eye_h/2],
                 fill=rgba(0,0,0,255))

    # Mouth (simple arc)
    mouth_y = y - body_h/2 + 20
    mouth_w = width * 0.2
    if expr == "polite":
        draw.arc([x - mouth_w/2, mouth_y, x + mouth_w/2, mouth_y + 5],
                 start=0, end=180, fill=rgba(0,0,0,255))
    elif expr == "tired":
        draw.line([x - mouth_w/4, mouth_y, x + mouth_w/4, mouth_y], fill=rgba(0,0,0,255), width=2)
    else:
        draw.line([x - mouth_w/4, mouth_y, x + mouth_w/4, mouth_y + 2],
                 fill=rgba(0,0,0,255), width=2)

    # Eyebrows
    brow_y = y - body_h/2 - head_radius/2 + 5
    draw.line([x - width/4, brow_y, x + width/4, brow_y],
              fill=rgba(0,0,0,255), width=2)

    # Caption text (bottom)
    caption = script_lines.get(current_scene, "No caption")
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        font = ImageFont.load_default()
    text_bbox = draw.textbbox((0,0), caption, font=font)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]
    text_pos = (x - text_w/2, y + body_h/2 + 10)
    draw.text(text_pos, caption, fill=rgba(255,255,255,255), font=font)

    # Apply visual effects
    effects = {}
    if current_scene == "you_good_hook":
        effects["vignette"] = 0.1
        effects["ghost"] = True
    elif current_scene == "mask_drop_breath":
        effects["vignette"] = 0.3
        effects["ghost"] = True
    elif current_scene == "quiet_room_honesty":
        effects["rim_light"] = (5,5)
    # safe_shake can be applied via stickman if needed
    # ui_snap_pop can be triggered here if desired
    # ghost_reflection, crt_vignette_pulse, rim_light_shift are already applied via effects dict

    # Save frame
    os.makedirs("build/frames", exist_ok=True)
    filename = f"frame_%05d.png" % frame_idx
    img.save(os.path.join("build/frames", filename))
    return img

def apply_effects(frame, scene_id):
    """Apply visual effects to a frame based on scene."""
    # This function is called by create_frame; we can add more here.
    # For now, just return the frame (effects are handled in create_frame).
    return frame

def render_to_canvas(frame):
    """Render frame to canvas (placeholder)."""
    return f"Canvas[{frame['width']}x{frame['height']}]"