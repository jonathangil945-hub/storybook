def validate_story(story):
    return isinstance(story, dict) and isinstance(story.get("scenes"), list) and len(story["scenes"]) == 5
