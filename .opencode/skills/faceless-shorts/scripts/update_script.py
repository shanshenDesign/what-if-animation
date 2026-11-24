import json
import os
from pathlib import Path

topic = os.environ.get("TOPIC", "").strip()
style = os.environ.get("STYLE", "").strip()
length_raw = os.environ.get("LENGTH", "30").strip()
voice = os.environ.get("VOICE", "am_michael").strip()

try:
    length = int(length_raw)
except ValueError:
    length = 30

script_path = Path("script.json")
script = json.loads(script_path.read_text(encoding="utf-8"))

topic_clean = topic.rstrip("?")
if topic_clean and not topic_clean.lower().startswith("what"):
    topic_clean = f"What happens if {topic_clean}"

if topic_clean:
    script["title"] = topic_clean + "?"
script["style"] = style
script["target_duration_sec"] = length
script["voice"] = voice

script_path.write_text(json.dumps(script, indent=2) + "\n", encoding="utf-8")
