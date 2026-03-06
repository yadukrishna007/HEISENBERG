# if  something is not in this file, then the software will not do that particular thing.  
# for example, if you want to add a new intent, then you need to add it to this file.
ALLOWED_ACTIONS = {
    "open_app",
    "open_folder",
    "open_website",
    "browser_play_pause",
    "browser_rewind",
    "browser_forward",
    "web_search",
    "none"
}

ALLOWED_TARGETS = {
    "chrome",
    "vscode",
    "downloads",
    "documents",
    "desktop"
}

def is_valid_intent(intent: dict) -> bool:
    if not isinstance(intent, dict):
        return False
    action = intent.get("action", "").strip().lower()
    target = intent.get("target", "").strip().lower() if intent.get("target") else None

    if action == "none":
        return True

    if action not in ALLOWED_ACTIONS:
        return False

    # For dynamic actions, any target is fine.
    if action in {"open_app", "open_website", "web_search"}:
        return True

    if target not in ALLOWED_TARGETS:
        return False

    return True
