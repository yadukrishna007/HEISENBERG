# HEISENBERG – Personal Offline AI Assistant

## What is this?

Heisenberg is a personal local AI assistant inspired by JARVIS/FRIDAY.
The goal is to build an AI that runs completely on your computer, understands you, remembers things, and can control your system — without paid APIs or cloud dependency.

Heisenberg can **control your computer, browse the web, answer questions, play/pause videos, and hold basic conversations** — all locally.

---

## What it can do

### 🖥️ App Launching
- Open any installed app by name — *"open calculator"*, *"open spotify"*
- Auto-discovers installed apps from Windows Start Menu shortcuts
- Built-in fallbacks for common UWP/system apps (`calc.exe`, `notepad.exe`, etc.)

### 🌐 Website Navigation
- Open websites directly — *"open netflix"*, *"open youtube"*
- Handles URLs, domain names, and Google searches automatically
- Supports 14+ popular sites with instant deterministic routing

### 🎬 Media Controls
- *"pause the video"* / *"play the video"* → toggles play/pause
- *"seek forward"* / *"fast forward"* / *"skip"* → skips ahead
- *"rewind"* / *"go back"* → seeks backward
- Works on any focused browser tab (YouTube, Netflix, etc.)

### 🔍 Web Search & Knowledge
- *"who is the CEO of Apple?"* → fetches answer from Wikipedia
- *"what is quantum computing?"* → instant factual lookup
- Falls back to DuckDuckGo scraping when Wikipedia doesn't have a match

### 💬 Conversation & Coding
- *"write a python script for a countdown timer"* → generates code
- *"hello"* → casual conversation
- Powered by TinyLlama 1.1B running locally

### 📂 Folder Navigation
- *"open downloads"* / *"open documents"* / *"open desktop"*

### 🎤 Voice Interface
- Voice input via Vosk (local STT, no cloud)
- Text-to-speech response output
- Learns misheard words permanently (*"gram"* → *"chrome"*)

### 🔒 Safety
- Confirmation prompts for dangerous actions (e.g., shutdown)
- Intent validation against allowed actions registry
- Memory persistence across restarts

---

## Architecture

```
Voice/Text Input
       │
       ▼
 ┌─────────────┐
 │  Normalizer │  ← alias correction, fuzzy matching
 └──────┬──────┘
        ▼
 ┌───────────────────────┐
 │   Deterministic       │  ← keyword matching (instant, no AI)
 │   Router              │
 │                       │
 │  • "open X" → app/web │
 │  • "pause" → media    │
 │  • "who/what" → search│
 └──────┬────────────────┘
        │ (only if no match)
        ▼
 ┌──────────────┐
 │  TinyLlama   │  ← local LLM for conversation/coding
 │  1.1B (CPU)  │
 └──────┬───────┘
        ▼
 ┌──────────────┐
 │  Executor    │  ← validated system actions
 └──────┬───────┘
        ▼
   Response + Memory Save
```

---

## File Structure

| File | Purpose |
|---|---|
| `main.py` | Entry point — voice/text loop |
| `command_handler.py` | Routing logic (deterministic + AI fallback) |
| `llm_interface.py` | TinyLlama integration with JSON intent parsing |
| `system_actions.py` | App launching, website opening, media controls, web search |
| `intent_schema.py` | Allowed actions & intent validation |
| `tools_registry.py` | Tool definitions for the LLM |
| `voice_interface.py` | Vosk STT + TTS output |
| `command_normalizer.py` | Alias correction & fuzzy matching |
| `memory_manager.py` | Persistent state & habit tracking |
| `sensitive_actions.py` | Actions requiring confirmation |

---

## Setup

```bash
git clone <repo>
cd HEISENBERG
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Dependencies
- `torch` + `transformers` (TinyLlama)
- `vosk` (offline speech recognition)
- `pyautogui` (media key simulation)
- `requests` + `beautifulsoup4` (web scraping)
- `wikipedia` (knowledge lookup)
- `pyttsx3` (text-to-speech)

> **Note**: Set `USE_VOICE = True` in `main.py` to enable voice mode, or `False` for text-only.

---

## Example Usage

```
You: open calculator
Heisenberg: Opened app: calculator

You: open netflix
Heisenberg: Opening netflix in your browser.

You: pause the video
Heisenberg: Toggled play/pause.

You: who is the ceo of apple
Heisenberg: Here's what I found: Tim Cook is an American businessman...

You: write a python hello world
Heisenberg: Here is a python script: print("Hello, World!")
```

---

## Roadmap

- [x] Phase 1 — System control (apps, folders)
- [x] Phase 2 — Web browsing, media controls, web search, conversation
- [ ] Phase 3 — Multi-turn context, smarter dialogue
- [ ] Phase 4 — Task automation & scheduling
- [ ] Phase 5 — Custom wake word & always-on mode
