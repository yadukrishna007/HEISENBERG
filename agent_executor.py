from system_actions import open_app, open_folder, APPS, FOLDERS

def execute_tool(intent: dict) -> str:
    action = intent.get("action")
    target = intent.get("target")

    if action == "open_app":
        if target in APPS:
            open_app(APPS[target])
            return f"Opened app: {target}"
        else:
            return f"App path not configured: {target}"

    if action == "open_folder":
        if target in FOLDERS:
            open_folder(FOLDERS[target])
            return f"Opened folder: {target}"
        else:
            return f"Folder path not configured: {target}"

    if action == "none":
        return "No system action required."

    return "Unknown action."
