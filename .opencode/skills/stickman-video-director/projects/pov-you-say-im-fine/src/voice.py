# Voice synthesis and lip-sync for Stickman Director
import json
import os

from .audio import play_voice_line, play_sound
from .stick import Stickman

class VoiceEngine:
    def __init__(self):
        self.engine = self.load_voice_engine()
        self.stickman = Stickman()

    def load_voice_engine(self):
        """Load the voice engine (Kokoro TTS or fallback)."""
        try:
            import kokoro_onnx
            print("[Voice] Loading Kokoro TTS engine...")
            return "Kokoro Engine"
        except Exception as e:
            print(f"[Voice] Kokoro not available ({e}), using fallback.")
            return "Fallback Engine"

    def synthesize_line(self, text, line_idx, duration, fps):
        """Synthesize a line and write to build/lines.json."""
        total_frames = int(duration * fps)
        start = (line_idx * duration) / total_frames
        end = ((line_idx + 1) * duration) / total_frames
        # Load script.json to get caps
        with open("script.json", "r") as f:
            script = json.load(f)
        line_entry = script["lines"][line_idx]
        caps = line_entry["caps"]
        entry = {
            "text": text,
            "start": round(start, 3),
            "end": round(end, 3),
            "caps": caps
        }
        os.makedirs("build", exist_ok=True)
        lines_path = "build/lines.json"
        if os.path.exists(lines_path):
            with open(lines_path, "r") as f:
                lines_data = json.load(f)
        else:
            lines_data = []
        lines_data.append(entry)
        with open(lines_path, "w") as f:
            json.dump(lines_data, f, indent=2)
        print(f"[Voice] Synthesized line {line_idx}: '{text}' ({start:.2f}s - {end:.2f}s)")

    def handle_scene(self, scene_id, frame_idx, text):
        """Handle voice for a given scene and line."""
        # Map scene_id to line index
        scene_to_line = {
            "you_good_hook": 0,
            "crowd_noise_blur": 1,
            "door_click_shut": 2,
            "mask_drop_breath": 3,
            "quiet_room_honesty": 4,
            "take_a_breath_end": 5
        }
        idx = scene_to_line.get(scene_id)
        if idx is None:
            print(f"[Voice] Unknown scene_id: {scene_id}")
            return
        # Synthesize the line using the provided text
        self.synthesize_line(text, idx, 40, 30)

if __name__ == "__main__":
    # When run as script, synthesize all lines from script.json
    engine = VoiceEngine()
    with open("script.json", "r") as f:
        script = json.load(f)
    for i, line in enumerate(script["lines"]):
        engine.synthesize_line(line["text"], i, script["duration"], script["fps"])