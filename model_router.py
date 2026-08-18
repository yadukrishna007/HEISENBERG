"""
Hybrid Model Router for Heisenberg V2 Architecture
Routes user queries to Local Qwen GGUF Model (default, private, low latency)
or Cloud Model (opt-in only for complex multi-turn reasoning when enabled).
"""

from typing import Dict, Any, Optional
from qwen_llm_interface import interpret as local_interpret
from memory_manager import memory_manager


class ModelRouter:
    """Hybrid Model Router evaluating local vs cloud inference."""
    
    def __init__(self, cloud_enabled: bool = False):
        self.cloud_enabled = cloud_enabled

    def interpret(self, user_input: str) -> Dict[str, Any]:
        """Routes user input to local Qwen GGUF engine or cloud fallback."""
        # Check user preferences for cloud opt-in
        pref_cloud = memory_manager.get_preference("cloud_model_enabled", False)
        use_cloud = self.cloud_enabled or pref_cloud

        # Check explicit user query trigger
        if "use cloud" in user_input.lower() or "cloud model" in user_input.lower():
            use_cloud = True

        if use_cloud:
            print("[ModelRouter] Routing query to Cloud Model (Opt-in mode)...")
            return self._cloud_interpret(user_input)
        else:
            # Default private local Qwen model execution
            return local_interpret(user_input)

    def _cloud_interpret(self, user_input: str) -> Dict[str, Any]:
        """Fallback cloud interpretation stub when cloud routing is explicitly enabled."""
        # Clean local fallback if cloud API keys are absent
        print("[ModelRouter] Cloud API key not configured. Falling back to local Qwen engine.")
        return local_interpret(user_input)


# Global singleton instance
model_router = ModelRouter()
