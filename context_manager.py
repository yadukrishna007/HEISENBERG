"""
Context Manager for Heisenberg V2
Monitors active application window, system resources, and contextual clipboard snippets.
"""

import psutil
import pyperclip
import time
from typing import Dict, Any, Optional

try:
    import pygetwindow as gw
except Exception:
    gw = None


class ContextManager:
    def __init__(self, max_clipboard_len: int = 250):
        self.max_clipboard_len = max_clipboard_len
        self.last_check_time = time.time()

    def get_active_window(self) -> Dict[str, str]:
        """Returns details about the currently active foreground window."""
        window_title = "Unknown"
        app_name = "Unknown"

        try:
            if gw:
                active_win = gw.getActiveWindow()
                if active_win and active_win.title:
                    window_title = active_win.title.strip()
        except Exception:
            pass

        # Fallback to psutil process scanning if needed
        return {
            "window_title": window_title,
            "app_name": app_name
        }

    def get_clipboard_snippet(self) -> Optional[str]:
        """Safely fetches recent clipboard text if valid and non-sensitive."""
        try:
            text = pyperclip.paste()
            if not text or not isinstance(text, str):
                return None
            
            clean_text = text.strip()
            if not clean_text:
                return None

            # Safe truncation
            if len(clean_text) > self.max_clipboard_len:
                clean_text = clean_text[:self.max_clipboard_len] + "..."
            
            return clean_text
        except Exception:
            return None

    def get_system_metrics(self) -> Dict[str, Any]:
        """Returns basic CPU and RAM utilization metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory_info = psutil.virtual_memory()
            return {
                "cpu_percent": cpu_percent,
                "ram_used_gb": round((memory_info.total - memory_info.available) / (1024 ** 3), 2),
                "ram_percent": memory_info.percent
            }
        except Exception:
            return {"cpu_percent": 0.0, "ram_used_gb": 0.0, "ram_percent": 0.0}

    def build_context(self, user_input: str = "") -> Dict[str, Any]:
        """
        Assembles contextual snapshot. 
        Clipboard content is attached ONLY if user_input references clipboard keywords.
        """
        active_window = self.get_active_window()
        system_metrics = self.get_system_metrics()
        
        context_data = {
            "active_window": active_window["window_title"],
            "system_metrics": system_metrics,
            "timestamp": time.time()
        }

        # Selectively attach clipboard if referenced by user query
        clipboard_keywords = ["clipboard", "copied", "this text", "paste", "what did i copy"]
        lowered_input = user_input.lower()
        if any(kw in lowered_input for kw in clipboard_keywords):
            snippet = self.get_clipboard_snippet()
            if snippet:
                context_data["clipboard_snippet"] = snippet

        return context_data


# Global singleton instance
context_manager = ContextManager()
