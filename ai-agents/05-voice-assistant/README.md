# 05 - Voice Assistant (Agentic & Web Interface)

This module builds a comprehensive Voice Assistant capable of:
1.  **Voice Interaction**: Speech-to-Text (Whisper) and Text-to-Speech (pyttsx3).
2.  **Agentic Capabilities**: Controlling simulated smart home devices (AC, TV, Door).
3.  **Web Interface**: A real-time dashboard visualization.

## Structure

-   `01_vad_test.py`: Testing Voice Activity Detection.
-   `02_whisper_test.py`: Testing Speech-to-Text.
-   `03_tts_test.py`: Testing Text-to-Speech.
-   `04_voice_loop.py`: Basic voice loop.
-   `05_voice_pipeline_rag.py`: Voice loop integrated with RAG (Qdrant).
-   `06_voice_assistant_enhanced.py`: Enhanced version with Web Search + RAG.
-   `**07_voice_assistant_agentic.py**`: **(NEW)** The complete Agentic Assistant with Web UI.

## 07 Agentic Voice Assistant

This script (`07_voice_assistant_agentic.py`) launches a web server and a voice assistant simultaneously.

### Features
-   **Voice Control**: Hands-free operation with proper turn-taking (no feedback loops)
-   **Tool Calling**: AI decides which home automation functions to execute
-   **Real-time Dashboard**: Web UI showing device states updated live
-   **Home Automation Tools**:
    -   "Turn on the AC" / "Turn off the AC"
    -   "Set AC to 25 degrees"
    -   "Turn on TV" / "Turn off TV"
    -   "Lock the door" / "Unlock the door"
    -   "Turn on everything" / "Turn off everything"

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     VOICE ASSISTANT FLOW                                 │
└─────────────────────────────────────────────────────────────────────────┘

 USER SPEAKS                    PROCESSING                     RESPONSE
    │                                                               │
    ▼                                                               ▼
┌─────────┐         ┌──────────────────────────────────┐      ┌─────────┐
│  🎤     │         │   VOICE PROCESSING PIPELINE      │      │  🔊     │
│ Audio   │────────▶│                                  │─────▶│  TTS    │
│ Input   │         │  1. VAD (Voice Activity Detect) │      │ Output  │
└─────────┘         │  2. Whisper (Speech-to-Text)    │      └─────────┘
                    │  3. Agent (Tool Decision)        │           ▲
                    │  4. Tool Execution               │           │
                    └──────────────────────────────────┘           │
                              │         │                           │
                              │         ▼                           │
                              │  ┌──────────────┐                  │
                              │  │ OLLAMA LLM   │                  │
                              │  │ ministral-3  │                  │
                              │  └──────────────┘                  │
                              │         │                           │
                              │         ▼                           │
                              │  ┌──────────────┐                  │
                              │  │ JSON Parser  │                  │
                              │  │ Tool Router  │                  │
                              │  └──────────────┘                  │
                              │         │                           │
                              ▼         ▼                           │
                    ┌─────────────────────────┐                    │
                    │  HOME AUTOMATION TOOLS  │                    │
                    ├─────────────────────────┤                    │
                    │ • turn_on_ac()          │                    │
                    │ • turn_off_ac()         │                    │
                    │ • set_ac_temperature()  │───────────────────┘
                    │ • turn_on_tv()          │  (Results returned
                    │ • turn_off_tv()         │   as text response)
                    │ • lock_door()           │
                    │ • unlock_door()         │
                    └─────────────────────────┘
                              │
                              ▼
                    ┌─────────────────────────┐
                    │    DEVICE STATE         │
                    │  { ac: {power, temp},   │
                    │    tv: {power},         │
                    │    door: {locked} }     │
                    └─────────────────────────┘
                              │
                              ▼
                    ┌─────────────────────────┐
                    │   WEB DASHBOARD         │
                    │   (FastAPI + HTML)      │
                    │   Auto-refresh: 1 sec   │
                    │   http://localhost:8000 │
                    └─────────────────────────┘
```

### Detailed Flow

1. **Audio Capture** (Thread 1):
   - Microphone continuously captures audio chunks
   - VAD (Silero) detects when user starts/stops speaking
   - Records audio while user is talking

2. **Speech-to-Text**:
   - Whisper transcribes recorded audio to text
   - Language: English, FP16 precision when available
   - Example: "Turn on the AC and TV"

3. **Agent Processing** (Ollama):
   - LLM receives transcribed text + system prompt
   - Decides which tool(s) to call based on intent
   - Returns JSON: `[{"tool": "turn_on_ac"}, {"tool": "turn_on_tv"}]`

4. **Tool Execution**:
   - Parser extracts tool names and arguments
   - Executes corresponding Python functions
   - Updates global device state
   - Returns result: "AC turned ON. TV turned ON."

5. **Text-to-Speech** (Thread 2):
   - **CRITICAL**: Pauses audio input before speaking (prevents feedback loop)
   - pyttsx3 speaks the response
   - Resumes audio input after completion
   - User hears: "AC turned ON. TV turned ON."

6. **Web Dashboard**:
   - FastAPI serves HTML/CSS/JS dashboard
   - Browser polls `/api/devices` every 1 second
   - Updates UI in real-time as devices change state

### Audio Feedback Prevention

The system uses **turn-taking** to prevent the microphone from hearing its own speech:

```
┌──────────────────────────────────────────────────────┐
│  Audio Loop (Always Running)                         │
│                                                       │
│  User Speaking:  [LISTENING] ────────────────────▶   │
│                       │                               │
│                       ▼                               │
│                  [RECORDING]                          │
│                       │                               │
│                       ▼                               │
│  Processing:    [AUDIO PAUSED] ◀── TTS Speaking      │
│                       │                               │
│                       ▼                               │
│  Ready:         [LISTENING] ◀──── TTS Complete       │
│                                                       │
└──────────────────────────────────────────────────────┘
```

### How to Run

1. **Prerequisites**:
   - Ollama running with `ministral-3:3b` model
   - Python 3.12+ (or use `.venv` with Python 3.12.8)

2. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn openai-whisper sounddevice pyttsx3 requests torch
   ```

3. **Run the assistant**:
   ```bash
   # Using virtual environment (recommended)
   .venv\Scripts\python.exe 07_voice_assistant_agentic.py

   # Or with system Python
   python 07_voice_assistant_agentic.py
   ```

4. **Open dashboard**:
   - Navigate to `http://localhost:8000`
   - See real-time device states

5. **Voice commands to try**:
   - "Turn on the AC"
   - "Set AC temperature to 22"
   - "Turn on TV and AC"
   - "Turn off everything"
   - "Unlock the door"
