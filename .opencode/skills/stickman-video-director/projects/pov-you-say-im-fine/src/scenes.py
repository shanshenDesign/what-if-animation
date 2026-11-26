# Scene definitions and logic for Stickman Director

from .stick import Stickman, rgba, safe_shake, ui_snap_pop, ghost_reflection, crt_vignette_pulse, rim_light_shift

# Scene IDs (match script.json)
SCENE_YOU_GOOD_HOOK = "you_good_hook"
SCENE_CROWD_NOISE_BLUR = "crowd_noise_blur"
SCENE_DOOR_CLICK_SHUT = "door_click_shut"
SCENE_MASK_DROP_BREATH = "mask_drop_breath"
SCENE_QUIET_ROOM_HONESTY = "quiet_room_honesty"
SCENE_TAKE_A_BREATH_END = "take_a_breath_end"

def get_scene_id_by_index(idx):
    """Map scene index to ID."""
    scenes = [
        SCENE_YOU_GOOD_HOOK,
        SCENE_CROWD_NOISE_BLUR,
        SCENE_DOOR_CLICK_SHUT,
        SCENE_MASK_DROP_BREATH,
        SCENE_QUIET_ROOM_HONESTY,
        SCENE_TAKE_A_BREATH_END,
    ]
    return scenes[idx] if 0 <= idx < len(scenes) else None

def apply_scene_effects(stickman, frame, scene_id):
    """Apply visual effects based on scene."""
    if scene_id == SCENE_YOU_GOOD_HOOK:
        stickman.set_expression("polite")
        stickman.blink(frame)
        stickman.gaze_shift(frame, 0.1, -0.1)
        frame = ghost_reflection(frame, frame)
        frame = crt_vignette_pulse(frame, 0.1)
        safe_shake((frame["width"], frame["height"], 1, 1), (0, 0, 0, 0))
    elif scene_id == SCENE_CROWD_NOISE_BLUR:
        stickman.set_expression("neutral")
        stickman.gaze_shift(frame, 0.2, -0.2)
        safe_shake((frame["width"], frame["height"], 1, 1), (0, 0, 0, 0))
    elif scene_id == SCENE_DOOR_CLICK_SHUT:
        stickman.set_expression("neutral")
        stickman.blink(frame)
        frame = crt_vignette_pulse(frame, 0.2)
        safe_shake((frame["width"], frame["height"], 1, 1), (0, 0, 0, 0))
    elif scene_id == SCENE_MASK_DROP_BREATH:
        stickman.set_expression("tired")
        stickman.blink(frame)
        frame = ghost_reflection(frame, frame)
        frame = crt_vignette_pulse(frame, 0.3)
        safe_shake((frame["width"], frame["height"], 1, 1), (0, 0, 0, 0))
        ui_snap_pop(frame)
    elif scene_id == SCENE_QUIET_ROOM_HONESTY:
        stickman.set_expression("honest")
        stickman.gaze_shift(frame, -0.1, 0.1)
        frame = rim_light_shift(frame, 5, 5)
        safe_shake((frame["width"], frame["height"], 1, 1), (0, 0, 0, 0))
    elif scene_id == SCENE_TAKE_A_BREATH_END:
        stickman.set_expression("honest")
        stickman.blink(frame)
        frame = crt_vignette_pulse(frame, 0.1)
        safe_shake((frame["width"], frame["height"], 1, 1), (0, 0, 0, 0))
    return frame