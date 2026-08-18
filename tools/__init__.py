"""
Tools package initialization for Heisenberg V2 Architecture.
Registers all OS, Web, and Browser tools into the central ToolRouter.
"""

from tools.tool_router import tool_router
from tools.os_tools import OpenAppTool, OpenFolderTool, SystemControlTool, TakeScreenshotTool
from tools.web_tools import WebSearchTool, FetchUrlSummaryTool, OpenWebsiteTool
from tools.browser_tools import BrowserNavigateTool, BrowserMediaTool, BrowserInspectTool

# Register all tool instances into the Tool Router
tool_router.register_tool(OpenAppTool())
tool_router.register_tool(OpenFolderTool())
tool_router.register_tool(SystemControlTool())
tool_router.register_tool(TakeScreenshotTool())

tool_router.register_tool(WebSearchTool())
tool_router.register_tool(FetchUrlSummaryTool())
tool_router.register_tool(OpenWebsiteTool())

tool_router.register_tool(BrowserNavigateTool())
tool_router.register_tool(BrowserMediaTool())
tool_router.register_tool(BrowserInspectTool())

__all__ = ["tool_router"]
