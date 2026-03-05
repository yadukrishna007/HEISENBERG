from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import json
import re

MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

device = "cpu"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32
).to(device)

conversation_history = []

SYSTEM_PROMPT = """
You are Heisenberg, a local AI personal assistant.

You must classify user input into ONE of the following:

1. tool_call
2. conversation
3. clarification

If tool_call, respond ONLY in JSON:
{
  "intent_type": "tool_call",
  "action": "...",
  "target": "..."
}

If conversation:
{
  "intent_type": "conversation",
  "response": "..."
}

If clarification:
{
  "intent_type": "clarification",
  "question": "..."
}

If the user input is unclear, meaningless, or appears to be speech recognition noise,
respond with:

{
  "intent_type": "clarification",
  "question": "I didn't quite catch that. Could you repeat?"
}


Keep responses short, natural, and concise like a voice assistant.
Avoid long explanations unless asked.


Do not add explanations outside JSON.
"""


# ---------- Prompt Builder ----------
def build_prompt(user_input):

    history_text = ""

    for turn in conversation_history[-6:]:
        role = turn["role"]
        content = turn["content"]
        history_text += f"<|{role}|>\n{content}\n"

    prompt = (
        f"<|system|>\n{SYSTEM_PROMPT}\n"
        f"{history_text}"
        f"<|user|>\n{user_input}\n"
        f"<|assistant|>\n"
    )

    return prompt


# ---------- Model Generation ----------
def generate_from_model(prompt):

    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=120,
            do_sample=False,
            temperature=0.0,
            use_cache=True,
            pad_token_id=tokenizer.eos_token_id
        )

    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)

    response = decoded.split("<|assistant|>")[-1].strip()

    return response


# ---------- JSON Parsing ----------
def parse_json(text):

    try:
        match = re.search(r"\{[\s\S]*?\}", text)
        if match:
            return json.loads(match.group())
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
