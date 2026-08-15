"""
OS Control Tools for Heisenberg V2 Architecture
Handles launching applications, opening local system folders, and executing system controls.
"""

from tools.base_tool import BaseTool, ToolResult
from system_actions import open_app, open_folder, get_installed_apps
import os

USER_HOME = os.path.expanduser("~")
FOLDERS = {
    "downloads": os.path.join(USER_HOME, "Downloads"),
    "documents": os.path.join(USER_HOME, "Documents"),
    "desktop": os.path.join(USER_HOME, "Desktop"),
}

class OpenAppTool(BaseTool):
    name = "open_app"
    description = "Launch an installed application on the user's desktop computer."
    risk_level = 1  # Medium risk (launch app)
    parameters_schema = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Name of application to open (e.g. 'chrome', 'vscode', 'calculator', 'notepad')."
            }
        },
        "required": ["target"]
    }

    def execute(self, target: str, **kwargs) -> ToolResult:
        apps = get_installed_apps()
        target_lower = target.lower().strip()
        
        # Check direct or substring match
        matched_path = None
        if target_lower in apps:
            matched_path = apps[target_lower]
        else:
            for app_name, app_path in apps.items():
                if target_lower in app_name:
                    matched_path = app_path
                    break

        if matched_path:
            try:
                open_app(matched_path)
                return ToolResult(success=True, data=f"Successfully opened application: '{target}'")
            except Exception as e:
                return ToolResult(success=False, error=f"Failed to launch application '{target}': {str(e)}")
        else:
            return ToolResult(success=False, error=f"Application '{target}' was not found on the system.")


class OpenFolderTool(BaseTool):
    name = "open_folder"
    description = "Open a local folder directory (downloads, documents, desktop)."
    risk_level = 0  # Low risk
    parameters_schema = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Folder identifier: 'downloads', 'documents', or 'desktop'."
            }
        },
        "required": ["target"]
    }

    def execute(self, target: str, **kwargs) -> ToolResult:
        folder_key = target.lower().strip()
        if folder_key in FOLDERS:
            try:
                open_folder(FOLDERS[folder_key])
                return ToolResult(success=True, data=f"Opened folder: {folder_key}")
            except Exception as e:
                return ToolResult(success=False, error=f"Failed to open folder '{folder_key}': {str(e)}")
        return ToolResult(success=False, error=f"Unknown folder '{target}'. Supported: {list(FOLDERS.keys())}")


class SystemControlTool(BaseTool):
    name = "system_action"
    description = "Perform sensitive system actions like system shutdown or restart."
    risk_level = 2  # High risk (requires user confirmation)
    parameters_schema = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "System action to perform: 'shutdown' or 'restart'."
            }
        },
        "required": ["action"]
    }

    def execute(self, action: str, **kwargs) -> ToolResult:
        act = action.lower().strip()
        if act == "shutdown":
            return ToolResult(success=True, data="System shutdown sequence initiated (demo mode).")
        elif act == "restart":
            return ToolResult(success=True, data="System restart sequence initiated (demo mode).")
        return ToolResult(success=False, error=f"Unsupported system action '{action}'.")
