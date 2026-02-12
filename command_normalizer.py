from difflib import get_close_matches
from memory_manager import get_aliases

KNOWN_TARGETS = {
    "chrome": ["chrome"],
    "vscode": ["vscode", "vs code"],
    "downloads": ["downloads", "download"],
    "desktop": ["desktop"],
    "documents": ["documents", "document"]
}

def is_valid_target(target):
    return target in KNOWN_TARGETS

def normalize_command(text: str):
    words = text.split()
    normalized_words = []
    fuzzy_detected = False
    suggestion = None

    learned_aliases = get_aliases()

    for word in words:

        # 1️⃣ Check learned aliases first
        if word in learned_aliases:
            normalized_words.append(learned_aliases[word])
            continue

        matched = False

        for target, variants in KNOWN_TARGETS.items():

            if word in variants:
                normalized_words.append(target)
                matched = True
                break

            matches = get_close_matches(word, variants, n=1, cutoff=0.75)
            if matches:
                normalized_words.append(target)
                fuzzy_detected = True
                suggestion = target
                matched = True
                break

        if not matched:
            normalized_words.append(word)

    return " ".join(normalized_words), fuzzy_detected, suggestion