import os
import json
import re
import time
from llama_cpp import Llama

MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "models", "qwen2.5-3b-instruct-q4_k_m.gguf"))

print(f"[Qwen LLM Engine] Initializing llama-cpp model from {MODEL_PATH}...")
_t_init = time.time()
llm = Llama(
    model_path=MODEL_PATH,
    n_gpu_layers=-1,  # Offload all layers to GPU (NVIDIA CUDA)
    n_ctx=2048,
    verbose=False
)
print(f"[Qwen LLM Engine] Initialized in {time.time() - _t_init:.2f}s with CUDA acceleration.")

conversation_history = []

SYSTEM_PROMPT = """You are Heisenberg, an intelligent AI assistant. You must ONLY output a valid JSON object. Do not output any other text or markdown wrappers.

Classify user input into intent_type: "tool_call", "conversation", or "clarification".

RULES & EXAMPLES:
1. Available tools for tool_call:
{"intent_type": "tool_call", "action": "open_app", "target": "chrome"}
{"intent_type": "tool_call", "action": "open_website", "target": "netflix"}
{"intent_type": "tool_call", "action": "open_folder", "target": "downloads"}
{"intent_type": "tool_call", "action": "browser_control", "target": "play_pause"}
{"intent_type": "tool_call", "action": "web_search", "target": "latest tech news"}
{"intent_type": "tool_call", "action": "system_action", "target": "shutdown"}

2. If the user asks a general question, output conversation with response:
{"intent_type": "conversation", "response": "Python is a high-level programming language..."}

3. If input is unclear or ambiguous, output clarification:
{"intent_type": "clarification", "question": "Could you specify which application to open?"}"""



def build_chat_messages(user_input: str):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for turn in conversation_history[-6:]:
        messages.append(turn)
    messages.append({"role": "user", "content": user_input})
    return messages


def generate_qwen_response(user_input: str) -> str:
    messages = build_chat_messages(user_input)
    response = llm.create_chat_completion(
        messages=messages,
        temperature=0.0,
        max_tokens=256
    )
    response_text = response["choices"][0]["message"]["content"].strip()
    return response_text


def parse_json_intent(text: str) -> dict:
    try:
        match = re.search(r"\{[\s\S]*?\}", text)
        if match:
            return json.loads(match.group())
    except Exception:
        pass

    return {
        "intent_type": "conversation",
        "response": text
    }


def interpret(user_input: str) -> dict:
    t0 = time.time()
    raw_response = generate_qwen_response(user_input)
    latency = time.time() - t0
    print(f"[Qwen LLM Engine] Inferred in {latency:.2f}s | Raw: {raw_response[:80]}...")

    conversation_history.append({"role": "user", "content": user_input})
    conversation_history.append({"role": "assistant", "content": raw_response})

    intent = parse_json_intent(raw_response)
    return intent

