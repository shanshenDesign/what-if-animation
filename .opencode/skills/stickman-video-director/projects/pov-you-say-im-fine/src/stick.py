# -*- coding: utf-8 -*-
# Stickman rig definition
from .common import rgba, safe_shake, ui_snap_pop, ghost_reflection, crt_vignette_pulse, rim_light_shift

COLOR_POLITE = rgba(255, 255, 255, 255)
COLOR_TIRED = rgba(200, 200, 200, 255)
COLOR_HONEST = rgba(150, 150, 150, 255)

class Stickman:
    def __init__(self):
        self.x = 640
        self.y = 360
        self.w = 200
        self.h = 300
        self.pose = "neutral"
        self.expression = "polite"
        self.eye_dir = [0, 0]
        self.pupil_offset = [0, 0]
        self.brow = 0
        self.mouth_open = 0

    def set_expression(self, expr):
        expr_map = {
            "polite": {"brow": 0.2, "mouth_open": 0.1, "eye_dir": [0.1, -0.1]},
            "tired": {"brow": -0.3, "mouth_open": 0.0, "eye_dir": [0, 0]},
            "honest": {"brow": -0.2, "mouth_open": 0.05, "eye_dir": [0, 0]},
        }
        if expr in expr_map:
            self.expression = expr
            self.brow = expr_map[expr]["brow"]
            self.mouth_open = expr_map[expr]["mouth_open"]
            self.eye_dir = expr_map[expr]["eye_dir"]
        else:
            self.expression = "neutral"

    def blink(self, frame):
        if isinstance(frame, dict):
            frame.setdefault("effects", {})["blink"] = True

    def gaze_shift(self, frame, left, right):
        if isinstance(frame, dict):
            frame.setdefault("effects", {})["gaze"] = [left, right]

    def lip_sync(self, frames):
        self.mouth_open = frames * 0.5

    def apply_effects(self, frame):
        safe_shake((1280, 720, 1, 1), (0, 0, 0, 0))
        if self.expression == "polite":
            self.blink(frame)
            self.gaze_shift(frame, 0.1, -0.1)
            ghost_reflection(frame, frame)
            crt_vignette_pulse(frame, 0.1)
        elif self.expression == "tired":
            self.blink(frame)
            crt_vignette_pulse(frame, 0.3)
        elif self.expression == "honest":
            self.gaze_shift(frame, -0.1, 0.1)
            rim_light_shift(frame, 5, 5)
        return frame
