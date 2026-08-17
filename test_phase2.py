"""
Automated Test Suite for Phase 2 Architecture:
- Context Manager (window detection, metrics, selective clipboard)
- Attention Manager (event routing, queueing, suppression, draining)
- Task Manager (state persistence and crash recovery)
"""

import time
import os
import pyperclip
from context_manager import ContextManager
from attention_manager import AttentionManager, EventPriority, ActionDecision
from task_manager import TaskManager, TaskStatus


def test_context_manager():
    print("=== Testing Context Manager ===")
    cm = ContextManager()
    
    # 1. Active window
    win_info = cm.get_active_window()
    print(f"Active Window: {win_info}")
    assert "window_title" in win_info, "Window title key missing"

    # 2. System metrics
    metrics = cm.get_system_metrics()
    print(f"System Metrics: {metrics}")
    assert "cpu_percent" in metrics, "CPU percent key missing"
    assert "ram_percent" in metrics, "RAM percent key missing"

    # 3. Selective clipboard testing
    pyperclip.copy("Sample confidential clipboard test snippet 12345")
    
    # Query WITHOUT clipboard keywords
    normal_context = cm.build_context("Open Chrome")
    print(f"Normal Context Keys: {list(normal_context.keys())}")
    assert "clipboard_snippet" not in normal_context, "Clipboard attached unexpectedly to normal prompt!"

    # Query WITH clipboard keywords
    clip_context = cm.build_context("Summarize my clipboard text")
    print(f"Clipboard Context: {clip_context.get('clipboard_snippet')}")
    assert "clipboard_snippet" in clip_context, "Clipboard failed to attach when explicitly requested!"
    assert "Sample confidential" in clip_context["clipboard_snippet"]

    print("[OK] Context Manager tests passed.\n")


def test_attention_manager():
    print("=== Testing Attention Manager ===")
    am = AttentionManager()

    # User command -> INTERRUPT_NOW
    d1 = am.evaluate_event("user", "command", EventPriority.NORMAL, {"cmd": "open vscode"})
    print(f"User command decision: {d1}")
    assert d1 == ActionDecision.INTERRUPT_NOW, "User command should interrupt immediately"

    # Background low priority while idle -> SUPPRESS
    d2 = am.evaluate_event("system", "background_check", EventPriority.BACKGROUND, {})
    print(f"Background idle decision: {d2}")
    assert d2 == ActionDecision.SUPPRESS, "Background event should be suppressed when idle"

    # Normal background event while agent is BUSY -> QUEUE
    am.set_busy_state(True)
    d3 = am.evaluate_event("system", "email_arrived", EventPriority.NORMAL, {"subject": "Meeting"})
    print(f"Normal event while busy decision: {d3}")
    assert d3 == ActionDecision.QUEUE, "Normal system event should queue when busy"

    # Drain queue after becoming idle
    am.set_busy_state(False)
    queued = am.drain_queue()
    print(f"Drained queued events: {len(queued)}")
    assert len(queued) == 1, "Queue should contain 1 event"
    assert queued[0]["event_type"] == "email_arrived"

    print("[OK] Attention Manager tests passed.\n")


def test_task_manager_recovery():
    print("=== Testing Task Manager Crash Recovery ===")
    test_storage = os.path.join(os.path.dirname(__file__), "memory", "test_tasks.json")
    
    # Clean temporary test file if present
    if os.path.exists(test_storage):
        os.remove(test_storage)

    # 1. Initialize TaskManager & create a multi-step task
    tm1 = TaskManager(storage_file=test_storage)
    t1 = tm1.create_task("Research laptops and create summary report", steps=["search", "compare", "report"])
    tm1.record_step(t1.id, "Step 1: Searched top models", result_data={"count": 5})
    tm1.pause_task(t1.id)
    print(f"Created task [{t1.id}] status: {t1.status}")

    # 2. Simulate application restart (reload TaskManager from disk)
    tm2 = TaskManager(storage_file=test_storage)
    interrupted = tm2.get_interrupted_tasks()
    print(f"Found {len(interrupted)} interrupted task(s) after reload.")
    
    assert len(interrupted) == 1, "Failed to recover interrupted task after restart!"
    assert interrupted[0].id == t1.id, "Recovered task ID mismatch"
    assert interrupted[0].status == TaskStatus.PAUSED, "Task status mismatch"
    assert len(interrupted[0].completed_steps) == 1, "Completed steps count mismatch"

    # Resume & complete task
    tm2.resume_task(t1.id)
    tm2.complete_task(t1.id)
    assert len(tm2.get_interrupted_tasks()) == 0, "Completed task should not show in interrupted tasks"

    # Cleanup test storage file
    if os.path.exists(test_storage):
        os.remove(test_storage)

    print("[OK] Task Manager Crash Recovery tests passed.\n")


if __name__ == "__main__":
    test_context_manager()
    test_attention_manager()
    test_task_manager_recovery()
    print("=== ALL PHASE 2 ARCHITECTURE TESTS PASSED! ===")
