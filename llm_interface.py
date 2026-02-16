from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import json
import re

MODEL_NAME = "microsoft/phi-2"

conversation_history = []


tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32
)

SYSTEM_PROMPT = """
You are Heisenberg, a local AI assistant.

You must classify the user's input into one of these types:

1. tool_call
2. conversation
3. clarification

If tool_call:
Return JSON:
{
  "intent_type": "tool_call",
  "action": "...",
  "target": "..."
}

If conversation:
Return JSON:
{
  "intent_type": "conversation",
  "response": "..."
}

If clarification:
Return JSON:
{
  "intent_type": "clarification",
  "question": "..."
}

Respond ONLY in valid JSON.
"""

def build_prompt(user_input: str):
    history_text = ""

    for turn in conversation_history:
        role = turn["role"]
        content = turn["content"]
        history_text += f"{role.upper()}: {content}\n"

    prompt = (
        SYSTEM_PROMPT +
        "\n\n" +
        history_text +
        f"USER: {user_input}\nASSISTANT:"
    )

    return prompt


def generate_from_model(prompt: str):
    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        outputs = model.generate(
        **inputs,
        max_new_tokens=80,
        temperature=0.0,
        do_sample=False,
        use_cache=True
    )

    response = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    )

    # Extract only new part after ASSISTANT:
    response = response.split("ASSISTANT:")[-1].strip()

    return response

def parse_json(text: str):
    try:
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception:
        pass

    return {
        "intent_type": "conversation",
        "response": "I’m not sure I understood that."
    }


def interpret(user_input: str):

    prompt = build_prompt(user_input)

    raw_response = generate_from_model(prompt)

    conversation_history.append({"role": "user", "content": user_input})
    conversation_history.append({"role": "assistant", "content": raw_response})

    return parse_json(raw_response)