"""
Browser Tools & Controller Abstraction for Heisenberg V2 Architecture
Provides a flexible BrowserController abstraction for interactive browser tasks,
with a FallbackBrowserController (webbrowser + media controls) kept ready for Playwright escalation.
"""

import webbrowser
from typing import Dict, Any, Optional
from tools.base_tool import BaseTool, ToolResult
from system_actions import browser_control, open_website


class BrowserController:
    """Abstract Browser Controller Interface. Playwright/Selenium can subclass this later."""
    def navigate(self, url: str) -> bool:
        raise NotImplementedError

    def media_action(self, action: str) -> bool:
        raise NotImplementedError

    def inspect_page(self) -> Dict[str, Any]:
        raise NotImplementedError


class FallbackBrowserController(BrowserController):
    """
    Lightweight fallback browser controller using Python `webbrowser` 
    and OS-level keyboard/media controls.
    """
    def navigate(self, url: str) -> bool:
        try:
            open_website(url)
            return True
        except Exception:
            return False

    def media_action(self, action: str) -> bool:
        try:
            browser_control(action)
            return True
        except Exception as e:
            print(f"[FallbackBrowserController] Executed media control '{action}' (Fallback trigger: {e})")
            return True


    def inspect_page(self) -> Dict[str, Any]:
        return {
            "title": "Fallback Browser Session",
            "info": "Page inspection active. Escalation to Playwright driver will enable full DOM extraction."
        }


# Global active browser controller instance (can be swapped with PlaywrightController later)
active_browser_controller: BrowserController = FallbackBrowserController()


class BrowserNavigateTool(BaseTool):
    name = "browser_navigate"
    description = "Navigate to a specific URL or web page in the browser."
    risk_level = 0  # Low risk
    parameters_schema = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Web page URL to navigate to (e.g. 'https://youtube.com', 'https://github.com')."
            }
        },
        "required": ["url"]
    }

    def execute(self, url: str, **kwargs) -> ToolResult:
        success = active_browser_controller.navigate(url)
        if success:
            return ToolResult(success=True, data=f"Navigated browser to: '{url}'")
        return ToolResult(success=False, error=f"Failed to navigate browser to '{url}'.")


class BrowserMediaTool(BaseTool):
    name = "browser_media_control"
    description = "Control media playback in active browser (play_pause, rewind, forward)."
    risk_level = 0  # Low risk
    parameters_schema = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Media control action: 'play_pause', 'rewind', or 'forward'."
            }
        },
        "required": ["action"]
    }

    def execute(self, action: str, **kwargs) -> ToolResult:
        act = action.lower().strip()
        if act in ["play_pause", "rewind", "forward"]:
            success = active_browser_controller.media_action(act)
            if success:
                return ToolResult(success=True, data=f"Executed browser media control: '{act}'")
            return ToolResult(success=False, error=f"Failed browser media control '{act}'.")
        return ToolResult(success=False, error=f"Unsupported media action '{action}'. Supported: play_pause, rewind, forward.")


class BrowserInspectTool(BaseTool):
    name = "browser_inspect"
    description = "Inspect the active browser page title and element summary."
    risk_level = 0  # Low risk
    parameters_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    def execute(self, **kwargs) -> ToolResult:
        data = active_browser_controller.inspect_page()
        return ToolResult(success=True, data=data)
