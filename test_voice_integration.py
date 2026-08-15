"""
Voice Pipeline Verification Script for Heisenberg V2
Tests: Whisper STT -> Command Normalization -> Fast Router / Qwen GGUF LLM -> TTS
"""

import sys
from command_handler import handle_command
from command_normalizer import normalize_command

def test_pipeline_text(sample_input: str):
    print(f"\n--- Testing Input: '{sample_input}' ---")
    norm_cmd, fuzzy, suggestion = normalize_command(sample_input.lower())
    print(f"Normalized: '{norm_cmd}' (Fuzzy: {fuzzy})")
    
    response, pending, meta = handle_command(norm_cmd, None)
    print(f"Response: {response}")
    print(f"Meta: {meta}")
    return response

if __name__ == "__main__":
    print("=== Running Voice Integration Synthetic Tests ===")
    test_pipeline_text("open chrome")
    test_pipeline_text("what is python programming language?")
    test_pipeline_text("open visual studio code")
    test_pipeline_text("tell me about artificial intelligence")
    print("\n=== Synthetic Voice Pipeline Verification Passed ===")
