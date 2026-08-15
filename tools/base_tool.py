"""
Base Tool Abstraction for Heisenberg V2 Architecture
Provides a flexible, extensible tool execution interface.
"""

from typing import Dict, Any, Optional

class ToolResult:
    """Flexible standardized result object returned by all Heisenberg tools."""
    def __init__(self, success: bool, data: Any = None, error: Optional[str] = None):
        self.success = success
        self.data = data
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error
        }

    def __repr__(self):
        return f"ToolResult(success={self.success}, data={self.data}, error={self.error})"


class BaseTool:
    """Base class for all tools in Heisenberg V2 Tool Registry."""
    name: str = ""
    description: str = ""
    parameters_schema: Dict[str, Any] = {}
    risk_level: int = 0  # 0: Low (Auto-approve), 1: Medium (Auto-approve/log), 2: High (Confirmation required)

    def execute(self, **kwargs) -> ToolResult:
        raise NotImplementedError("Subclasses must implement execute()")

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters_schema,
            "risk_level": self.risk_level
        }
