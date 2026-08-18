"""
Agent Core & Executor for Heisenberg V2 Architecture
Implements the multi-turn Agent Loop:
Observation -> Validation -> Safety -> Tool Execution -> Observation -> Finished Check?
"""

from typing import Tuple, Dict, Any, Optional
from llm_interface import interpret
from tools.tool_router import tool_router
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
                exec_data = tool_router.route_and_execute(tool_name, args, user_confirmed=True)
                if exec_data["status"] == "SUCCESS":
                    return f"Confirmed. Executed {tool_name}: {exec_data['result']}", None, {"tool": tool_name, "args": args}
                else:
                    return f"Execution failed: {exec_data.get('error')}", None, {}

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
                task_manager.complete_task(task.id)
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
                        tool_name = "browser_media_control"
                        arguments = {"action": act_map.get(intent.get("action"), "play_pause")}

                # Dispatch via ToolRouter (Stage 1 Validation + Stage 2 Safety + Execution)
                exec_data = tool_router.route_and_execute(tool_name, arguments)

                if exec_data["status"] == "VALIDATION_FAILED":
                    print(f"[Agent Loop] Stage 1 Validation Rejected: {exec_data['error']}")
                    current_prompt = f"System Error: Validation failed - {exec_data['error']}. Please retry or clarify."
                    continue

                if exec_data["status"] == "NEEDS_CONFIRMATION":
                    return exec_data["prompt"], exec_data["pending_action"], {}

                if exec_data["status"] == "SAFETY_DENIED":
                    task_manager.fail_task(task.id, exec_data["error"])
                    return f"Safety policy denied execution: {exec_data['error']}", None, {}

                if exec_data["status"] == "SUCCESS":
                    task_manager.complete_task(task.id)
                    return str(exec_data["result"]), None, {"tool": tool_name, "args": arguments}
                else:
                    task_manager.fail_task(task.id, str(exec_data.get("error")))
                    return f"Tool execution error: {exec_data.get('error')}", None, {}

        return "I completed the maximum reasoning steps without reaching a final response.", None, {}


agent_executor = AgentExecutor()
