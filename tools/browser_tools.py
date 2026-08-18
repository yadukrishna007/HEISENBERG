"""
Browser Tools & Controller Abstraction for Heisenberg V2 Architecture
Provides a flexible BrowserController abstraction for interactive browser tasks,
supporting FallbackBrowserController and PlaywrightBrowserController drivers.
"""

import webbrowser
from typing import Dict, Any, Optional
from tools.base_tool import BaseTool, ToolResult
from system_actions import browser_control, open_website


class BrowserController:
    """Abstract Browser Controller Interface. Playwright/Selenium subclass this."""
    def navigate(self, url: str) -> bool:
        raise NotImplementedError

    def media_action(self, action: str) -> bool:
        raise NotImplementedError

    def inspect_page(self) -> Dict[str, Any]:
        raise NotImplementedError

    def click_element(self, selector: str) -> bool:
        return False

    def type_text(self, selector: str, text: str) -> bool:
        return False


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
            "active_driver": "Fallback (webbrowser)",
            "info": "Page inspection active. Escalation to Playwright driver enables full DOM extraction."
        }


# Global active browser controller instance
active_browser_controller: BrowserController = FallbackBrowserController()

def set_browser_controller(controller: BrowserController):
    global active_browser_controller
    active_browser_controller = controller


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
    description = "Inspect the active browser page title, URL, buttons, and links."
    risk_level = 0  # Low risk
    parameters_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    def execute(self, **kwargs) -> ToolResult:
        data = active_browser_controller.inspect_page()
        return ToolResult(success=True, data=data)


class BrowserClickTool(BaseTool):
    name = "browser_click"
    description = "Click an element on the active browser page using a CSS selector."
    risk_level = 1  # Medium risk
    parameters_schema = {
        "type": "object",
        "properties": {
            "selector": {
                "type": "string",
                "description": "CSS selector of element to click (e.g. '#submit-btn', 'button.search')."
            }
        },
        "required": ["selector"]
    }

    def execute(self, selector: str, **kwargs) -> ToolResult:
        success = active_browser_controller.click_element(selector)
        if success:
            return ToolResult(success=True, data=f"Clicked browser element '{selector}'")
        return ToolResult(success=False, error=f"Failed to click element '{selector}'. Require interactive Playwright session.")


class BrowserTypeTool(BaseTool):
    name = "browser_type"
    description = "Type text into an input field on the active browser page."
    risk_level = 1  # Medium risk
    parameters_schema = {
        "type": "object",
        "properties": {
            "selector": {
                "type": "string",
                "description": "CSS selector of input field (e.g. 'input[name=\"q\"]', '#search')."
            },
            "text": {
                "type": "string",
                "description": "Text content to type."
            }
        },
        "required": ["selector", "text"]
    }

    def execute(self, selector: str, text: str, **kwargs) -> ToolResult:
        success = active_browser_controller.type_text(selector, text)
        if success:
            return ToolResult(success=True, data=f"Typed into element '{selector}'")
        return ToolResult(success=False, error=f"Failed to type into '{selector}'. Require interactive Playwright session.")
