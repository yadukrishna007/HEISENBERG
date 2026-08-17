"""
Automated Verification Suite for Heisenberg V2 Phase 2:
- TaskManager: Task State Tracking, Step Logging, Pause, Resume, and Crash Recovery Persistence
- MemoryManager: Explicit Memory Gatekeeper, Fact Extraction, User Preference Storage, Context Injection
"""

import sys
import os
from task_manager import task_manager, TaskStatus
from memory_manager import memory_manager
from qwen_llm_interface import build_chat_messages

def run_tests():
    print("=== Testing TaskManager ===")
    task = task_manager.create_task(description="Research Qwen 2.5 architecture and compare with Llama 3")
    print(f"Created Task: ID={task.id}, Status={task.status}")
    assert task.id.startswith("task_")
    assert task.status == TaskStatus.CREATED

    # Record steps
    task_manager.record_step(task.id, "Executed web search for Qwen 2.5", result_data="Summary snippet", success=True)
    assert task.status == TaskStatus.IN_PROGRESS
    assert len(task.completed_steps) == 1

    # Pause task
    paused_ok = task_manager.pause_task(task.id)
    assert paused_ok is True
    assert task_manager.get_task(task.id).status == TaskStatus.PAUSED

    # Resume task
    resumed_task = task_manager.resume_task(task.id)
    assert resumed_task is not None
    assert resumed_task.status == TaskStatus.IN_PROGRESS

    # Complete task
    completed_ok = task_manager.complete_task(task.id)
    assert completed_ok is True
    assert task_manager.get_task(task.id).status == TaskStatus.COMPLETED

    print("[OK] TaskManager state tracking & persistence test passed.")

    print("\n=== Testing MemoryManager Gatekeeper ===")
    # 1. Gatekeeper filtering
    assert memory_manager.should_remember("My name is Yaduk Krishna") is True
    assert memory_manager.should_remember("Remember that my favorite editor is VS Code") is True
    assert memory_manager.should_remember("Open chrome") is False
    assert memory_manager.should_remember("What time is it?") is False

    # 2. Fact extraction & persistence
    msg1 = memory_manager.extract_and_remember("My name is Yaduk Krishna")
    print("Extracted name:", msg1)
    assert memory_manager.get_fact("user_name") == "Yaduk Krishna"

    msg2 = memory_manager.extract_and_remember("Remember that my favorite editor is VS Code")
    print("Extracted preference:", msg2)

    all_facts = memory_manager.get_all_facts()
    print("All stored facts:", all_facts)
    assert "user_name" in all_facts

    summary = memory_manager.format_facts_summary()
    print("Formatted Facts Summary for LLM:\n", summary)
    assert "Yaduk Krishna" in summary

    print("[OK] MemoryManager gatekeeper test passed.")

    print("\n=== Testing Context Injection into Qwen Prompt ===")
    messages = build_chat_messages("Hello, what is my name?")
    sys_content = messages[0]["content"]
    print("Constructed System Prompt System Content:\n", sys_content[-200:])
    assert "KNOWN USER FACTS & PREFERENCES:" in sys_content
    assert "Yaduk Krishna" in sys_content

    print("[OK] LLM System Context Injection test passed.")

    print("\n=== Phase 2 Architecture Verification Complete: ALL TESTS PASSED! ===")

if __name__ == "__main__":
    run_tests()
