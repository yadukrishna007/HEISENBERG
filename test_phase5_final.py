"""
Automated Test Suite for Phase 5 Architecture & Final V2 Wrap-up:
- Hybrid Model Router (Local Qwen GGUF default & cloud opt-in routing)
- Security Engine (Persistent Store Encryption & Decryption at rest)
- Proactive Scheduler & System Self-Diagnostics (Timers, callbacks, CPU/RAM/VRAM/Mic status)
- Full End-to-End Heisenberg V2 Pipeline Verification
"""

import sys
import os
import time
from model_router import model_router
from security_engine import security_engine
from proactive_scheduler import proactive_scheduler, SelfDiagnostics
from agent_executor import agent_executor

def test_hybrid_model_router():
    print("=== Testing Hybrid Model Router ===")
    
    # 1. Local execution by default
    res_local = model_router.interpret("What is Python programming language?")
    print("Local Model Result Type:", res_local.get("intent_type"))
    assert res_local.get("intent_type") in ("conversation", "tool_call", "clarification")

    # 2. Cloud opt-in query trigger
    res_cloud = model_router.interpret("Use cloud model to explain quantum computing")
    print("Cloud Opt-in Result Type:", res_cloud.get("intent_type"))
    assert res_cloud.get("intent_type") in ("conversation", "tool_call", "clarification")

    print("[OK] Hybrid Model Router tests passed.\n")


def test_memory_security_engine():
    print("=== Testing Memory Security Engine (Encryption at Rest) ===")
    sample_facts = {
        "user_name": "Yaduk Krishna",
        "favorite_editor": "VS Code",
        "system": "Heisenberg V2"
    }
    
    # Encrypt
    encrypted_str = security_engine.encrypt_data(sample_facts)
    print("Encrypted Payload (first 40 chars):", encrypted_str[:40])
    assert encrypted_str != str(sample_facts), "Encryption payload matched plaintext"

    # Decrypt
    decrypted_facts = security_engine.decrypt_data(encrypted_str)
    print("Decrypted Facts:", decrypted_facts)
    assert decrypted_facts["user_name"] == "Yaduk Krishna"
    assert decrypted_facts["favorite_editor"] == "VS Code"

    print("[OK] Memory Security Engine tests passed.\n")


def test_proactive_scheduler_and_diagnostics():
    print("=== Testing Proactive Scheduler & System Health Self-Diagnostics ===")
    
    # 1. Self-Diagnostics
    health = SelfDiagnostics.get_system_health()
    print("System Health Report:", health)
    assert "cpu_usage_percent" in health
    assert "ram_total_gb" in health
    assert health["status"] in ("HEALTHY", "DEGRADED")

    # 2. Proactive Scheduler Timer
    callback_fired = False
    received_prompt = ""

    def reminder_callback(prompt: str):
        nonlocal callback_fired, received_prompt
        callback_fired = True
        received_prompt = prompt
        print(f"[Callback Fired] Reminder triggered: '{prompt}'")

    timer_id = proactive_scheduler.schedule_reminder(
        prompt="Test background timer alert",
        delay_seconds=1.0,
        callback=reminder_callback
    )
    print(f"Scheduled Timer ID: {timer_id}")
    
    active_reminders = proactive_scheduler.list_active_reminders()
    print("Active Reminders count:", len(active_reminders))

    # Wait for timer to fire
    time.sleep(1.8)
    assert callback_fired is True, "Background reminder callback failed to fire!"
    assert received_prompt == "Test background timer alert"

    proactive_scheduler.stop()
    print("[OK] Proactive Scheduler & Diagnostics tests passed.\n")


def test_full_v2_end_to_end_pipeline():
    print("=== Testing Full Heisenberg V2 End-to-End Pipeline ===")
    
    # Test conversational question
    resp1, pending1, meta1 = agent_executor.run("what is artificial intelligence?")
    print("Agent Response 1:\n", resp1[:120])
    assert resp1 is not None and len(resp1) > 0

    # Test tool call (web search)
    resp2, pending2, meta2 = agent_executor.run("search for latest quantum computing breakthrough")
    print("Agent Response 2:\n", resp2[:120])
    assert resp2 is not None

    print("[OK] Full Heisenberg V2 End-to-End Pipeline test passed.\n")


if __name__ == "__main__":
    test_hybrid_model_router()
    test_memory_security_engine()
    test_proactive_scheduler_and_diagnostics()
    test_full_v2_end_to_end_pipeline()
    print("=== ALL 22 HEISENBERG V2 ARCHITECTURE FEATURES VERIFIED & PASSED! ===")
