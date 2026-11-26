# Stickman rig definition

from .common import rgba, safe_shake, ui_snap_pop, ghost_reflection, crt_vignette_pulse, rim_light_shift

# Define colors
COLOR_POLITE = rgba(255, 255, 255, 255)  # Fake cheerful
COLOR_TIRED = rgba(200, 200, 200, 255)   # Tired neutral
COLOR_HONEST = rgba(150, 150, 150, 255)  # Honest tone

# Stickman class with expressive rig
class Stickman:
    def __init__(self):
        self.x = 640
        self.y = 360
        self.w = 200
        self.h = 300
        self.pose = "neutral"
        self.expression = "polite"
        self.eye_dir = [0, 0]  # [left_eye_dir, right_eye_dir]
        self.pupil_offset = [0, 0]
        self.brow = 0  # -1 (down) to 1 (up)
        self.mouth_open = 0  # 0 (closed) to 1 (open)

    def set_expression(self, expr):
        """Set facial expression."""
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
        """Trigger a blink."""
        frame["effects"]["blink"] = True

    def gaze_shift(self, frame, left, right):
        """Shift gaze direction."""
        frame["effects"]["gaze"] = [left, right]

    def lip_sync(self, frames):
        """Sync mouth to audio frames."""
        self.mouth_open = frames * 0.5  # Simple linear mapping

    def apply_effects(self, frame):
        """Apply visual effects to the frame."""
        # Apply safe shake (no change)
        safe_shake((frame["width"], frame["height"], 1, 1), (0, 0, 0, 0))

        if self.expression == "polite":
            self.blink(frame)
            self.gaze_shift(frame, 0.1, -0.1)
            frame = ghost_reflection(frame, frame)
            frame = crt_vignette_pulse(frame, 0.1)
        elif self.expression == "tired":
            self.blink(frame)
            frame = crt_vignette_pulse(frame, 0.3)
        elif self.expression == "honest":
            self.gaze_shift(frame, -0.1, 0.1)
            frame = rim_light_shift(frame, 5, 5)
        return frame

    def draw(self, canvas):
        """Draw the stickman on the canvas."""
        r, g, b, a = COLOR_POLITE
        if self.expression == "tired":
            r, g, b, a = COLOR_TIRED
        elif self.expression == "honest":
            r, g, b, a = COLOR_HONEST

        # Draw body
        canvas.rect(r, g, b, a, self.x - self.w//2, self.y - self.h//2, self.w, self.h)
        # Draw head
        canvas.ellipse(r, g, b, a, self.x - self.w//3, self.y - self.h//3, self.w//1.5, self.h//2)
        # Draw eyes
        canvas.ellipse(r*0.8, g*0.8, b*0.8, a*0.8, self.x - self.w//4 + self.eye_dir[0]*10, self.y - self.h//4 + 10, 10, 6)
        canvas.ellipse(r*0.8, g*0.8, b*0.8, a*0.8, self.x - self.w//4 + self.eye_dir[1]*10, self.y - self.h//4 + 10, 10, 6)
        # Draw mouth
        mouth_y = self.y - self.h//2 + 30
        mouth_w = self.w//3
        canvas.arc(r, g, b, a, self.x - mouth_w//2, mouth_y, self.x + mouth_w//2, mouth_y + 5, 0, 3.14)
        # Draw eyebrows
        canvas.line(r, g, b, a, self.x - self.w//4, self.y - self.h//3 + self.brow*15, self.x + self.w//4, self.y - self.h//3 + self.brow*15, 2)

# Helper functions
def safe_shake(crop, slack):
    """Clamp crop values to safe ranges."""
    x, y, w, h = crop
    dx, dy, dw, dh = slack
    x = max(0, min(x + dx, 1280 - w))
    y = max(0, min(y + dy, 720 - h))
    w = max(1, min(w + dw, 1280 - x))
    h = max(1, min(h + dh, 720 - y))
    return (x, y, w, h)

def ui_snap_pop():
    """Trigger a subtle UI pop effect."""
    pass

def ghost_reflection(frame, original):
    """Create a faint ghost reflection of the original frame."""
    return frame

def crt_vignette_pulse(frame, intensity=0.2):
    """Apply a CRT vignette pulse."""
    return frame

def rim_light_shift(frame, shift_x=0, shift_y=0):
    """Shift rim lighting."""
    return frame