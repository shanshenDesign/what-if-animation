# Main workflow plan for Stickman Director
from .scenes import get_scene_id_by_index, apply_scene_effects
from .frames import create_frame, apply_effects, render_to_canvas
from .voice import VoiceEngine
from .audio import play_sound, get_sfx_info
from .stick import Stickman, rgba, safe_shake, ui_snap_pop, ghost_reflection, crt_vignette_pulse, rim_light_shift
import json
import os

class Plan:
    def __init__(self, scene_indices):
        self.scene_indices = scene_indices  # List of scene indices (0-5)
        self.voice = VoiceEngine()
        self.stickman = Stickman()
        self.frame = None

    def run(self, script_json_path):
        """Execute the full plan based on script."""
        with open(script_json_path, 'r') as f:
            script = json.load(f)

        duration = script["duration"]
        fps = script["fps"]
        total_frames = int(duration * fps)

        # Precompute scene mapping (frame ranges)
        scenes = [
            ("you_good_hook", 0, int(duration / 6 * fps)),
            ("crowd_noise_blur", int(duration / 6 * fps), int(2 * duration / 6 * fps)),
            ("door_click_shut", int(2 * duration / 6 * fps), int(3 * duration / 6 * fps)),
            ("mask_drop_breath", int(3 * duration / 6 * fps), int(4 * duration / 6 * fps)),
            ("quiet_room_honesty", int(4 * duration / 6 * fps), int(5 * duration / 6 * fps)),
            ("take_a_breath_end", int(5 * duration / 6 * fps), total_frames)
        ]
        scene_ranges = {}
        for scene_id, start, end in scenes:
            scene_ranges[scene_id] = (start, end)

        # Main loop (simplified, no actual rendering)
        for frame_idx in range(total_frames):
            # Determine current scene
            current_scene = None
            for scene_id, start, end in scenes:
                if start <= frame_idx < end:
                    current_scene = scene_id
                    break
            if current_scene is None:
                current_scene = "take_a_breath_end"  # fallback

            # Create frame
            self.frame = create_frame(1280, 720, current_scene, frame_idx)
            self.frame["scene_id"] = current_scene
            self.frame["frame_idx"] = frame_idx

            # Apply effects
            self.frame = apply_effects(self.frame, current_scene)

            # Voice handling
            if frame_idx in script["lines"]:
                line = script["lines"][frame_idx]
                self.voice.handle_scene(current_scene, frame_idx, line["text"])

            # Audio SFX
            sfx_info = get_sfx_info()
            # In real implementation, map line_idx to sfx
            # For now, just play a generic sound
            play_sound("hum", frame_idx, 0, 0.0)

            # Render to canvas (placeholder)
            canvas_output = render_to_canvas(self.frame)
            print(f"Frame {frame_idx}: {canvas_output}")

        print("Plan execution completed.")

    def generate_timeline_and_captions(self, script_json_path):
        """Generate timeline.json and captions.srt."""
        with open(script_json_path, 'r') as f:
            script = json.load(f)

        duration = script["duration"]
        fps = script["fps"]
        total_frames = int(duration * fps)

        # Build timeline.json
        timeline = {
            "fps": fps,
            "duration": duration,
            "total_frames": total_frames,
            "scenes": []
        }
        # Compute scene frame ranges (equal division)
        scenes = [
            ("you_good_hook", 0, int(duration / 6 * fps)),
            ("crowd_noise_blur", int(duration / 6 * fps), int(2 * duration / 6 * fps)),
            ("door_click_shut", int(2 * duration / 6 * fps), int(3 * duration / 6 * fps)),
            ("mask_drop_breath", int(3 * duration / 6 * fps), int(4 * duration / 6 * fps)),
            ("quiet_room_honesty", int(4 * duration / 6 * fps), int(5 * duration / 6 * fps)),
            ("take_a_breath_end", int(5 * duration / 6 * fps), total_frames)
        ]
        for scene_id, start, end in scenes:
            timeline["scenes"].append({
                "id": scene_id,
                "from_frame": start,
                "to_frame": end
            })

        # Write timeline.json
        os.makedirs("build", exist_ok=True)
        with open("build/timeline.json", "w") as f:
            json.dump(timeline, f, indent=2)

        # Build captions.srt
        captions_path = "build/captions.srt"
        with open(captions_path, "w") as f:
            for idx, line in enumerate(script["lines"]):
                start_time = idx * (duration / total_frames)  # approximate
                end_time = (idx + 1) * (duration / total_frames)
                # Format time as HH:MM:SS,ms
                def fmt(seconds):
                    hrs = int(seconds // 3600)
                    mins = int((seconds % 3600) // 60)
                    secs = int(seconds % 60)
                    ms = int((seconds - int(seconds)) * 1000)
                    return f"{hrs:02}:{mins:02}:{secs:02},{ms:03}"
                start_str = fmt(start_time)
                end_str = fmt(end_time)
                caption_text = " ".join(line["caps"])
                f.write(f"{idx+1}\n")
                f.write(f"{start_str} --> {end_str}\n")
                f.write(f"{caption_text}\n\n")

        print("Timeline and captions generated.")

# Example usage (not executed on Android)
if __name__ == "__main__":
    # Example: run scenes 0, 2, 4, 5 (you_good_hook, door_click_shut, quiet_room_honesty, take_a_breath_end)
    plan = Plan(scene_indices=[0, 2, 4, 5])
    plan.run("script.json")
    plan.generate_timeline_and_captions("script.json")