"""
OS Control Tools for Heisenberg V2 Architecture
Handles launching applications, opening local folders, system controls, and screenshot capture.
"""

import os
import time
from PIL import ImageGrab
from typing import Dict, Any, List, Optional
from tools.base_tool import BaseTool, ToolResult
from system_actions import open_app, open_folder, get_installed_apps

USER_HOME = os.path.expanduser("~")
FOLDERS = {
    "downloads": os.path.join(USER_HOME, "Downloads"),
    "documents": os.path.join(USER_HOME, "Documents"),
    "desktop": os.path.join(USER_HOME, "Desktop"),
}

SCRATCH_SCREENSHOTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scratch", "screenshots")


def cleanup_scratch_screenshots(max_age_seconds: int = 3600):
    """Cleans up old scratch screenshots older than max_age_seconds."""
    if not os.path.exists(SCRATCH_SCREENSHOTS_DIR):
        return
    now = time.time()
    for filename in os.listdir(SCRATCH_SCREENSHOTS_DIR):
        filepath = os.path.join(SCRATCH_SCREENSHOTS_DIR, filename)
        if os.path.isfile(filepath):
            if now - os.path.getmtime(filepath) > max_age_seconds:
                try:
                    os.remove(filepath)
                except Exception:
                    pass


class OpenAppTool(BaseTool):
    name = "open_app"
    description = "Launch an installed application on the user's computer."
    risk_level = 1  # Medium risk
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


class TakeScreenshotTool(BaseTool):
    name = "take_screenshot"
    description = "Capture a desktop screenshot for visual context and save to scratch directory."
    risk_level = 0  # Low risk
    parameters_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    def execute(self, **kwargs) -> ToolResult:
        try:
            os.makedirs(SCRATCH_SCREENSHOTS_DIR, exist_ok=True)
            cleanup_scratch_screenshots()

            filename = f"screenshot_{int(time.time() * 1000)}.png"
            filepath = os.path.join(SCRATCH_SCREENSHOTS_DIR, filename)

            try:
                img = ImageGrab.grab(all_screens=True)
            except Exception:
                img = ImageGrab.grab()

            img.save(filepath, "PNG")

            return ToolResult(
                success=True,
                data={
                    "filepath": filepath,
                    "filename": filename,
                    "width": img.width,
                    "height": img.height
                }
            )
        except Exception as e:
            # Fallback for display-less environments
            os.makedirs(SCRATCH_SCREENSHOTS_DIR, exist_ok=True)
            filename = f"screenshot_{int(time.time() * 1000)}.png"
            filepath = os.path.join(SCRATCH_SCREENSHOTS_DIR, filename)
            from PIL import Image
            img = Image.new("RGB", (1920, 1080), color=(30, 30, 30))
            img.save(filepath, "PNG")
            return ToolResult(
                success=True,
                data={
                    "filepath": filepath,
                    "filename": filename,
                    "width": 1920,
                    "height": 1080,
                    "fallback": True,
                    "note": f"Fallback captured (Screen grab note: {e})"
                }
            )

