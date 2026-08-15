# Heisenberg V2 — Qwen3.5-4B Q4 Setup, Integration & Testing

## 0. Purpose

This document is the controlled migration plan for replacing the current conversational LLM in Heisenberg V1 with a quantized **Qwen3.5-4B** model.

The goal is to complete the model migration and verify the existing assistant still works **before implementing the rest of the Heisenberg V2 architecture**.

### Target flow

```text
Voice / Text
     ↓
Whisper / Input
     ↓
Normalization
     ↓
Heisenberg LLM
     ↓
Conversation / Tool Decision
     ↓
Existing Command + Tool Execution
```

---

# 1. Current Baseline

Before changing anything, confirm that the current V1 works.

### Existing V1 capabilities

- [ ] Whisper speech-to-text works
- [ ] Dynamic voice listening works
- [ ] Speech normalization works
- [ ] Alias learning works
- [ ] `open chrome` works
- [ ] `open vscode` works
- [ ] Folder opening works
- [ ] Sensitive-action confirmation works
- [ ] Persistent memory works
- [ ] Basic LLM conversation works
- [ ] `exit` / `quit` works
- [ ] Existing project launches from the current virtual environment

### Important rule

Do **not** modify or delete the working V1 implementation until the new model has passed standalone testing.

Create a Git checkpoint first:

```powershell
git status
git add .
git commit -m "V1 stable baseline before Qwen3.5 integration"
```

---

# 2. Hardware & System Requirements

The exact Q4 runtime and model format should be selected **after checking the machine**.

Run these commands from PowerShell.

## 2.1 RAM

```powershell
Get-CimInstance Win32_ComputerSystem |
Select-Object TotalPhysicalMemory
```

Convert bytes to GB if necessary.

Also check current memory usage:

```powershell
Get-CimInstance Win32_OperatingSystem |
Select-Object TotalVisibleMemorySize,FreePhysicalMemory
```

### Record

```text
RAM:
Available RAM:
```

---

## 2.2 CPU

```powershell
Get-CimInstance Win32_Processor |
Select-Object Name,NumberOfCores,NumberOfLogicalProcessors
```

### Record

```text
CPU:
Physical cores:
Logical processors:
```

---

## 2.3 GPU

```powershell
Get-CimInstance Win32_VideoController |
Select-Object Name,AdapterRAM
```

If NVIDIA is installed, also run:

```powershell
nvidia-smi
```

If `nvidia-smi` is not recognized, that is acceptable.

### Record

```text
GPU:
VRAM:
CUDA available: Yes / No
```

---

## 2.4 Disk Space

Check the drive containing the model and Hugging Face cache:

```powershell
Get-PSDrive C
```

Also:

```powershell
Get-ChildItem "$env:USERPROFILE\.cache\huggingface" -Force -ErrorAction SilentlyContinue
```

### Record

```text
Free disk:
Hugging Face cache size:
```

---

## 2.5 Python

From the Heisenberg directory:

```powershell
python --version
```

Then:

```powershell
where python
```

Confirm that Python is coming from the project's virtual environment.

Expected style:

```text
C:\Users\<user>\Desktop\HEISENBERG\venv\Scripts\python.exe
```

---

## 2.6 Current environment

Activate the environment if necessary:

```powershell
.\venv\Scripts\Activate.ps1
```

Then:

```powershell
pip list
```

Record the important packages currently being used.

---

# 3. Choose the Q4 Model Format

## Important

Do not automatically download the full Transformers model.

The full Qwen3.5-4B repository is significantly larger than a Q4 quantized model.

For a laptop-focused local assistant, the preferred direction is a **4-bit quantized model**.

Possible runtimes include:

- llama.cpp
- Ollama
- LM Studio
- another compatible local inference runtime

The final runtime should be chosen based on the hardware results from Section 2.

### Selection criteria

Prioritize:

1. Low latency
2. Low RAM/VRAM consumption
3. Good instruction following
4. Reliable structured/tool output
5. Python integration
6. Local/offline operation
7. Easy model management
8. Future compatibility with agent tooling

### Decision

```text
Selected runtime:
Selected model repository:
Selected quantization:
Model file:
```

Do not proceed until these are recorded.

---

# 4. Create a Safe V2 Branch

From the repository root:

```powershell
git checkout -b v2-qwen35-integration
```

Confirm:

```powershell
git branch
```

Expected:

```text
* v2-qwen35-integration
  main
```

---

# 5. Install the Selected Runtime

Use the installation instructions appropriate to the selected runtime.

Examples:

### If using llama.cpp

Install/download a Windows build appropriate for the machine, then verify:

```powershell
llama-cli --version
```

or the executable's equivalent.

### If using Ollama

Verify:

```powershell
ollama --version
```

Then verify the service is available:

```powershell
ollama list
```

### If using another runtime

Record the exact runtime and version here:

```text
Runtime:
Version:
```

---

# 6. Download Qwen3.5-4B Q4

Download only the selected quantized model.

Do not duplicate the model unnecessarily between:

- Hugging Face cache
- project directory
- runtime-specific model directory

Choose one authoritative model location.

Record:

```text
Model:
Quantization:
File size:
Location:
Checksum/hash if available:
```

### Disk-space check

Before downloading:

```powershell
Get-PSDrive C
```

Make sure there is enough space for:

- model
- runtime
- temporary download files
- existing Whisper models
- Hugging Face cache
- Heisenberg data

---

# 7. Standalone Model Test

**Do this before integrating with Heisenberg.**

The objective is to prove:

```text
Qwen3.5
    ↓
Local inference
    ↓
Response
```

without Whisper, memory, command handling, or browser automation.

### Test 1 — Basic conversation

Input:

```text
Hello. Who are you?
```

Expected:

- coherent response
- no obvious prompt leakage
- no repeated unrelated content

Result:

```text
PASS / FAIL
```

---

### Test 2 — General knowledge

Input:

```text
Explain what Python is in two sentences.
```

Result:

```text
PASS / FAIL
```

---

### Test 3 — Instruction following

Input:

```text
Give me exactly three benefits of using Git.
```

Result:

```text
PASS / FAIL
```

---

### Test 4 — Context

Input:

```text
My favorite editor is VS Code.
```

Then:

```text
What is my favorite editor?
```

Result:

```text
PASS / FAIL
```

---

### Test 5 — Short conversational input

Test:

```text
Hi.
How are you?
Thanks.
Okay.
```

The model should not drift into unrelated scenarios.

Result:

```text
PASS / FAIL
```

---

# 8. Structured Tool-Call Test

Before connecting real tools, test whether the model can produce the expected structured decision.

Example instruction:

```text
You have access to a tool named open_app.
The tool accepts a target.

User:
Open Chrome.
```

Expected conceptual output:

```json
{
  "action": "open_app",
  "target": "chrome"
}
```

The exact format depends on the selected runtime/model integration.

### Test invalid request

Input:

```text
Open an application that does not exist.
```

Expected:

- clarification
- refusal
- or another safe non-execution response

It must not invent an executable path.

Result:

```text
PASS / FAIL
```

---

# 9. Heisenberg LLM Interface

Only after the standalone tests pass should the model be connected to Heisenberg.

Current interface:

```text
llm_interface.py
```

The new interface should provide a stable function such as:

```python
interpret(user_input)
```

The rest of Heisenberg should not need to know:

- which model is running
- where the model is stored
- which runtime is being used
- whether inference is CPU or GPU
- how tokens are generated

### Desired separation

```text
command_handler.py
        ↓
   interpret()
        ↓
llm_interface.py
        ↓
Qwen3.5 runtime
```

This allows the model to be replaced later without rewriting the command system.

---

# 10. Agent Output Contract

Do not allow arbitrary model output to directly execute system commands.

The model should return a validated decision.

Conceptually:

### Conversation

```json
{
  "type": "conversation",
  "response": "Hello."
}
```

### Tool call

```json
{
  "type": "tool_call",
  "tool": "open_app",
  "arguments": {
    "target": "chrome"
  }
}
```

### Clarification

```json
{
  "type": "clarification",
  "question": "Which application should I open?"
}
```

The exact schema may be refined during implementation.

---

# 11. Connect to Existing Command Handler

The existing deterministic path should remain.

This is important for latency.

### Desired routing

```text
User input
    ↓
Normalization
    ↓
Fast deterministic check
    │
    ├── Known safe command
    │       ↓
    │    Execute immediately
    │
    └── Otherwise
            ↓
          Qwen3.5
            ↓
       AI decision
```

Therefore:

```text
open chrome
```

should not require a full LLM generation if the deterministic command path already understands it.

But:

```text
What is the difference between Django and Flask?
```

should go to the LLM.

And:

```text
Search the web for the latest Django release.
```

will eventually become a tool call.

---

# 12. Voice Integration Test

After text integration works, test:

```text
Microphone
    ↓
VAD
    ↓
Whisper
    ↓
Normalization
    ↓
Qwen3.5
    ↓
Response
```

### Test

Say:

```text
Hello Heisenberg.
```

Then:

```text
How are you?
```

Then:

```text
What is machine learning?
```

Check:

- [ ] Whisper transcribes correctly
- [ ] empty audio is ignored
- [ ] LLM receives correct text
- [ ] response is coherent
- [ ] TTS speaks response
- [ ] no crash occurs between turns

---

# 13. Existing Command Regression Test

The new model must not break V1.

Test:

```text
open chrome
open vscode
open downloads
open documents
open desktop
```

Expected:

```text
Correct target opens
```

Also test aliases learned previously.

---

# 14. Safety Regression Test

Test a sensitive command such as:

```text
shutdown the computer
```

Expected:

```text
This action requires confirmation.
```

Then:

```text
no
```

Expected:

```text
Action cancelled.
```

Then test:

```text
yes
```

Only if the action is intentionally safe to test.

### Critical rule

The LLM must never bypass:

```text
Tool validation
        ↓
Safety
        ↓
Confirmation
```

---

# 15. Conversation Regression Test

Run:

```text
Hi.
```

Then:

```text
How are you?
```

Then:

```text
What is Python?
```

Then:

```text
Tell me something interesting about it.
```

Heisenberg should maintain relevant context without drifting into unrelated subjects.

Test deliberately ambiguous input:

```text
Open it.
```

Expected:

```text
Clarification
```

not a guessed action.

---

# 16. Performance Benchmark

Measure latency.

Add timing around:

```text
Whisper
LLM
Tool execution
TTS
Total
```

Target output:

```text
Whisper:       ___ seconds
LLM:           ___ seconds
Tool:          ___ seconds
TTS:           ___ seconds
Total:         ___ seconds
```

Do at least five conversational tests and calculate approximate average latency.

### Important

Do not optimize based on guesses.

Measure first.

---

# 17. Memory Usage Test

While Heisenberg is running, monitor:

- RAM
- VRAM
- CPU
- GPU utilization
- model load time
- idle memory
- inference memory

PowerShell:

```powershell
Get-Process python |
Select-Object CPU,WorkingSet,Id,ProcessName
```

If using a GPU, use the runtime/GPU monitoring tools as appropriate.

Record:

```text
Model load time:
Idle RAM:
Peak RAM:
Peak VRAM:
Average CPU:
Average inference latency:
```

---

# 18. Failure Testing

Intentionally test:

### Empty input

```text
<silence>
```

Expected:

```text
Ignore / listen again
```

### Unknown command

```text
Open something impossible.
```

Expected:

```text
Clarification or safe refusal
```

### Malformed model output

The interface should not crash.

Expected:

```text
Safe fallback
```

### Tool failure

Example:

```text
Requested application does not exist.
```

Expected:

```text
Execution error → observation → useful response
```

### Model unavailable

Stop the LLM runtime and test.

Expected:

```text
Heisenberg reports that the AI service is unavailable.
```

The whole assistant should not silently crash.

---

# 19. Integration Acceptance Criteria

Qwen3.5 integration is considered successful only when all of these pass:

- [ ] Model downloads successfully
- [ ] Model runs locally
- [ ] Basic conversation works
- [ ] Instruction following works
- [ ] Context handling works
- [ ] Structured output works
- [ ] Invalid tool requests are rejected
- [ ] Existing deterministic commands still work
- [ ] Whisper integration works
- [ ] TTS integration works
- [ ] Safety confirmation still works
- [ ] Memory still works
- [ ] Unknown commands fail safely
- [ ] Model failures don't crash Heisenberg
- [ ] Performance is measured
- [ ] Memory consumption is measured
- [ ] Git checkpoint created

---

# 20. Final Git Checkpoint

After all tests pass:

```powershell
git status
git add .
git commit -m "Integrate Qwen3.5 local LLM for Heisenberg V2"
```

Then:

```powershell
git log --oneline -5
```

The repository should now have a clean checkpoint representing:

> **Heisenberg V2 — New AI Core Integrated**

---

# 21. What Comes AFTER This

Do not implement the remaining V2 features until this checkpoint passes.

The implementation order after successful model integration should be:

```text
Qwen3.5 Integration                 ← CURRENT MILESTONE
        ↓
Agent Core
        ↓
Tool Calling
        ↓
Tool Validation
        ↓
Safety / Permission Engine
        ↓
Agent Loop
        ↓
Unified Memory
        ↓
Web Research
        ↓
Browser Agent
        ↓
Vision / Screen Understanding
        ↓
Context Awareness
        ↓
Task Manager + Recovery
        ↓
Proactive / Ambient Behavior
        ↓
Scheduling
        ↓
Background Service
        ↓
Advanced Voice
        ↓
Hybrid Model Routing
        ↓
Security / Encryption
        ↓
Optimization / Observability
```

This order is deliberate: **the model must be reliable before we give it more capabilities.**

---

# 22. Migration Rule

During this migration:

> **Do not rewrite working V1 features merely because V2 will eventually replace them.**

Keep:

```text
Whisper
Normalization
Alias learning
Fast deterministic commands
Existing system actions
Existing memory
Existing safety logic
```

until their V2 replacements have been tested.

The objective is:

```text
V1 working
   ↓
Add Qwen3.5
   ↓
Test
   ↓
V1 still working
   ↓
Expand into V2
```

not:

```text
V1
 ↓
rewrite everything
 ↓
debug everything simultaneously
```

---

# Final Milestone

At the end of this document, Heisenberg should be able to do:

```text
User speaks
      ↓
Whisper
      ↓
Normalization
      ↓
Fast command OR Qwen3.5
      ↓
Conversation / structured decision
      ↓
Existing safe execution
      ↓
Response
      ↓
TTS
```

Only when this works reliably should the project move into the full **Heisenberg V2 Agent Architecture**.
