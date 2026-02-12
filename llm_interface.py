from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import json

MODEL_NAME = "microsoft/phi-2"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32
)

SYSTEM_PROMPT = """
You are an AI assistant named Heisenberg.
Convert the user's command into a JSON intent.

Allowed actions:
- open_app
- open_folder

Allowed targets:
- chrome
- vscode
- downloads
- documents
- desktop

Respond ONLY in valid JSON.
Example:
{"action":"open_folder","target":"downloads"}
"""

def interpret(command: str) -> dict:
    prompt = SYSTEM_PROMPT + "\nUser: " + command + "\nIntent:"

    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(
        **inputs,
        max_new_tokens=80,
        do_sample=False,
        temperature=0.0
    )

    text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract JSON safely
    start = text.find("{")
    end = text.find("}") + 1

    try:
        return json.loads(text[start:end])
    except:
        return {"action": "unknown", "target": None}