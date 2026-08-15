"""
LLM Interface Adapter for Heisenberg V2 - Qwen Integration
Delegates model inference to qwen_llm_interface.py
"""

from qwen_llm_interface import interpret

__all__ = ["interpret"]
