import os
import time
import json
import re
from llama_cpp import Llama

MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "models", "qwen2.5-3b-instruct-q4_k_m.gguf"))

def run_standalone_tests():
    print(f"--- Loading model: {MODEL_PATH} ---")
    start_time = time.time()
    
    llm = Llama(
        model_path=MODEL_PATH,
        n_gpu_layers=-1,  # Full GPU offload
        n_ctx=2048,
        verbose=False
    )
    
    print(f"Model loaded in {time.time() - start_time:.2f} seconds.")
    
    # ------------------ TEST 1: Basic Conversation ------------------
    print("\n--- Test 1: Basic Conversation ---")
    messages = [
        {"role": "system", "content": "You are Heisenberg, an intelligent AI assistant."},
        {"role": "user", "content": "Hello. Who are you?"}
    ]
    t0 = time.time()
    res = llm.create_chat_completion(messages=messages, temperature=0.0, max_tokens=100)
    response1 = res["choices"][0]["message"]["content"]
    print(f"Response ({time.time() - t0:.2f}s):\n{response1}")
    
    # ------------------ TEST 2: General Knowledge ------------------
    print("\n--- Test 2: General Knowledge ---")
    messages = [
        {"role": "user", "content": "Explain what Python is in two sentences."}
    ]
    t0 = time.time()
    res = llm.create_chat_completion(messages=messages, temperature=0.0, max_tokens=100)
    response2 = res["choices"][0]["message"]["content"]
    print(f"Response ({time.time() - t0:.2f}s):\n{response2}")

    # ------------------ TEST 3: Structured Tool Call ------------------
    print("\n--- Test 3: Structured Tool Call ---")
    system_prompt = """You are Heisenberg. Output ONLY a valid JSON object.
Rules:
- If user wants to open an application or site, output {"intent_type": "tool_call", "action": "open_app", "target": "<target>"}
- If user asks a general question, output {"intent_type": "conversation", "response": "<answer>"}
- Otherwise output {"intent_type": "clarification", "question": "<question>"}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Open Visual Studio Code"}
    ]
    t0 = time.time()
    res = llm.create_chat_completion(messages=messages, temperature=0.0, max_tokens=100)
    response3 = res["choices"][0]["message"]["content"]
    print(f"Response ({time.time() - t0:.2f}s):\n{response3}")

if __name__ == "__main__":
    run_standalone_tests()

