"""
Validation Engine (Stage 1 of Heisenberg V2 Tool Pipeline)
Validates that a tool exists in the registry and required parameters are present before risk evaluation.
"""

from typing import Dict, Any, Optional
from tools_registry import registry


class ValidationResult:
    def __init__(self, valid: bool, error: Optional[str] = None):
        self.valid = valid
        self.error = error

    def __repr__(self):
        return f"ValidationResult(valid={self.valid}, error={self.error})"


def validate_tool_call(tool_name: str, arguments: Dict[str, Any]) -> ValidationResult:
    """Validates tool call existence and parameters against schema."""
    if not tool_name:
        return ValidationResult(valid=False, error="Tool name cannot be empty.")

    from tools_registry import registry
    tool = registry.get_tool(tool_name)
    if not tool:
        available = ", ".join(registry.list_tools())
        return ValidationResult(
            valid=False,
            error=f"Tool '{tool_name}' does not exist in registry. Available tools: {available}"
        )

    schema = tool.parameters_schema
    required_params = schema.get("required", [])

    if not isinstance(arguments, dict):
        return ValidationResult(valid=False, error="Tool arguments must be a JSON object.")

    missing = [param for param in required_params if param not in arguments or arguments[param] is None]
    if missing:
        return ValidationResult(
            valid=False,
            error=f"Missing required parameter(s) {missing} for tool '{tool_name}'."
        )

    return ValidationResult(valid=True)


class ValidationEngine:
    def validate_call(self, tool_name: str, arguments: Dict[str, Any]) -> ValidationResult:
        return validate_tool_call(tool_name, arguments)


validation_engine = ValidationEngine()

