"""
Automated Verification Suite for Heisenberg V2 Phase 1:
- Tool Registry Schemas
- Stage 1: Validation Engine
- Stage 2: Safety Engine
- Agent Execution Loop & Replanning
"""

import sys
from tools_registry import registry
from validation_engine import validate_tool_call
from safety_engine import evaluate_safety, SafetyResult
from agent_executor import agent_executor

def run_tests():
    print("=== Testing Tool Registry ===")
    tools = registry.list_tools()
    print("Registered tools:", tools)
    assert "open_app" in tools
    assert "open_folder" in tools
    assert "web_search" in tools
    assert "system_action" in tools
    print("[OK] Tool Registry test passed.")


    print("\n=== Testing Stage 1: Validation Engine ===")
    val_ok = validate_tool_call("open_app", {"target": "chrome"})
    print("Valid call check:", val_ok)
    assert val_ok.valid is True

    val_fake = validate_tool_call("fake_nonexistent_tool", {"arg": 123})
    print("Fake tool check:", val_fake)
    assert val_fake.valid is False
    assert "does not exist" in val_fake.error

    val_missing = validate_tool_call("open_app", {})
    print("Missing params check:", val_missing)
    assert val_missing.valid is False
    assert "Missing required" in val_missing.error
    print("[OK] Stage 1 Validation Engine test passed.")

    print("\n=== Testing Stage 2: Safety Engine ===")
    safe_low = evaluate_safety("open_folder", {"target": "documents"})
    print("Low risk check:", safe_low)
    assert safe_low.status == SafetyResult.STATUS_ALLOWED

    safe_high = evaluate_safety("system_action", {"action": "shutdown"})
    print("High risk check:", safe_high)
    assert safe_high.status == SafetyResult.STATUS_NEEDS_CONFIRMATION
    print("[OK] Stage 2 Safety Engine test passed.")

    print("\n=== Testing Agent Executor High-Risk Confirmation Flow ===")
    resp, pending, meta = agent_executor.run("shutdown the computer")
    print("Agent prompt:", resp)
    print("Pending state:", pending)
    assert pending is not None
    assert pending.get("tool") == "system_action"

    # User confirms 'yes'
    conf_resp, pending_after, _ = agent_executor.run("yes", pending_confirmation=pending)
    print("Confirmation response:", conf_resp)
    assert pending_after is None
    assert "Confirmed" in conf_resp or "initiated" in conf_resp
    print("[OK] Agent Executor confirmation flow test passed.")


    print("\n=== Phase 1 Architecture Verification Complete: ALL TESTS PASSED! ===")

if __name__ == "__main__":
    run_tests()
