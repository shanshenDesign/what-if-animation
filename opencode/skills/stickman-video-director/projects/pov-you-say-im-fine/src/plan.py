# Main workflow plan for Stickman Director

from .scenes import get_scene_id_by_index, apply_scene_effects
from .frames import create_frame, apply_effects, render_to_canvas
from .voice import VoiceEngine
from .audio import play_sound, get_sfx_info
from .stick import Stickman, rgba, safe_shake, ui_snap_pop, ghost_reflection, crt_vignette_pulse, rim_light_shift

class Plan:
    def __init__(self, scene_indices):
        self.scene_indices = scene_indices  # List of scene indices (0-5)
        self.voice = VoiceEngine()
        self.stickman = Stickman()
        self.frame = None

    def run(self, script_json_path):
        """Execute the full plan based on script."""
        import json
        with open(script_json_path, 'r') as f:
            script = json.load(f)

        duration = script["duration"]
        fps = script["fps"]
        total_frames = duration * fps

        # Precompute scene mapping
        scene_ids = []
        for idx in self.scene_indices:
            scene_id = get_scene_id_by_index(idx)
            scene_ids.append(scene_id)

        # Main loop (simplified, no actual rendering)
        for frame_idx in range(total_frames):
            scene_idx = frame_idx // (duration / len(scene_ids))  # Rough mapping
            scene_id = scene_ids[frame_idx % len(scene_ids)] if len(scene_ids) > 0 else scene_ids[0]

            # Create frame
            self.frame = create_frame(1280, 720, scene_id)
            self.frame["scene_id"] = scene_id

            # Apply effects
            self.frame = apply_effects(self.frame, scene_id)

            # Voice handling
            if frame_idx in script["lines"]:
                line = script["lines"][frame_idx]
                self.voice.handle_scene(scene_id, frame_idx, line["text"])

            # Audio SFX
            sfx_info = get_sfx_info()
            # In real implementation, map line_idx to sfx
            # For now, just play a generic sound
            play_sound("hum", frame_idx, 0, 0.0)

            # Render to canvas (placeholder)
            canvas_output = render_to_canvas(self.frame)
            print(f"Frame {frame_idx}: {canvas_output}")

        print("Plan execution completed.")

# Example usage (not executed on Android)
if __name__ == "__main__":
    # Example: run scenes 0, 2, 4, 5 (you_good_hook, door_click_shut, quiet_room_honesty, take_a_breath_end)
    plan = Plan(scene_indices=[0, 2, 4, 5])
    plan.run("script.json")