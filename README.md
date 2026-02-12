# HEISENBERG – Personal Offline AI Assistant (Checkpoint)

## What is this?

Heisenberg is my personal local AI assistant inspired by JARVIS/FRIDAY.
The goal is to build an AI that runs completely on my computer, understands me, remembers things, and can control my system — without paid APIs or cloud dependency.

At this stage, Heisenberg is an **AI‑powered computer controller** — not yet a fully conversational assistant.

---

## What it can do right now

* Open apps (Chrome, VSCode, etc.)
* Open folders (Downloads, Desktop, etc.)
* Understand voice commands (Whisper local STT)
* Interpret natural language commands using a local LLM (Phi‑2)
* Ask confirmation for dangerous actions
* Remember last actions even after restart
* Learn misheard words permanently ("gram" → "chrome")

You can talk or type — both work.

---

## How it works (simple)

1. You speak or type
2. Voice → text (if mic used)
3. Text cleaned + alias corrected
4. Known commands handled directly
5. Unknown commands interpreted by AI
6. Safe system action executed
7. Memory saved

---

## Run it

```bash
git clone <repo>
cd HEISENBERG
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

(Download Whisper + Phi‑2 locally before running)

---

## Current Limitation

Heisenberg does NOT truly "talk" yet.

Right now:

> It understands instructions

But it does NOT yet:

* hold conversations
* explain things logically
* maintain chat context

Every sentence is treated as a task.

---

## Next Step

We now teach Heisenberg the difference between:
**a command** vs **a conversation**

That is where it becomes a real assistant instead of just an automation tool.
