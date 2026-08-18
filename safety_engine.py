"""
Safety Engine (Stage 2 of Heisenberg V2 Tool Pipeline)
Implements 3-tier risk classification:
Level 0: Low Risk -> Auto-approved
Level 1: Medium Risk -> Auto-approved with audit log
Level 2: High Risk -> Requires explicit user confirmation
"""

from typing import Dict, Any, Optional
from tools_registry import registry


class SafetyStatus:
    ALLOWED = "ALLOWED"
    NEEDS_CONFIRMATION = "NEEDS_CONFIRMATION"
    DENIED = "DENIED"


class SafetyResult:
    STATUS_ALLOWED = "ALLOWED"
    STATUS_NEEDS_CONFIRMATION = "NEEDS_CONFIRMATION"
    STATUS_DENIED = "DENIED"

    def __init__(self, status: str, prompt: Optional[str] = None):
        self.status = status
        self.prompt = prompt

    def __repr__(self):
        return f"SafetyResult(status={self.status}, prompt={self.prompt})"



def evaluate_safety(tool_name: str, arguments: Dict[str, Any], user_confirmed: bool = False) -> SafetyResult:
    from tools_registry import registry
    tool = registry.get_tool(tool_name)
    if not tool:
        return SafetyResult(status=SafetyResult.STATUS_DENIED, prompt="Unknown tool.")

    risk = tool.risk_level

    # Level 0 & Level 1: Approved automatically
    if risk < 2 or user_confirmed:
        return SafetyResult(status=SafetyResult.STATUS_ALLOWED)

    # Level 2: High risk actions require explicit user confirmation
    action_desc = f"{tool_name} with arguments {arguments}"
    confirmation_prompt = f"Warning: '{action_desc}' is a high-risk action. Do you want to proceed? (yes/no)"
    return SafetyResult(status=SafetyResult.STATUS_NEEDS_CONFIRMATION, prompt=confirmation_prompt)


class SafetyEngine:
    def evaluate_action(self, tool_name: str, arguments: Dict[str, Any], user_confirmed: bool = False) -> SafetyResult:
        return evaluate_safety(tool_name, arguments, user_confirmed)


safety_engine = SafetyEngine()

