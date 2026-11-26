# Frame handling utilities for Stickman Director

from .common import rgba, safe_shake, ui_snap_pop, ghost_reflection, crt_vignette_pulse, rim_light_shift
from .stick import Stickman

def create_frame(width, height, scene_id, stickman_pose=None):
    """Create a new frame with background and stickman."""
    # Placeholder: create a blank frame with background color
    frame = {
        "width": width,
        "height": height,
        "background": rgba(0, 0, 0, 255),  # Black background
        "stickman": None,
        "effects": {}
    }
    if stickman_pose:
        stickman = Stickman()
        stickman.pose = stickman_pose
        frame["stickman"] = stickman
    return frame

def apply_effects(frame, scene_id):
    """Apply visual effects to a frame based on scene."""
    if frame["stickman"]:
        frame["effects"] = frame["stickman"].apply_effects(frame["frame"])
    else:
        # Apply scene-level effects
        if scene_id == "you_good_hook":
            frame["effects"] = {"vignette": 0.1, "ghost": True}
        elif scene_id == "mask_drop_breath":
            frame["effects"] = {"vignette": 0.3, "ghost": True}
        elif scene_id == "quiet_room_honesty":
            frame["effects"] = {"rim_light": (5, 5)}
        return frame
    return frame

def render_to_canvas(frame):
    """Render frame to canvas (placeholder)."""
    # In real implementation, this would draw to a surface
    return f"Canvas[{frame['width']}x{frame['height']}]"

def safe_shake_crop(crop, slack):
    """Safe version of shake with clamping."""
    return safe_shake(crop, slack)

def ui_snap_pop():
    """Trigger UI snap pop effect."""
    pass