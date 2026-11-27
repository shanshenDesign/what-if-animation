# -*- coding: utf-8 -*-
# Main execution plan for Stickman Director
import os
import json
from .frames import create_frame, apply_effects, render_to_canvas
from .voice import VoiceEngine
from .audio import generate_mix_wav, play_sound
from .common import rgba, safe_shake, ui_snap_pop, ghost_reflection, crt_vignette_pulse, rim_light_shift, synthesize

class Plan:
    def __init__(self, scene_indices=None):
        self.scene_indices = scene_indices or [0, 1, 2, 3, 4, 5]
        self.voice = VoiceEngine()

    def run(self, script_json_path="script.json"):
        """Run the full rendering pipeline to generate build assets."""
        with open(script_json_path, "r") as f:
            script = json.load(f)

        duration = script["duration"]
        fps = script["fps"]
        total_frames = int(duration * fps)

        os.makedirs("build/frames", exist_ok=True)
        os.makedirs("renders", exist_ok=True)

        scenes = [
            ("you_good_hook", 0, int(duration / 6 * fps)),
            ("crowd_noise_blur", int(duration / 6 * fps), int(2 * duration / 6 * fps)),
            ("door_click_shut", int(2 * duration / 6 * fps), int(3 * duration / 6 * fps)),
            ("mask_drop_breath", int(3 * duration / 6 * fps), int(4 * duration / 6 * fps)),
            ("quiet_room_honesty", int(4 * duration / 6 * fps), int(5 * duration / 6 * fps)),
            ("take_a_breath_end", int(5 * duration / 6 * fps), total_frames)
        ]

        print(f"[Plan] Generating {total_frames} frames at {fps} fps ({duration}s)...")
        for frame_idx in range(total_frames):
            current_scene = "take_a_breath_end"
            for s_id, start, end in scenes:
                if start <= frame_idx < end:
                    current_scene = s_id
                    break

            # Create supersampled 2x frame (1280x720)
            img = create_frame(1280, 720, current_scene, frame_idx)
            frame_filename = f"build/frames/frame_{frame_idx:05d}.png"
            img.save(frame_filename)

            if frame_idx % 100 == 0:
                print(f"[Plan] Rendered frame {frame_idx}/{total_frames} ({current_scene})")

        # Generate audio mix.wav
        generate_mix_wav("build/mix.wav")

        # Generate timeline and captions
        self.generate_timeline_and_captions(script_json_path)
        print("[Plan] Plan execution completed successfully.")

    def generate_timeline_and_captions(self, script_json_path):
        with open(script_json_path, "r") as f:
            script = json.load(f)

        duration = script["duration"]
        fps = script["fps"]
        total_frames = int(duration * fps)

        timeline = {
            "fps": fps,
            "duration": duration,
            "total_frames": total_frames,
            "scenes": []
        }
        scenes = [
            ("you_good_hook", 0, int(duration / 6 * fps)),
            ("crowd_noise_blur", int(duration / 6 * fps), int(2 * duration / 6 * fps)),
            ("door_click_shut", int(2 * duration / 6 * fps), int(3 * duration / 6 * fps)),
            ("mask_drop_breath", int(3 * duration / 6 * fps), int(4 * duration / 6 * fps)),
            ("quiet_room_honesty", int(4 * duration / 6 * fps), int(5 * duration / 6 * fps)),
            ("take_a_breath_end", int(5 * duration / 6 * fps), total_frames)
        ]
        for s_id, start, end in scenes:
            timeline["scenes"].append({
                "id": s_id,
                "from_frame": start,
                "to_frame": end
            })

        os.makedirs("build", exist_ok=True)
        with open("build/timeline.json", "w") as f:
            json.dump(timeline, f, indent=2)

        # Build captions.srt
        captions_path = "build/captions.srt"
        line_duration = duration / len(script["lines"])
        with open(captions_path, "w") as f:
            for idx, line in enumerate(script["lines"]):
                start_time = idx * line_duration
                end_time = (idx + 1) * line_duration
                def fmt(seconds):
                    hrs = int(seconds // 3600)
                    mins = int((seconds % 3600) // 60)
                    secs = int(seconds % 60)
                    ms = int((seconds - int(seconds)) * 1000)
                    return f"{hrs:02}:{mins:02}:{secs:02},{ms:03}"
                f.write(f"{idx+1}\n")
                f.write(f"{fmt(start_time)} --> {fmt(end_time)}\n")
                f.write(f"{' '.join(line['caps'])}\n\n")

        print("[Plan] Generated timeline.json and captions.srt")

if __name__ == "__main__":
    plan = Plan()
    plan.run("script.json")
