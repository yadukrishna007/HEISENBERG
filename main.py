"""
Heisenberg V2 — Main Application Entry Point
Integrates complete architecture:
Perception (Voice/Text) -> Context Manager -> Attention Manager -> Model Router ->
Task Manager -> Tool Router (Validation + Safety) -> Execution Replanning Loop -> Response Engine
"""

import sys
from command_handler import handle_command
from memory_manager import memory_manager, get_state, update_state, add_alias
from voice_interface import listen, speak
from command_normalizer import normalize_command, is_valid_target
from context_manager import context_manager
from attention_manager import attention_manager, EventPriority, ActionDecision
from task_manager import task_manager
from proactive_scheduler import proactive_scheduler, SelfDiagnostics
from security_engine import security_engine
from model_router import model_router

USE_VOICE = False  # Set False for text-only mode, True for voice mode


def on_reminder_trigger(prompt: str):
    alert_msg = f"Reminder Alert: {prompt}"
    print(f"\n🔔 Heisenberg: {alert_msg}")
    if USE_VOICE:
        speak(alert_msg)


def main():
    state = get_state()
    pending_confirmation = state.get("pending_confirmation")

    # Start proactive background scheduler daemon
    proactive_scheduler.start()

    # System Health Self-Diagnostics
    health = SelfDiagnostics.get_system_health()
    print("=== Heisenberg V2 Online ===")
    print(f"System Health: {health['status']} | CPU: {health['cpu_usage_percent']}% | RAM Used: {health['ram_used_percent']}%")
    print(f"Local Model Loaded: {health['local_model_loaded']} ({health['local_model_size_gb']} GB)")
    print("Type or speak 'exit' to stop.")

    # Task Recovery check on startup
    interrupted_tasks = [t for t in task_manager.tasks.values() if t.status == "PAUSED"]
    if interrupted_tasks:
        for task in interrupted_tasks:
            print(f"\nHeisenberg: Found paused/interrupted task [{task.id}]: '{task.description}'.")
            prompt_res = input("Would you like to resume this task? (yes/no): ").strip().lower()
            if prompt_res in ("yes", "y"):
                task_manager.resume_task(task.id)
                print(f"Heisenberg: Resumed task [{task.id}]. Completed steps: {len(task.completed_steps)}")
            else:
                print("Heisenberg: Task kept on hold.")

    if state.get("last_action"):
        print(
            f"Heisenberg: Last time I was doing "
            f"{state['last_action']} ({state['last_target']})."
        )

    while True:
        try:
            # 🎤 INPUT LAYER (voice or text)
            if USE_VOICE:
                print("\nListening...")
                raw_command = listen().lower()
                normalized_command, fuzzy, suggestion = normalize_command(raw_command)

                print(f"Heard: {raw_command}")
                print(f"Normalized: {normalized_command}")

                command = normalized_command

                if command.strip() in ("exit", "quit", "stop"):
                    print("Heisenberg: Shutting down.")
                    break

                if fuzzy and suggestion:
                    print(f"Heisenberg: Did you mean open {suggestion}? (yes/no)")
                    confirmation = input("You: ").strip().lower()

                    if confirmation not in ("yes", "y"):
                        print("Heisenberg: Okay, cancelling.")
                        continue
                    else:
                        words_raw = raw_command.split()
                        words_norm = normalized_command.split()

                        for w_raw, w_norm in zip(words_raw, words_norm):
                            if w_raw != w_norm and is_valid_target(w_norm):
                                add_alias(w_raw, w_norm)
                                print(f"Heisenberg: Learned that '{w_raw}' means '{w_norm}'")
                print(f"You (voice): {command}")
            else:
                command = input("\nYou: ").strip().lower()
            
            if not command.strip():
                continue

            if command.strip() in ("exit", "quit", "stop"):
                print("Heisenberg: Shutting down.")
                break

            # Special commands: System Health check or Schedule Reminder
            if command.strip() == "system status" or command.strip() == "health":
                sys_health = SelfDiagnostics.get_system_health()
                print(f"Heisenberg Diagnostics: {sys_health}")
                continue

            # 🧠 Attention & Context Evaluation
            decision = attention_manager.evaluate_event(
                source="user",
                event_type="text_input",
                priority=EventPriority.URGENT,
                payload={"command": command}
            )

            if decision == ActionDecision.SUPPRESS:
                continue

            attention_manager.set_busy_state(True)
            context_data = context_manager.build_context(command)

            # 🧠 Core logic handling
            response, pending_confirmation, meta = handle_command(
                command,
                pending_confirmation
            )

            attention_manager.set_busy_state(False)

            # Process background events
            queued_events = attention_manager.drain_queue()
            if queued_events:
                print(f"Heisenberg Notice: Processed {len(queued_events)} background events.")

            # 💾 Persist state
            update_state(
                pending_confirmation=pending_confirmation,
                last_action=meta.get("action"),
                last_target=meta.get("target")
            )

            # 🔊 OUTPUT
            print(f"Heisenberg: {response}")
            if USE_VOICE:
                speak(response)

        except KeyboardInterrupt:
            print("\nHeisenberg: Received shutdown signal.")
            break
        except Exception as e:
            print(f"\nHeisenberg Error: {e}")

    proactive_scheduler.stop()


if __name__ == "__main__":
    main()