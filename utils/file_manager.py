from pathlib import Path
import json, re

ROOT = Path("outputs/stories")
ROOT.mkdir(parents=True, exist_ok=True)

def story_dir(title):
    safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", title).strip("_")[:50] or "cuento"
    path = ROOT / safe
    path.mkdir(parents=True, exist_ok=True)
    return path

def save_story(story, idea, genre):
    folder = story_dir(story["title"])
    payload = {"idea": idea, "genre": genre, **story}
    (folder / "story.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return folder
