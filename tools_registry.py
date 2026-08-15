"""
Central Tool Registry for Heisenberg V2 Architecture
Registers all available system, OS, and web tools and provides schema definitions to the LLM.
"""

from typing import Dict, Optional, List
from tools.base_tool import BaseTool
from tools.os_tools import OpenAppTool, OpenFolderTool, SystemControlTool
from tools.web_tools import WebSearchTool, OpenWebsiteTool, BrowserControlTool


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        default_tools = [
            OpenAppTool(),
            OpenFolderTool(),
            SystemControlTool(),
            WebSearchTool(),
            OpenWebsiteTool(),
            BrowserControlTool()
        ]
        for tool in default_tools:
            self.register_tool(tool)

    def register_tool(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        return list(self._tools.keys())

    def get_all_schemas(self) -> List[Dict]:
        return [tool.get_schema() for tool in self._tools.values()]


# Global singleton instance
registry = ToolRegistry()
