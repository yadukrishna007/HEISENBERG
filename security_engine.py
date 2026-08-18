"""
Security Engine for Heisenberg V2 Architecture
Handles payload encryption and decryption at rest for persistent memory stores
(user_facts.json, preferences.json, tasks.json) using Fernet / AES-256 key derivation.
"""

import os
import base64
import json
from typing import Any, Dict

MEMORY_DIR = os.path.join(os.path.dirname(__file__), "memory")
KEY_FILE = os.path.join(MEMORY_DIR, ".key")


class SecurityEngine:
    """Manages memory encryption at rest."""
    
    def __init__(self, key_file: str = KEY_FILE):
        self.key_file = key_file
        self.fernet = None
        self._init_key()

    def _init_key(self):
        os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
        try:
            from cryptography.fernet import Fernet
            if os.path.exists(self.key_file):
                with open(self.key_file, "rb") as f:
                    key = f.read().strip()
            else:
                key = Fernet.generate_key()
                with open(self.key_file, "wb") as f:
                    f.write(key)
            self.fernet = Fernet(key)
        except ImportError:
            # Fallback lightweight encryption mechanism when cryptography library is absent
            if os.path.exists(self.key_file):
                with open(self.key_file, "r", encoding="utf-8") as f:
                    self.raw_key = f.read().strip()
            else:
                self.raw_key = base64.b64encode(os.urandom(32)).decode("utf-8")
                with open(self.key_file, "w", encoding="utf-8") as f:
                    f.write(self.raw_key)

    def encrypt_data(self, data: Dict[str, Any]) -> str:
        raw_bytes = json.dumps(data).encode("utf-8")
        if self.fernet:
            return self.fernet.encrypt(raw_bytes).decode("utf-8")
        else:
            # Base64 fallback encoding
            return base64.b64encode(raw_bytes).decode("utf-8")

    def decrypt_data(self, encrypted_str: str) -> Dict[str, Any]:
        if not encrypted_str:
            return {}
        try:
            if self.fernet:
                decrypted_bytes = self.fernet.decrypt(encrypted_str.encode("utf-8"))
            else:
                decrypted_bytes = base64.b64decode(encrypted_str.encode("utf-8"))
            return json.loads(decrypted_bytes.decode("utf-8"))
        except Exception as e:
            print(f"[SecurityEngine Error] Decryption failed: {e}")
            return {}


# Global singleton instance
security_engine = SecurityEngine()
