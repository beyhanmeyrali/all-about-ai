# Windows Setup Guide - Voice Assistant

Complete guide to run the voice assistant on Windows with microphone and speakers.

---

## 🪟 Quick Setup on Windows

### Prerequisites

1. **Python 3.12** - [Download from python.org](https://www.python.org/downloads/)
2. **Git** - [Download from git-scm.com](https://git-scm.com/download/win)
3. **Ollama** - [Download from ollama.com](https://ollama.com/download/windows)
4. **Docker Desktop** (for Qdrant) - [Download](https://www.docker.com/products/docker-desktop/)

---

## 📦 Step-by-Step Installation

### 1. Clone the Repository

Open PowerShell or Command Prompt:

```powershell
# Clone the repo
git clone <your-repo-url>
cd all-about-ai\ai-agents

# Or if already cloned, just navigate to it
cd path\to\all-about-ai\ai-agents
```

### 2. Create Virtual Environment

```powershell
# Create venv
python -m venv venv

# Activate venv
.\venv\Scripts\activate

# Verify
python --version
# Should show Python 3.12.x
```

### 3. Install Dependencies

```powershell
cd 05-voice-assistant

# Install all dependencies (~3GB download)
pip install -r requirements.txt

# This will install:
# - PyTorch (with CUDA if you have NVIDIA GPU)
# - Whisper (speech-to-text)
# - pyttsx3 (text-to-speech)
# - CrewAI (agent framework)
# - All other dependencies
```

### 4. Install Ollama Models

```powershell
# Start Ollama (if not running)
# Ollama should auto-start on Windows

# Pull required models
ollama pull qwen3:8b
ollama pull qwen3-embedding:0.6b

# Verify
ollama list
# Should show both models
```

### 5. Start Qdrant (Optional - for Knowledge Base)

```powershell
# Navigate to project root
cd ..

# Start Qdrant with Docker
docker compose up -d

# Verify
docker ps
# Should show qdrant container running
```

### 6. Verify Installation

```powershell
cd 05-voice-assistant

# Run verification script
python 00_verify_installation.py
```

Expected output:
```
✅ PyTorch 2.x.x (CUDA: True/False)
✅ OpenAI Whisper
✅ Silero VAD (model loaded)
✅ pyttsx3 TTS
⚠️  sounddevice (may show error on first run - ignore)
✅ soundfile
✅ NumPy
✅ SciPy

✅ Passed: 7/8
```

---

## 🎤 Running the Voice Assistant

### Option 1: Enhanced Assistant (Recommended)

**Full features: Knowledge Base + Web Search**

```powershell
# Make sure you're in 05-voice-assistant folder
cd 05-voice-assistant

# Activate venv if not already active
.\venv\Scripts\activate

# Run the enhanced assistant
python 06_voice_assistant_enhanced.py
```

**What happens:**
1. Loads all models (takes ~30 seconds first time)
2. Greets you with "Hello! I'm your enhanced AI assistant..."
3. Starts listening for your voice
4. Transcribes your speech
5. Answers using Knowledge Base OR Web Search
6. Speaks the answer back to you

**Try asking:**
- "What is RAG?" → Uses Knowledge Base
- "What's the weather today?" → Uses Web Search
- "Explain embeddings" → Uses Knowledge Base
- "Latest Python news" → Uses Web Search

**To stop:** Press `Ctrl+C`

### Option 2: Text-Based Chat (No microphone needed)

```powershell
python chat_assistant.py
```

Type your questions instead of speaking them.

### Option 3: Basic Assistant (Knowledge Base only)

```powershell
python 05_voice_assistant_rag.py
```

Only uses knowledge base, no web search.

---

## 🎯 Testing Individual Components

### Test Text-to-Speech

```powershell
python 03_tts_test.py
```

- Lists available voices
- Speaks test phrases
- Interactive mode to test different voices

### Test Speech-to-Text

```powershell
python 02_whisper_test.py
```

- Records 5 seconds of audio
- Transcribes using Whisper
- Shows detected language

### Test Voice Activity Detection

```powershell
python 01_vad_test.py
```

- Real-time speech detection
- Shows when you start/stop speaking

### Test Voice Loop

```powershell
python 04_voice_loop.py
```

- Continuous listening
- Automatic transcription
- No AI responses (just transcription)

---

## ⚙️ Configuration

### Change Whisper Model Size

Edit `06_voice_assistant_enhanced.py`:

```python
assistant = VoiceAssistantEnhanced(
    whisper_model_size="base",  # Options: tiny, base, small, medium, large
    tts_voice_index=0
)
```

**Model sizes:**
- `tiny` - Fastest, less accurate (~75MB)
- `base` - **Recommended** balance (~150MB)
- `small` - Better accuracy (~500MB)
- `medium` - Very good accuracy (~1.5GB)
- `large` - Best accuracy (~3GB)

### Change TTS Voice

```powershell
# Run this to see available voices
python -c "import pyttsx3; engine = pyttsx3.init(); voices = engine.getProperty('voices'); [print(f'{i}: {v.name}') for i, v in enumerate(voices)]"
```

Then edit the script:
```python
assistant = VoiceAssistantEnhanced(
    whisper_model_size="base",
    tts_voice_index=1  # Change to the voice index you want
)
```

### Adjust VAD Sensitivity

Edit `06_voice_assistant_enhanced.py`, change these constants:

```python
VAD_THRESHOLD = 0.5              # Lower = more sensitive (0.0-1.0)
MIN_SPEECH_DURATION_MS = 250     # Minimum speech duration
MIN_SILENCE_DURATION_MS = 500    # Silence before stopping recording
```

---

## 🔧 Troubleshooting

### Microphone Not Working

**Check Windows Settings:**
1. Settings → Privacy & Security → Microphone
2. Enable "Let apps access your microphone"
3. Enable for Python

**Set Default Microphone:**
1. Right-click speaker icon in taskbar
2. Open Sound Settings
3. Input → Choose your microphone
4. Test microphone

### Audio Playback Issues

**Check Speakers:**
1. Right-click speaker icon
2. Open Sound Settings
3. Output → Choose your speakers/headphones
4. Test audio

### Whisper Model Download Slow

Models are downloaded to: `C:\Users\<YourName>\.cache\whisper\`

- Use smaller model (`tiny` or `base`) for faster download
- First run downloads models (~150MB for base)
- Subsequent runs use cached models

### CUDA/GPU Not Detected

**If you have NVIDIA GPU:**

```powershell
# Check if CUDA is available
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

If False but you have NVIDIA GPU:
1. Install NVIDIA drivers
2. Install CUDA Toolkit 11.8+
3. Reinstall PyTorch with CUDA support

**CPU Only (works fine, just slower):**
- Whisper will use CPU
- Takes ~10-15 seconds instead of ~2 seconds
- Still usable!

### Ollama Not Responding

```powershell
# Check if Ollama is running
ollama list

# If not running, start it
# Ollama should auto-start, but you can run:
# Start Menu → Ollama (or check system tray)

# Test connection
curl http://localhost:11434/api/tags
```

### Qdrant Connection Failed

```powershell
# Check if Docker is running
docker ps

# Start Qdrant
docker compose up -d

# Verify
docker ps | findstr qdrant
```

**If you don't want to use Qdrant:**
- The assistant will still work with web search!
- Just ignore the knowledge base error
- Or use the text-based chat which has built-in knowledge

---

## 🎓 Usage Examples

### Example Session 1: Technical Questions

```
🎤 Voice Assistant Started
Speak into your microphone...

[You speak: "What is RAG?"]

🟢 Listening...
🔄 Transcribing...

💬 You: What is RAG?

🤔 Thinking (with KB + Web Search)...
🤖 Assistant: RAG stands for Retrieval-Augmented Generation.
It's a technique that combines information retrieval with LLM
generation to provide accurate, contextual responses based on
your own data.

🔊 Speaking...

[Assistant speaks the answer]
```

### Example Session 2: Current Information

```
[You speak: "What's the weather today?"]

🟢 Listening...
🔄 Transcribing...

💬 You: What's the weather today?

🤔 Thinking (with KB + Web Search)...
🤖 Assistant: I found current weather information from
AccuWeather showing partly cloudy conditions with a
temperature of 72°F...

🔊 Speaking...
```

---

## 📊 Performance Expectations

### With NVIDIA GPU (RTX 3060+):
- Speech detection: Instant
- Transcription: ~2 seconds
- Answer generation: ~2-3 seconds
- **Total response time: 4-5 seconds** ⚡

### CPU Only (Intel i7/AMD Ryzen 7):
- Speech detection: Instant
- Transcription: ~10-15 seconds
- Answer generation: ~3-5 seconds
- **Total response time: 13-20 seconds** 🐢

**Tips for faster performance:**
- Use `tiny` or `base` Whisper model
- Use GPU if available
- Close other applications

---

## 🌟 Advanced Features

### Enable Continuous Conversation

Currently, each question is independent. To maintain context:

1. Modify the agent to include conversation history
2. Store previous Q&A in memory
3. Pass to LLM for context-aware responses

(This is a future enhancement)

### Add Custom Knowledge

To add your own documents to the knowledge base:

1. Add documents to `03-embeddings-rag/data/`
2. Run the ingestion script to add to Qdrant
3. The assistant will now answer questions about your docs!

### Change Language

Edit `06_voice_assistant_enhanced.py`:

```python
result = self.whisper_model.transcribe(
    audio,
    language="en",  # Change to: "es", "fr", "de", "tr", etc.
    fp16=torch.cuda.is_available()
)
```

Whisper supports 99+ languages!

---

## 📱 Next Steps

### After Testing:

1. **Customize the agent** - Modify instructions, add more tools
2. **Add your knowledge base** - Ingest your own documents
3. **Improve TTS** - Try different voices or Coqui TTS
4. **Add wake word** - "Hey Assistant" activation
5. **Build a UI** - Gradio/Streamlit interface

---

## 🆘 Getting Help

### Check Logs

```powershell
# View Ollama logs
# Check: C:\Users\<YourName>\.ollama\logs\

# View Python errors
# Errors will be shown in console
```

### Common Issues

| Issue | Solution |
|-------|----------|
| "No module named..." | `pip install -r requirements.txt` |
| "Ollama not responding" | Start Ollama from Start Menu |
| "CUDA not available" | Install NVIDIA drivers + CUDA toolkit |
| "Microphone not detected" | Check Windows microphone permissions |
| "Qdrant connection failed" | `docker compose up -d` |

---

## ✅ Quick Start Checklist

- [ ] Python 3.12 installed
- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Ollama installed and models pulled
- [ ] Docker Desktop running (optional)
- [ ] Qdrant started (optional)
- [ ] Microphone and speakers working
- [ ] Run `python 06_voice_assistant_enhanced.py`
- [ ] Start talking! 🎤

---

## 🎉 Ready to Go!

Your command to start:

```powershell
cd 05-voice-assistant
.\venv\Scripts\activate
python 06_voice_assistant_enhanced.py
```

Then speak: **"What is RAG?"** and watch the magic happen! ✨

---

## 📚 Additional Resources

- **README.md** - Complete module documentation
- **TESTING_GUIDE.md** - Detailed testing instructions
- **ENHANCEMENT_SUMMARY.md** - Technical implementation details
- **COMPLETION_SUMMARY.md** - Original voice assistant features

---

**Happy Testing! 🎤🤖**
