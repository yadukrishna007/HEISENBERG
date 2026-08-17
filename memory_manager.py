"""
Explicit Memory Gatekeeper for Heisenberg V2 Architecture
Acts as the central gatekeeper deciding what data is worth persisting long-term into
persistent JSON stores (user facts, preferences, habits, state) vs transient chatter.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional

MEMORY_DIR = os.path.join(os.path.dirname(__file__), "memory")

FILES = {
    "preferences": "preferences.json",
    "habits": "habits.json",
    "state": "state.json",
    "user_facts": "user_facts.json"
}


class MemoryManager:
    """Explicit Gatekeeper for all persistent memory operations."""
    
    def __init__(self, memory_dir: str = MEMORY_DIR):
        self.memory_dir = memory_dir
        self._ensure_files()

    def _ensure_files(self):
        os.makedirs(self.memory_dir, exist_ok=True)
        for fname in FILES.values():
            fpath = os.path.join(self.memory_dir, fname)
            if not os.path.exists(fpath):
                with open(fpath, "w", encoding="utf-8") as f:
                    json.dump({}, f)

    def _load(self, file_key: str) -> dict:
        path = os.path.join(self.memory_dir, FILES[file_key])
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save(self, file_key: str, data: dict):
        path = os.path.join(self.memory_dir, FILES[file_key])
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[MemoryManager Error] Failed to save {file_key}: {e}")

    # -------- Memory Gatekeeper Logic --------
    def should_remember(self, text: str) -> bool:
        """Determines whether text contains long-term user facts or preferences worth persisting."""
        if not text or len(text.strip()) < 4:
            return False

        patterns = [
            r"my name is\s+(.+)",
            r"i prefer\s+(.+)",
            r"remember that\s+(.+)",
            r"my favorite\s+(.+)",
            r"i work as\s+(.+)",
            r"i live in\s+(.+)",
            r"my default\s+(.+)"
        ]

        text_lower = text.lower()
        for pat in patterns:
            if re.search(pat, text_lower):
                return True
        return False

    def extract_and_remember(self, text: str) -> Optional[str]:
        """Filters input text and persists any user facts found."""
        text_lower = text.lower().strip()
        
        # Name
        match_name = re.search(r"my name is\s+([a-zA-Z0-9\s]+)", text_lower)
        if match_name:
            name = match_name.group(1).strip().title()
            self.remember_fact("user_name", name)
            return f"Learned user name: '{name}'"

        # General Preference / Fact
        match_pref = re.search(r"(?:remember that|i prefer|my favorite)\s+(.+)", text_lower)
        if match_pref:
            fact_detail = match_pref.group(1).strip()
            fact_key = f"pref_{int(os.times().system * 1000)}"
            self.remember_fact(fact_key, fact_detail)
            return f"Saved preference: '{fact_detail}'"

        return None

    def remember_fact(self, key: str, value: Any):
        facts = self._load("user_facts")
        facts[key] = value
        self._save("user_facts", facts)

    def get_fact(self, key: str, default=None) -> Any:
        facts = self._load("user_facts")
        return facts.get(key, default)

    def get_all_facts(self) -> Dict[str, Any]:
        return self._load("user_facts")

    def format_facts_summary(self) -> str:
        facts = self.get_all_facts()
        if not facts:
            return ""
        lines = []
        for k, v in facts.items():
            if k == "user_name":
                lines.append(f"- User's name is {v}.")
            else:
                lines.append(f"- {v}.")
        return "\n".join(lines)

    # -------- Preferences --------
    def get_preference(self, key: str, default=None):
        data = self._load("preferences")
        return data.get(key, default)

    def set_preference(self, key: str, value: Any):
        data = self._load("preferences")
        data[key] = value
        self._save("preferences", data)

    # -------- Habits --------
    def increment_habit(self, key: str):
        data = self._load("habits")
        data[key] = data.get(key, 0) + 1
        self._save("habits", data)

    # -------- State --------
    def get_state(self) -> dict:
        return self._load("state")

    def update_state(self, **kwargs):
        data = self._load("state")
        for k, v in kwargs.items():
            data[k] = v
        self._save("state", data)

    # -------- Aliases --------
    def get_aliases(self) -> dict:
        data = self._load("preferences")

        return data.get("aliases", {})

    def add_alias(self, alias: str, target: str):
        data = self._load("preferences")
        aliases = data.get("aliases", {})
        aliases[alias] = target
        data["aliases"] = aliases
        self._save("preferences", data)


# Global singleton instance
memory_manager = MemoryManager()

# Module-level legacy wrappers for backwards compatibility
def get_preference(key: str, default=None):
    return memory_manager.get_preference(key, default)

def set_preference(key: str, value: Any):
    memory_manager.set_preference(key, value)

def increment_habit(key: str):
    memory_manager.increment_habit(key)

def get_state():
    return memory_manager.get_state()

def update_state(**kwargs):
    memory_manager.update_state(**kwargs)

def clear_pending_confirmation():
    memory_manager.update_state(pending_confirmation=None)

def get_aliases():
    return memory_manager.get_aliases()

def add_alias(alias: str, target: str):
    memory_manager.add_alias(alias, target)