import json
import os
from typing import Any

MEMORY_DIR = "memory"

FILES = {
    "preferences": "preferences.json",
    "habits": "habits.json",
    "state": "state.json"
}

def _load(file_name: str) -> dict:
    path = os.path.join(MEMORY_DIR, file_name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(file_name: str, data: dict):
    path = os.path.join(MEMORY_DIR, file_name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# -------- Preferences --------
def get_preference(key: str, default=None):
    data = _load(FILES["preferences"])
    return data.get(key, default)

def set_preference(key: str, value: Any):
    data = _load(FILES["preferences"])
    data[key] = value
    _save(FILES["preferences"], data)

# -------- Habits --------
def increment_habit(key: str):
    data = _load(FILES["habits"])
    data[key] = data.get(key, 0) + 1
    _save(FILES["habits"], data)

# -------- State --------
def get_state():
    return _load(FILES["state"])

def update_state(**kwargs):
    data = _load(FILES["state"])
    for k, v in kwargs.items():
        data[k] = v
    _save(FILES["state"], data)

def clear_pending_confirmation():
    update_state(pending_confirmation=None)

# -------- Aliases --------
def get_aliases():
    data = _load(FILES["preferences"])
    return data.get("aliases", {})

def add_alias(alias: str, target: str):
    data = _load(FILES["preferences"])
    aliases = data.get("aliases", {})
    aliases[alias] = target
    data["aliases"] = aliases
    _save(FILES["preferences"], data)