import os
from system_actions import open_app, open_folder
from llm_interface import interpret
from intent_schema import ALLOWED_ACTIONS, ALLOWED_TARGETS
from sensitive_actions import SENSITIVE_ACTIONS
from memory_manager import increment_habit

USER_HOME = os.path.expanduser("~")

FOLDERS = {
    "downloads": os.path.join(USER_HOME, "Downloads"),
    "documents": os.path.join(USER_HOME, "Documents"),
    "desktop": os.path.join(USER_HOME, "Desktop"),
}

APPS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "vscode": r"C:\Users\yaduk\AppData\Local\Programs\Microsoft VS Code\Code.exe",
}

ALL_TARGETS = list(FOLDERS.keys()) + list(APPS.keys())

def handle_confirmation(command, pending):
    if command in ("yes", "y"):
        return f"Confirmed. Executing {pending}.", None, True
    if command in ("no", "n"):
        return "Action cancelled.", None, False
    return "Please confirm with yes or no.", pending, None

def is_valid_intent(intent: dict) -> bool:
    if not isinstance(intent, dict):
        return False

    action = intent.get("action")
    target = intent.get("target")

    if action not in ALLOWED_ACTIONS:
        return False

    if target not in ALLOWED_TARGETS:
        return False

    return True

def extract_explicit_target(command: str):
    for target in ALL_TARGETS:
        if target in command:
            return target
    return None

def execute(action: str, target: str) -> str:
    habit_key = f"{action}_{target}"
    increment_habit(habit_key)

    if action == "open_folder" and target in FOLDERS:
        open_folder(FOLDERS[target])
        return f"Opened folder: {target}"

    if action == "open_app" and target in APPS:
        open_app(APPS[target])
        return f"Opened app: {target}"

    return "I understood the request, but it is not safe to execute."

def handle_command(command: str, pending_confirmation):

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

    # 4️⃣ AI-based execution (validated)
    intent = interpret(command)

    if is_valid_intent(intent):
        action = intent["action"]
        target = intent["target"]

        result = execute(action, target)

        return (
            result,
            None,
            {"action": action, "target": target}
        )

    # 5️⃣ Nothing matched
    return "Command not recognized.", pending_confirmation, {}