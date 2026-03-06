from llm_interface import interpret

queries = [
    "open netflix",
    "pause the video",
    "who is the ceo of apple?",
    "write a python script for a countdown timer"
]

for q in queries:
    print(f"\n--- {q} ---")
    res = interpret(q)
    print(f"PARSED JSON FOR '{q}':", res)
