import os
from system_actions import open_app, open_folder, get_installed_apps, open_website, browser_control, fetch_info
from llm_interface import interpret
from intent_schema import ALLOWED_ACTIONS, ALLOWED_TARGETS, is_valid_intent
from sensitive_actions import SENSITIVE_ACTIONS
from memory_manager import increment_habit

USER_HOME = os.path.expanduser("~")

FOLDERS = {
    "downloads": os.path.join(USER_HOME, "Downloads"),
    "documents": os.path.join(USER_HOME, "Documents"),
    "desktop": os.path.join(USER_HOME, "Desktop"),
}

APPS = get_installed_apps()

ALL_TARGETS = list(FOLDERS.keys()) + list(APPS.keys())

def handle_confirmation(command, pending):
    if command in ("yes", "y"):
        return f"Confirmed. Executing {pending}.", None, True
    if command in ("no", "n"):
        return "Action cancelled.", None, False
    return "Please confirm with yes or no.", pending, None

def extract_explicit_target(command: str):
    for target in ALL_TARGETS:
        if target in command:
            return target
    return None

def looks_like_direct_command(command: str):
    words = command.split()

    if not words:
        return False

    # Direct open commands
    if words[0] == "open":
        return True

    return False

def execute(action: str, target: str) -> str:
    habit_key = f"{action}_{target}"
    increment_habit(habit_key)

    if action == "open_folder" and target in FOLDERS:
        open_folder(FOLDERS[target])
        return f"Opened folder: {target}"

    if action == "open_app" and target in APPS:
        open_app(APPS[target])
        return f"Opened app: {target}"
        
    if action == "open_website":
        open_website(target)
        return f"Opening website: {target}"
        
    if action == "web_search":
        info = fetch_info(target)
        return f"Here is what I found: {info}"
        
    if action in ["browser_play_pause", "browser_rewind", "browser_forward"]:
        browser_control(action.split("_", 1)[1])
        return "Executed media control."

    return "I understood the request, but it is not safe to execute."

def handle_command(command: str, pending_confirmation):
    # FAST ROUTER (skip AI if obvious command)
    if looks_like_direct_command(command):

        explicit_target = extract_explicit_target(command)

        if explicit_target in APPS:
            open_app(APPS[explicit_target])
            return (
                f"Opened app: {explicit_target}",
                None,
                {"action": "open_app", "target": explicit_target}
            )

        if explicit_target in FOLDERS:
            open_folder(FOLDERS[explicit_target])
            return (
                f"Opened folder: {explicit_target}",
                None,
                {"action": "open_folder", "target": explicit_target}
            )

    # 1️⃣ If waiting for confirmation
    if pending_confirmation:
        msg, new_pending, decision = handle_confirmation(
            command, pending_confirmation
        )
        return msg, new_pending, {}

    # 2️⃣ Sensitive action trigger (demo)
    if "shutdown" in command:
        return (
            "This action requires confirmation. Are you sure? (yes/no)",
            "shutdown_system",
            {}
        )

    # 3️⃣ Deterministic execution (FAST + SAFE)
    words = command.split()

    if len(words) >= 2 and words[0] == "open":
        target = words[1]

        if target in APPS:
            open_app(APPS[target])
            return (
                f"Opened app: {target}",
                None,
                {"action": "open_app", "target": target}
            )

        if target in FOLDERS:
            open_folder(FOLDERS[target])
            return (
                f"Opened folder: {target}",
                None,
                {"action": "open_folder", "target": target}
            )

    # 3.5️⃣ Deterministic MEDIA CONTROL routing
    MEDIA_PLAY_KEYWORDS = ["pause", "play", "resume", "unpause"]
    MEDIA_REWIND_KEYWORDS = ["rewind", "seek back", "go back"]
    MEDIA_FORWARD_KEYWORDS = ["seek forward", "fast forward", "skip", "go forward"]

    if any(kw in command for kw in MEDIA_PLAY_KEYWORDS):
        browser_control("play_pause")
        return "Toggled play/pause.", None, {"action": "browser_play_pause", "target": "video"}

    if any(kw in command for kw in MEDIA_REWIND_KEYWORDS):
        browser_control("rewind")
        return "Rewinding.", None, {"action": "browser_rewind", "target": "video"}

    if any(kw in command for kw in MEDIA_FORWARD_KEYWORDS):
        browser_control("forward")
        return "Skipping forward.", None, {"action": "browser_forward", "target": "video"}

    # 3.6️⃣ Deterministic WEBSITE opening (catches "open netflix", "open youtube", etc.)
    WEBSITE_KEYWORDS = [
        "netflix", "youtube", "google", "facebook", "twitter",
        "instagram", "reddit", "amazon", "github", "linkedin",
        "whatsapp", "telegram", "discord", "spotify"
    ]

    if len(words) >= 2 and words[0] == "open":
        remaining = " ".join(words[1:])
        # Check if it matches a known website or has a dot (URL-like)
        if any(site in remaining for site in WEBSITE_KEYWORDS) or "." in remaining:
            open_website(remaining)
            return (
                f"Opening {remaining} in your browser.",
                None,
                {"action": "open_website", "target": remaining}
            )

    # 3.7️⃣ Deterministic WEB SEARCH routing (factual questions)
    QUESTION_STARTERS = ["who ", "what ", "when ", "where ", "why ", "how ", "which ",
                         "tell me about ", "search for ", "look up ", "find "]

    if any(command.startswith(q) for q in QUESTION_STARTERS):
        query = command
        # Strip leading question word for cleaner search
        for q in ["search for ", "look up ", "find ", "tell me about "]:
            if command.startswith(q):
                query = command[len(q):]
                break
        info = fetch_info(query)
        return (
            f"Here's what I found: {info}",
            None,
            {"action": "web_search", "target": query}
        )

    # 4️⃣ AI-based execution (validated)
    intent = interpret(command)
    print("DEBUG INTENT:", intent)

    intent_type = intent.get("intent_type")

    if intent_type == "tool_call":
        if not is_valid_intent(intent):
            return "I cannot safely execute that.", None, {}

        result = execute(intent["action"], intent["target"])
        return result, None, intent

    if intent_type == "conversation":
        return intent.get("response", "I'm not sure how to respond."), None, {}

    if intent_type == "clarification":
        return intent.get("question", "Could you clarify?"), None, {}

    return "I did not understand that.", None, {}


    # 5️⃣ Nothing matched
    return "Command not recognized.", pending_confirmation, {}