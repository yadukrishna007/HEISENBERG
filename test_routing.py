"""
Quick integration test for deterministic routing in command_handler.
Tests that media controls, website opening, and web search bypass the LLM.
"""

# Monkey-patch system_actions to avoid actually opening apps/websites
import system_actions
system_actions.open_website = lambda url: print(f"  [MOCK] open_website({url})")
system_actions.browser_control = lambda action: print(f"  [MOCK] browser_control({action})")
system_actions.open_app = lambda path: print(f"  [MOCK] open_app({path})")
system_actions.open_folder = lambda path: print(f"  [MOCK] open_folder({path})")

# Override fetch_info to avoid network calls
original_fetch_info = system_actions.fetch_info
system_actions.fetch_info = lambda q: f"[MOCK] fetch_info result for: {q}"

# Now import command_handler (which imports system_actions)
import importlib
import command_handler
importlib.reload(command_handler)

test_cases = [
    ("open calculator",         "Should open app (fast router)"),
    ("open netflix",            "Should open website (deterministic)"),
    ("open youtube",            "Should open website (deterministic)"),
    ("pause the video",         "Should toggle play/pause (deterministic)"),
    ("play the video",          "Should toggle play/pause (deterministic)"),
    ("seek forward",            "Should skip forward (deterministic)"),
    ("rewind",                  "Should rewind (deterministic)"),
    ("who is the ceo of apple", "Should web search (deterministic)"),
    ("what is python",          "Should web search (deterministic)"),
    ("hello",                   "Should fall through to LLM"),
]

print("=" * 70)
print("DETERMINISTIC ROUTING INTEGRATION TEST")
print("=" * 70)

for cmd, description in test_cases:
    print(f"\n--- {description} ---")
    print(f"  Command: '{cmd}'")
    try:
        response, pending, meta = command_handler.handle_command(cmd, None)
        print(f"  Response: {response}")
        print(f"  Meta: {meta}")
    except Exception as e:
        print(f"  ERROR: {e}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
