# Voice Assistant Module

This module contains the voice interface components for the AI Agent system.

## Components

### 1. Voice Activity Detection (VAD) - Silero VAD
**File:** `01_vad_test.py`

Silero VAD is a lightweight, efficient voice activity detector that:
- Detects when speech starts and ends
- Works in real-time with low latency
- Requires only 16kHz audio
- No internet connection needed

**Usage:**
```powershell
python 01_vad_test.py
```

### 2. Speech-to-Text (STT) - Whisper
**File:** `02_whisper_test.py`

OpenAI Whisper for accurate speech recognition:
- Supports multiple languages (English, Turkish, etc.)
- Works offline after model download
- Multiple model sizes (tiny, base, small, medium, large)
- High accuracy even with accents

**Usage:**
```powershell
python 02_whisper_test.py
```

**Model Sizes:**
- `tiny` - Fastest, least accurate (~75MB)
- `base` - Good balance (~150MB) **← Recommended**
- `small` - Better accuracy (~500MB)
- `medium` - High accuracy (~1.5GB)
- `large` - Best accuracy (~3GB)

### 3. Text-to-Speech (TTS) - pyttsx3
**File:** `03_tts_test.py`

System TTS using pyttsx3:
- Uses Windows built-in voices
- No internet required
- Adjustable speed and voice
- Lightweight and fast

**Usage:**
```powershell
python 03_tts_test.py
```

## Installation

```powershell
# Navigate to the voice-assistant directory
cd 05-voice-assistant

# Install dependencies (use the shared .venv_new from crewai)
..\..\02-agent-frameworks\crewai\.venv_new\Scripts\pip install -r requirements.txt
```

**Note:** Installing Whisper and PyTorch will download ~2-3GB of data.

## System Requirements

- **Microphone** for voice input
- **Speakers/Headphones** for audio output
- **~4GB RAM** for Whisper base model
- **~2GB disk space** for models

## Architecture

```
User Voice Input
    ↓
[Silero VAD] ← Detects speech start/end
    ↓
[Whisper STT] ← Converts speech to text
    ↓
[RAG Agent] ← Processes query with knowledge base
    ↓
[pyttsx3 TTS] ← Speaks the answer
    ↓
User hears response
```

## Next Steps

After testing individual components:
1. Combine VAD + Whisper for continuous listening
2. Integrate with RAG agent from `04-integrated-agents`
3. Add TTS for spoken responses
4. Create full voice assistant loop

## Troubleshooting

### Microphone not detected
- Check Windows sound settings
- Ensure microphone is set as default input device
- Run `python -m sounddevice` to list audio devices

### Whisper model download fails
- Check internet connection
- Models are cached in `~/.cache/whisper/`
- Try smaller model size first

### TTS voice not working
- Windows voices are in Settings → Time & Language → Speech
- Install additional voices if needed
- Try different voice index in the script
