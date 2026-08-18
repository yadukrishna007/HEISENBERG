"""
Tool Router for Heisenberg V2 Architecture
Central dispatcher that registers tools and routes execution requests
through Stage 1 (Validation Engine) and Stage 2 (Safety Engine).
"""

from typing import Dict, Any, List, Optional
from tools.base_tool import BaseTool, ToolResult
from validation_engine import validation_engine, ValidationResult
from safety_engine import safety_engine, SafetyStatus, SafetyResult


class ToolRouter:
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._sync_with_registry()

    def _sync_with_registry(self):
        from tools_registry import registry
        for tool_name in registry.list_tools():
            tool = registry.get_tool(tool_name)
            if tool:
                self.register_tool(tool)

    def register_tool(self, tool: BaseTool):
        """Registers a tool instance in the central router."""
        self.tools[tool.name] = tool



    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        return self.tools.get(tool_name)

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """Returns schemas for all registered tools."""
        return [tool.get_schema() for tool in self.tools.values()]

    def route_and_execute(self, tool_name: str, args: Dict[str, Any], user_confirmed: bool = False) -> Dict[str, Any]:
        """
        Routes tool call through:
        1. Stage 1 Validation Engine (Valid tool & parameters?)
        2. Stage 2 Safety Engine (Allowed or Needs Confirmation?)
        3. Tool Execution
        """
        # --- Stage 1: Validation Engine ---
        val_res: ValidationResult = validation_engine.validate_call(tool_name, args)
        if not val_res.valid:
            return {
                "status": "VALIDATION_FAILED",
                "result": None,
                "error": val_res.error
            }

        tool = self.tools.get(tool_name)
        if not tool:
            return {
                "status": "VALIDATION_FAILED",
                "result": None,
                "error": f"Tool '{tool_name}' not found in router registry."
            }

        # --- Stage 2: Safety Engine ---
        safety_res: SafetyResult = safety_engine.evaluate_action(tool_name, args, user_confirmed)
        if safety_res.status == SafetyStatus.NEEDS_CONFIRMATION:
            return {
                "status": "NEEDS_CONFIRMATION",
                "prompt": safety_res.prompt,
                "pending_action": {"tool": tool_name, "args": args}
            }
        elif safety_res.status == SafetyStatus.DENIED:
            return {
                "status": "SAFETY_DENIED",
                "result": None,
                "error": safety_res.prompt or "Action denied by Safety Engine."
            }

        # --- Execution Stage ---
        try:
            res: ToolResult = tool.execute(**args)
            return {
                "status": "SUCCESS" if res.success else "EXECUTION_ERROR",
                "result": res.data if res.success else None,
                "error": res.error if not res.success else None
            }
        except Exception as e:
            return {
                "status": "EXECUTION_ERROR",
                "result": None,
                "error": f"Tool execution failed with exception: {str(e)}"
            }


# Global singleton instance
tool_router = ToolRouter()
