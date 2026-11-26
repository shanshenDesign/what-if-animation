# Common utilities for Stickman Director

# RGBA tuple helper to avoid concatenation bugs
def rgba(r, g, b, a):
    """Return a tuple (r, g, b, a) with validation."""
    return (int(r), int(g), int(b), int(a))

# Safe shake function with clamping
def safe_shake(crop, slack):
    """Clamp crop values to safe ranges."""
    # Assuming crop is a tuple/list of 4 values (x, y, w, h)
    # and slack is a tuple (dx, dy, dw, dh)
    x, y, w, h = crop
    dx, dy, dw, dh = slack
    x = max(0, min(x + dx, 1280 - w))
    y = max(0, min(y + dy, 720 - h))
    w = max(1, min(w + dw, 1280 - x))
    h = max(1, min(h + dh, 720 - y))
    return (x, y, w, h)

# UI snap pop for subtle cues
def ui_snap_pop(frame):
    """Trigger a subtle UI pop effect."""
    frame["effects"]["ui_snap"] = True

# Ghost reflection effect
def ghost_reflection(frame, original):
    """Create a faint ghost reflection of the original frame."""
    frame["effects"]["ghost"] = True
    return frame

# CRT vignette pulse effect
def crt_vignette_pulse(frame, intensity=0.2):
    """Apply a CRT vignette pulse."""
    frame["effects"]["vignette"] = intensity
    return frame

# Rim light shift effect
def rim_light_shift(frame, shift_x=0, shift_y=0):
    """Shift rim lighting."""
    frame["effects"]["rim_light"] = (shift_x, shift_y)
    return frame