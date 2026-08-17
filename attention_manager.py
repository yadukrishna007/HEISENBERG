"""
Attention Manager for Heisenberg V2
Determines whether incoming events/requests should interrupt immediately, queue for later, or be suppressed.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
import time


class EventPriority(Enum):
    URGENT = 1
    NORMAL = 2
    BACKGROUND = 3


class ActionDecision(Enum):
    INTERRUPT_NOW = "INTERRUPT_NOW"
    QUEUE = "QUEUE"
    SUPPRESS = "SUPPRESS"


class AttentionManager:
    def __init__(self):
        self.is_busy = False
        self.queue: List[Dict[str, Any]] = []

    def set_busy_state(self, busy: bool):
        """Sets whether the agent is currently engaged in active execution."""
        self.is_busy = busy

    def evaluate_event(self, source: str, event_type: str, priority: EventPriority, payload: Dict[str, Any]) -> ActionDecision:
        """
        Evaluates an incoming trigger (user or system) to decide immediate handling.
        """
        # User input always interrupts immediately
        if source.lower() in ("user", "voice", "text", "cli"):
            return ActionDecision.INTERRUPT_NOW

        # Urgent system events interrupt immediately
        if priority == EventPriority.URGENT:
            return ActionDecision.INTERRUPT_NOW

        # If user/agent is currently busy, queue normal/background events
        if self.is_busy:
            if priority == EventPriority.NORMAL:
                self.queue_event(source, event_type, payload)
                return ActionDecision.QUEUE
            else:
                # Low priority background noise suppressed while busy
                return ActionDecision.SUPPRESS

        # If idle, queue or interrupt based on priority
        if priority == EventPriority.BACKGROUND:
            return ActionDecision.SUPPRESS

        return ActionDecision.INTERRUPT_NOW

    def queue_event(self, source: str, event_type: str, payload: Dict[str, Any]):
        """Pushes an event into the background queue."""
        self.queue.append({
            "source": source,
            "event_type": event_type,
            "payload": payload,
            "timestamp": time.time()
        })

    def drain_queue(self) -> List[Dict[str, Any]]:
        """Returns and flushes all queued background events."""
        events = list(self.queue)
        self.queue.clear()
        return events


# Global singleton instance
attention_manager = AttentionManager()
