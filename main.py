from command_handler import handle_command
from memory_manager import get_state, update_state, add_alias
from voice_interface import listen, speak
from command_normalizer import normalize_command, is_valid_target

USE_VOICE = False  # Set False if you want text-only mode

def main():
    state = get_state()
    pending_confirmation = state.get("pending_confirmation")

    print("Heisenberg is online. Type or speak 'exit' to stop.")

    if state.get("last_action"):
        print(
            f"Heisenberg: Last time I was doing "
            f"{state['last_action']} ({state['last_target']})."
        )

    while True:
        # 🎤 INPUT LAYER (voice or text)
        if USE_VOICE:
            print("Listening...")
            raw_command = listen().lower()
            normalized_command, fuzzy, suggestion = normalize_command(raw_command)

            print(f"Heard: {raw_command}")
            print(f"Normalized: {normalized_command}")

            # Default assignment (IMPORTANT)
            command = normalized_command

            # SYSTEM COMMANDS (bypass AI completely)
            if command.strip() in ("exit", "quit", "stop"):
                print("Heisenberg: Shutting down.")
                break

            # Only ask confirmation if fuzzy match detected
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
                        # Learn only if:
                        # 1. Word changed
                        # 2. Target is valid
                        if w_raw != w_norm and is_valid_target(w_norm):
                            add_alias(w_raw, w_norm)
                            print(f"Heisenberg: Learned that '{w_raw}' means '{w_norm}'")
            print(f"You (voice): {command}")
        else:
            command = input("You: ").strip().lower()
        
        if not command.strip():
            continue

        # 🧠 Core logic (UNCHANGED)
        response, pending_confirmation, meta = handle_command(
            command,
            pending_confirmation
        )

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

if __name__ == "__main__":
    main()