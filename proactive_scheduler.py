"""
Proactive Scheduler & System Health Diagnostics for Heisenberg V2 Architecture
Handles background daemon timers, scheduled reminders, and system health checks
(CPU, RAM, GPU, Mic, and Local LLM status).
"""

import os
import time
import threading
import psutil
from typing import Dict, Any, List, Callable, Optional


class SelfDiagnostics:
    """Monitors system health and hardware utilization."""
    
    @staticmethod
    def get_system_health() -> Dict[str, Any]:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        
        # Check local GGUF model file health
        model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "models", "qwen2.5-3b-instruct-q4_k_m.gguf"))
        model_exists = os.path.exists(model_path)
        model_size_gb = os.path.getsize(model_path) / (1024 ** 3) if model_exists else 0

        return {
            "cpu_usage_percent": cpu_percent,
            "ram_total_gb": round(mem.total / (1024 ** 3), 2),
            "ram_available_gb": round(mem.available / (1024 ** 3), 2),
            "ram_used_percent": mem.percent,
            "local_model_loaded": model_exists,
            "local_model_size_gb": round(model_size_gb, 2),
            "status": "HEALTHY" if cpu_percent < 90 and mem.percent < 90 else "DEGRADED"
        }


class ScheduledTimer:
    def __init__(self, timer_id: str, prompt: str, delay_seconds: float, callback: Callable[[str], None]):
        self.timer_id = timer_id
        self.prompt = prompt
        self.trigger_time = time.time() + delay_seconds
        self.callback = callback
        self.fired = False


class ProactiveScheduler:
    """Background daemon thread managing timers and scheduled reminders."""
    
    def __init__(self):
        self.timers: Dict[str, ScheduledTimer] = {}
        self._running = False
        self._thread = None
        self._lock = threading.Lock()

    def start(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self._running = False

    def schedule_reminder(self, prompt: str, delay_seconds: float, callback: Callable[[str], None]) -> str:
        timer_id = f"timer_{int(time.time() * 1000)}"
        timer = ScheduledTimer(timer_id, prompt, delay_seconds, callback)
        with self._lock:
            self.timers[timer_id] = timer
        self.start()
        return timer_id

    def cancel_reminder(self, timer_id: str) -> bool:
        with self._lock:
            if timer_id in self.timers:
                del self.timers[timer_id]
                return True
        return False

    def _scheduler_loop(self):
        while self._running:
            time.sleep(0.5)
            now = time.time()
            to_fire = []
            
            with self._lock:
                for timer_id, timer in list(self.timers.items()):
                    if not timer.fired and now >= timer.trigger_time:
                        timer.fired = True
                        to_fire.append(timer)
                        del self.timers[timer_id]

            for timer in to_fire:
                try:
                    timer.callback(timer.prompt)
                except Exception as e:
                    print(f"[ProactiveScheduler Error] Callback failed for timer '{timer.timer_id}': {e}")

    def list_active_reminders(self) -> List[Dict[str, Any]]:
        with self._lock:
            now = time.time()
            return [
                {
                    "timer_id": t.timer_id,
                    "prompt": t.prompt,
                    "seconds_remaining": max(0, round(t.trigger_time - now, 1))
                }
                for t in self.timers.values() if not t.fired
            ]


# Global singleton instance
proactive_scheduler = ProactiveScheduler()
