from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import json
import re
from transformers import StoppingCriteria, StoppingCriteriaList

MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

device = "cpu"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32
).to(device)

conversation_history = []

SYSTEM_PROMPT = """
You are a helpful AI assistant. You must ONLY output a valid JSON object. Do not output any other text.

Classify the user input into an intent_type: "tool_call", "conversation", or "clarification".

RULES:
1. If the user asks you to open something, or control a video, or search the web, use "tool_call".
{"intent_type": "tool_call", "action": "open_website", "target": "netflix"}
{"intent_type": "tool_call", "action": "browser_play_pause", "target": "video"}
{"intent_type": "tool_call", "action": "web_search", "target": "ceo of apple"}

2. If the user asks you a general question or asks you to write code, use "conversation". Put your answer in "response". Use \n for newlines.
{"intent_type": "conversation", "response": "Here is the code..."}

3. If the input is random noise, use "clarification".
{"intent_type": "clarification", "question": "Pardon?"}
"""


# ---------- Prompt Builder ----------
def build_prompt(user_input):

    history_text = ""

    for turn in conversation_history[-6:]:
        role = turn["role"]
        content = turn["content"]
        history_text += f"<|{role}|>\n{content}</s>\n"

    prompt = (
        f"<|system|>\n{SYSTEM_PROMPT}</s>\n"
        f"{history_text}"
        f"<|user|>\n{user_input}</s>\n"
        f"<|assistant|>\n"
    )

    return prompt


# ---------- Stopping Criteria ----------
class JsonStoppingCriteria(StoppingCriteria):
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        decoded = self.tokenizer.decode(input_ids[0])
        # Force stop generation if we hit the closing brace.
        if "}" in decoded.split("<|assistant|>")[-1]:
            return True
        return False

# ---------- Model Generation ----------
def generate_from_model(prompt):

    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    stopping_criteria = StoppingCriteriaList([JsonStoppingCriteria(tokenizer)])

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=500,
            do_sample=False,
            temperature=0.0,
            use_cache=True,
            stopping_criteria=stopping_criteria,
            pad_token_id=tokenizer.eos_token_id
        )

    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)

    response = decoded.split("<|assistant|>")[-1].strip()

    return response


# ---------- JSON Parsing ----------
def parse_json(text):

    try:
        # Match only the VERY FIRST JSON object
        match = re.search(r"\{[\s\S]*?\}", text)
        if match:
            obj = json.loads(match.group())
            return obj
    except Exception:
        pass

    # fallback → treat as conversation
    return {
        "intent_type": "conversation",
        "response": text.strip()
    }


# ---------- Main Interface ----------
def interpret(user_input: str):

    prompt = build_prompt(user_input)

    raw_response = generate_from_model(prompt)

    print("RAW MODEL OUTPUT:\n", raw_response)

    conversation_history.append(
        {"role": "user", "content": user_input}
    )
    conversation_history.append(
        {"role": "assistant", "content": raw_response}
    )

    return parse_json(raw_response)
