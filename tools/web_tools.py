"""
Web & Media Control Tools for Heisenberg V2 Architecture
Handles web searches, website opening, and media playback control.
"""

from tools.base_tool import BaseTool, ToolResult
from system_actions import open_website, browser_control, fetch_info

class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the web or Wikipedia for information on a query."
    risk_level = 0  # Low risk
    parameters_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Topic or query to search for."
            }
        },
        "required": ["query"]
    }

    def execute(self, query: str, **kwargs) -> ToolResult:
        try:
            info = fetch_info(query)
            return ToolResult(success=True, data=info)
        except Exception as e:
            return ToolResult(success=False, error=f"Web search failed for '{query}': {str(e)}")


class OpenWebsiteTool(BaseTool):
    name = "open_website"
    description = "Open a website in the default browser (e.g. 'netflix.com', 'youtube.com', 'google.com')."
    risk_level = 0  # Low risk
    parameters_schema = {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "Website URL or name to open."
            }
        },
        "required": ["target"]
    }

    def execute(self, target: str, **kwargs) -> ToolResult:
        try:
            open_website(target)
            return ToolResult(success=True, data=f"Opened website '{target}' in default browser.")
        except Exception as e:
            return ToolResult(success=False, error=f"Failed to open website '{target}': {str(e)}")


class BrowserControlTool(BaseTool):
    name = "browser_control"
    description = "Control media playback in active browser (play_pause, rewind, forward)."
    risk_level = 0  # Low risk
    parameters_schema = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Media action: 'play_pause', 'rewind', or 'forward'."
            }
        },
        "required": ["action"]
    }

    def execute(self, action: str, **kwargs) -> ToolResult:
        act = action.lower().strip()
        if act in ["play_pause", "rewind", "forward"]:
            try:
                browser_control(act)
                return ToolResult(success=True, data=f"Executed media control: '{act}'")
            except Exception as e:
                return ToolResult(success=False, error=f"Failed media control '{act}': {str(e)}")
        return ToolResult(success=False, error=f"Unknown media action '{action}'. Supported: play_pause, rewind, forward.")
