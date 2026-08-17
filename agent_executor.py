"""
Agent Core & Executor for Heisenberg V2 Architecture
Implements the multi-turn Agent Loop:
Observation -> Validation -> Safety -> Tool Execution -> Observation -> Finished Check?
"""

from typing import Tuple, Dict, Any, Optional
from llm_interface import interpret
from validation_engine import validate_tool_call
from safety_engine import evaluate_safety, SafetyResult
from tools_registry import registry
from memory_manager import memory_manager
from task_manager import task_manager


class AgentExecutor:
    """Orchestrates the Heisenberg V2 Agent Execution Loop."""
    
    def __init__(self, max_turns: int = 3):
        self.max_turns = max_turns

    def run(self, user_input: str, pending_confirmation: Optional[Dict[str, Any]] = None) -> Tuple[str, Optional[Dict[str, Any]], Dict[str, Any]]:
        # Gatekeeper memory check
        if memory_manager.should_remember(user_input):
            remember_msg = memory_manager.extract_and_remember(user_input)
            if remember_msg:
                print(f"[Memory Gatekeeper] {remember_msg}")

        # Handle pending confirmation response
        if pending_confirmation:
            tool_name = pending_confirmation.get("tool")
            args = pending_confirmation.get("args", {})
            user_reply = user_input.strip().lower()

            if user_reply in ("yes", "y", "confirm"):
                tool = registry.get_tool(tool_name)
                if tool:
                    res = tool.execute(**args)
                    if res.success:
                        return f"Confirmed. Executed {tool_name}: {res.data}", None, {"tool": tool_name, "args": args}
                    else:
                        return f"Execution failed: {res.error}", None, {}
                return "Failed to find pending tool.", None, {}

            elif user_reply in ("no", "n", "cancel"):
                return "Action cancelled by user.", None, {}

            else:
                return "Please reply with 'yes' or 'no' to confirm.", pending_confirmation, {}

        # Track task state
        task = task_manager.create_task(description=user_input)

        # Core Agent Loop
        current_prompt = user_input
        turn_count = 0


        while turn_count < self.max_turns:
            turn_count += 1
            intent = interpret(current_prompt)
            intent_type = intent.get("intent_type")

            # Case 1: Simple conversational response
            if intent_type == "conversation":
                response_text = intent.get("response", "I am not sure how to answer that.")
                return response_text, None, {"type": "conversation"}

            # Case 2: Clarification request
            if intent_type == "clarification":
                question_text = intent.get("question", "Could you please clarify?")
                return question_text, None, {"type": "clarification"}

            # Case 3: Tool call
            if intent_type == "tool_call":
                tool_name = intent.get("action")
                target = intent.get("target")

                # Map legacy arguments if needed
                arguments = intent.get("arguments", {})
                if not arguments and target:
                    if tool_name in ("open_app", "open_folder", "open_website"):
                        arguments = {"target": target}
                    elif tool_name == "web_search":
                        arguments = {"query": target}
                    elif tool_name == "system_action":
                        arguments = {"action": target}
                    elif tool_name in ("browser_play_pause", "browser_rewind", "browser_forward"):
                        act_map = {
                            "browser_play_pause": "play_pause",
                            "browser_rewind": "rewind",
                            "browser_forward": "forward"
                        }
                        tool_name = "browser_control"
                        arguments = {"action": act_map.get(intent.get("action"), "play_pause")}


                # Stage 1: Tool Validation
                val_result = validate_tool_call(tool_name, arguments)
                if not val_result.valid:
                    print(f"[Agent Loop] Stage 1 Validation Rejected: {val_result.error}")
                    # Feed observation back to agent loop to replan or notify user
                    current_prompt = f"System Error: Validation failed - {val_result.error}. Please retry or clarify."
                    continue

                # Stage 2: Safety Engine Risk Assessment
                safety_result = evaluate_safety(tool_name, arguments)
                if safety_result.status == SafetyResult.STATUS_NEEDS_CONFIRMATION:
                    pending_data = {"tool": tool_name, "args": arguments}
                    return safety_result.prompt, pending_data, {}

                elif safety_result.status == SafetyResult.STATUS_DENIED:
                    return f"Safety policy denied execution of tool '{tool_name}'.", None, {}

                # Stage 3: Execution
                tool = registry.get_tool(tool_name)
                exec_result = tool.execute(**arguments)

                if exec_result.success:
                    return str(exec_result.data), None, {"tool": tool_name, "args": arguments}
                else:
                    return f"Tool execution error: {exec_result.error}", None, {}

        return "I completed the maximum reasoning steps without reaching a final response.", None, {}


agent_executor = AgentExecutor()
