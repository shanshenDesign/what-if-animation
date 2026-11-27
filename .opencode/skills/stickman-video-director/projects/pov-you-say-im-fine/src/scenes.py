# -*- coding: utf-8 -*-
# Scene definitions and logic for Stickman Director
from .common import rgba, safe_shake, ui_snap_pop, ghost_reflection, crt_vignette_pulse, rim_light_shift

SCENE_YOU_GOOD_HOOK = "you_good_hook"
SCENE_CROWD_NOISE_BLUR = "crowd_noise_blur"
SCENE_DOOR_CLICK_SHUT = "door_click_shut"
SCENE_MASK_DROP_BREATH = "mask_drop_breath"
SCENE_QUIET_ROOM_HONESTY = "quiet_room_honesty"
SCENE_TAKE_A_BREATH_END = "take_a_breath_end"

def get_scene_id_by_index(idx):
    scenes = [
        SCENE_YOU_GOOD_HOOK,
        SCENE_CROWD_NOISE_BLUR,
        SCENE_DOOR_CLICK_SHUT,
        SCENE_MASK_DROP_BREATH,
        SCENE_QUIET_ROOM_HONESTY,
        SCENE_TAKE_A_BREATH_END,
    ]
    return scenes[idx] if 0 <= idx < len(scenes) else None

def apply_scene_effects(frame, scene_id):
    if scene_id == SCENE_YOU_GOOD_HOOK:
        crt_vignette_pulse(frame, 0.1)
        ghost_reflection(frame, frame)
    elif scene_id == SCENE_CROWD_NOISE_BLUR:
        crt_vignette_pulse(frame, 0.15)
    elif scene_id == SCENE_DOOR_CLICK_SHUT:
        crt_vignette_pulse(frame, 0.2)
    elif scene_id == SCENE_MASK_DROP_BREATH:
        crt_vignette_pulse(frame, 0.3)
        ghost_reflection(frame, frame)
        ui_snap_pop(frame)
    elif scene_id == SCENE_QUIET_ROOM_HONESTY:
        rim_light_shift(frame, 5, 5)
    elif scene_id == SCENE_TAKE_A_BREATH_END:
        crt_vignette_pulse(frame, 0.1)
    return frame
