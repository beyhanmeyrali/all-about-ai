# Voice Assistant Module

Build a complete Voice GPT assistant with RAG integration running 100% locally.

## 🎯 Overview

This module implements a full voice assistant that combines:
- **Voice Activity Detection (VAD)** - Silero VAD for detecting speech
- **Speech-to-Text (STT)** - Whisper for accurate transcription
- **RAG Agent** - CrewAI agent with Qdrant knowledge base
- **Text-to-Speech (TTS)** - pyttsx3 for speaking responses

## 📁 Module Structure

```
05-voice-assistant/
├── README.md                        # This file
├── requirements.txt                 # Dependencies
├── 00_verify_installation.py       # Verify all components are installed
├── 01_vad_test.py                  # Test Silero VAD alone
├── 02_whisper_test.py              # Test Whisper STT alone
├── 03_tts_test.py                  # Test TTS alone
├── 04_voice_loop.py                # VAD + Whisper integration
├── 05_voice_assistant_rag.py       # Complete voice assistant with RAG
├── tools_web_search.py             # Web search tool (DuckDuckGo)
└── 06_voice_assistant_enhanced.py  # ✨ ENHANCED: RAG + Web Search
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Activate virtual environment
source ../venv/bin/activate  # Linux/Mac
# or
..\venv\Scripts\activate     # Windows

# Install dependencies (~2-3GB download for PyTorch + Whisper)
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python 00_verify_installation.py
```

This will check that all components are installed correctly.

### 3. Start Qdrant (Required for RAG)

```bash
# From project root
docker compose up -d
```

### 4. Run the Voice Assistant

**Option A: Basic RAG Assistant** (knowledge base only)
```bash
python 05_voice_assistant_rag.py
```

**Option B: Enhanced Assistant** (✨ RECOMMENDED - knowledge base + web search)
```bash
python 06_voice_assistant_enhanced.py
```

The enhanced assistant will:
1. ✅ Greet you
2. 🎤 Listen continuously for your voice
3. 🔄 Transcribe your questions
4. 🧠 Search knowledge base for technical topics
5. 🌐 Search the web for current information
6. 🔊 Speak the answers

## 🧪 Testing Individual Components

### Test TTS (Text-to-Speech)
```bash
python 03_tts_test.py
```
- No downloads required
- Uses system voices
- Interactive mode to test different voices

### Test Whisper (Speech-to-Text)
```bash
python 02_whisper_test.py
```
- First run downloads ~150MB for base model
- Records 5 seconds and transcribes
- Supports multiple languages

### Test VAD (Voice Activity Detection)
```bash
python 01_vad_test.py
```
- First run downloads ~1MB VAD model
- Real-time speech detection
- Shows when speech starts/ends

### Test Voice Loop (VAD + Whisper)
```bash
python 04_voice_loop.py
```
- Continuous listening
- Automatic speech detection and transcription
- No RAG integration

## 🏗️ Architecture

### Complete Voice Assistant Flow

```
┌────────────────────────────────────────────────────────────┐
│                   Voice Assistant Loop                      │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  1. [Silero VAD]                                           │
│     ↓ Detects speech start/end                             │
│     ↓ Records audio during speech                          │
│                                                             │
│  2. [Whisper STT]                                          │
│     ↓ Transcribes audio to text                            │
│     ↓ Supports multiple languages                          │
│                                                             │
│  3. [RAG Agent - CrewAI]                                   │
│     ↓ Receives user query                                  │
│     ↓ Searches Qdrant knowledge base                       │
│     ↓ Uses qwen3:8b LLM to generate answer                 │
│                                                             │
│  4. [pyttsx3 TTS]                                          │
│     ↓ Converts answer to speech                            │
│     ↓ Speaks using system voices                           │
│                                                             │
│  5. Loop back to step 1                                    │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. Silero VAD
- **Purpose:** Detect when user starts/stops speaking
- **Model:** Silero VAD (PyTorch)
- **Latency:** ~50ms
- **Accuracy:** High (even with background noise)
- **Offline:** ✅ Yes
- **Size:** ~1MB

#### 2. Whisper STT
- **Purpose:** Convert speech to text
- **Model:** OpenAI Whisper (base = ~150MB)
- **Languages:** 99+ languages supported
- **Accuracy:** Very high (better than Google STT for many accents)
- **Offline:** ✅ Yes (after model download)
- **GPU:** Optional (5-10x faster with CUDA)

**Model Sizes:**
- `tiny` - 39M params, ~75MB, fastest
- `base` - 74M params, ~150MB, **recommended balance**
- `small` - 244M params, ~500MB, higher accuracy
- `medium` - 769M params, ~1.5GB, very high accuracy
- `large` - 1550M params, ~3GB, best accuracy

#### 3. RAG Agent (CrewAI + Qdrant)
- **LLM:** Qwen3:8b via Ollama
- **Vector DB:** Qdrant
- **Embeddings:** qwen3-embedding:0.6b
- **Knowledge Base:** AI Agents documentation
- **Tools:** KnowledgeBaseTool for semantic search

#### 4. pyttsx3 TTS
- **Purpose:** Convert text to speech
- **Engine:** System TTS (Windows: SAPI, Linux: espeak, Mac: NSSpeechSynthesizer)
- **Offline:** ✅ Yes
- **Latency:** Low (~100ms)
- **Quality:** Good (system voices)
- **Customization:** Speed, volume, voice selection

## ⚙️ Configuration

### Whisper Model Size

Edit in `05_voice_assistant_rag.py`:
```python
assistant = VoiceAssistant(
    whisper_model_size="base",  # Change to: tiny, small, medium, large
    tts_voice_index=0
)
```

### TTS Voice

List available voices:
```python
import pyttsx3
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for i, voice in enumerate(voices):
    print(f"{i}: {voice.name}")
```

Then set in assistant:
```python
assistant = VoiceAssistant(
    whisper_model_size="base",
    tts_voice_index=1  # Use voice at index 1
)
```

### VAD Sensitivity

Edit in `04_voice_loop.py` or `05_voice_assistant_rag.py`:
```python
VAD_THRESHOLD = 0.5              # Lower = more sensitive (0.0-1.0)
MIN_SPEECH_DURATION_MS = 250     # Minimum speech duration
MIN_SILENCE_DURATION_MS = 500    # Silence before stopping recording
```

### Language Detection

In Whisper transcription:
```python
result = self.whisper_model.transcribe(
    audio,
    language="en",  # Force English
    # language="tr",  # Force Turkish
    # language=None,  # Auto-detect (default)
    fp16=torch.cuda.is_available()
)
```

## 🎤 System Requirements

### Minimum (CPU only)
- **RAM:** 4GB (2GB for Whisper base + 2GB for system)
- **CPU:** 4 cores
- **Disk:** 3GB (models + dependencies)
- **Microphone:** Any USB or built-in mic
- **Speakers:** Any audio output device

### Recommended (GPU)
- **RAM:** 8GB
- **GPU:** NVIDIA with 4GB+ VRAM (RTX 3060, 4060, etc.)
- **CPU:** 6+ cores
- **Disk:** 5GB
- **CUDA:** 11.8+ installed

### Performance Benchmarks

**With GPU (NVIDIA RTX 4060):**
- Whisper base: ~2 seconds for 5 seconds of audio
- Total latency: ~2-3 seconds (speech end → response start)
- Feels nearly real-time

**CPU Only (AMD Ryzen 7 / Intel i7):**
- Whisper base: ~10-15 seconds for 5 seconds of audio
- Total latency: ~12-18 seconds (speech end → response start)
- Usable but noticeable delay

**Optimization Tips:**
1. Use `tiny` model on CPU for faster response (~5s latency)
2. Use `base` or `small` on GPU for best balance
3. Enable FP16 on GPU (already enabled in code)

## 🔧 Troubleshooting

### Microphone Not Detected

**Linux/WSL:**
```bash
# Install PortAudio
sudo apt-get install portaudio19-dev python3-pyaudio

# List audio devices
python -m sounddevice
```

**Windows:**
- Check microphone permissions in Settings
- Ensure microphone is set as default device

**macOS:**
- Grant microphone permission to Terminal
- System Preferences → Security & Privacy → Microphone

### Whisper Model Download Fails

Models are cached in `~/.cache/whisper/`. If download fails:
1. Check internet connection
2. Try smaller model first (`tiny`)
3. Manually download from [Hugging Face](https://huggingface.co/openai/whisper-base)

### Qdrant Connection Error

```bash
# Check if Qdrant is running
curl http://localhost:6333/health

# If not running, start it
cd /path/to/project
docker compose up -d

# Check collections
curl http://localhost:6333/collections
```

### TTS Not Working

**Linux:**
```bash
# Install espeak
sudo apt-get install espeak

# Test
espeak "Hello world"
```

**Windows:**
- TTS uses built-in SAPI voices
- Install additional voices from Microsoft Store

**macOS:**
- Uses built-in NSSpeechSynthesizer
- Should work out of the box

### Low Audio Quality

1. **Check microphone settings:**
   - Sample rate: 16kHz (required by VAD/Whisper)
   - Channels: Mono
   - Bit depth: 16-bit or 32-bit float

2. **Reduce background noise:**
   - Use headset microphone
   - Speak clearly and close to mic
   - Enable noise cancellation in OS settings

3. **Adjust VAD sensitivity:**
   - Lower `VAD_THRESHOLD` for quieter speech
   - Increase `MIN_SILENCE_DURATION_MS` for slower speakers

### High Latency

1. **Use smaller Whisper model:**
   - `tiny` is 5x faster than `base`
   - Good enough for simple queries

2. **Enable GPU:**
   ```bash
   # Check CUDA availability
   python -c "import torch; print(torch.cuda.is_available())"
   ```

3. **Reduce silence timeout:**
   ```python
   MIN_SILENCE_DURATION_MS = 300  # Faster but may cut off slow speakers
   ```

## 🧑‍💻 Usage Examples

### Basic Question
```
You: "What is RAG?"
Assistant: "RAG stands for Retrieval-Augmented Generation. It's a technique that combines..."
```

### Knowledge Base Query
```
You: "How do I use embeddings in RAG?"
Assistant: "According to the documentation, embeddings are used to convert text..."
```

### Multi-turn Conversation
```
You: "What are AI agents?"
Assistant: "AI agents are autonomous systems that can..."

You: "Can you give me an example?"
Assistant: "Sure! A common example is a customer support agent that..."
```

## 🎓 Learning Path

1. **Start with individual tests:**
   - Run `03_tts_test.py` (fastest, no downloads)
   - Run `02_whisper_test.py` (downloads ~150MB)
   - Run `01_vad_test.py` (downloads ~1MB)

2. **Test integration:**
   - Run `04_voice_loop.py` (VAD + Whisper)
   - Speak into microphone and see transcriptions

3. **Full assistant:**
   - Ensure Qdrant is running
   - Run `05_voice_assistant_rag.py`
   - Ask questions about AI agents

## 🌟 Enhanced Features (NEW!)

### Web Search Integration

The **06_voice_assistant_enhanced.py** adds real-time web search capability:

**Why Web Search?**
- Knowledge base has technical documentation (AI agents, RAG, embeddings)
- Web search provides current, real-time information
- Best of both worlds: technical expertise + current events

**What Can You Ask?**

**Technical Questions** (uses Knowledge Base):
- "What is RAG?"
- "How do embeddings work?"
- "Explain LangChain tools"
- "What are AI agents?"

**Current Information** (uses Web Search):
- "What's the weather today?"
- "Latest Python news"
- "Current Bitcoin price"
- "Recent AI developments"

**How It Works:**
1. Agent receives your question
2. Decides which tool to use (Knowledge Base or Web Search)
3. Retrieves relevant information
4. Synthesizes concise answer
5. Speaks response

**Tools Available:**
- `KnowledgeBaseTool` - Searches Qdrant vector database
- `WebSearchTool` - Searches DuckDuckGo for current info

### Architecture Comparison

**Basic Assistant (05_voice_assistant_rag.py):**
```
Voice → VAD → Whisper → RAG Agent → [Knowledge Base] → TTS → Speaker
```

**Enhanced Assistant (06_voice_assistant_enhanced.py):**
```
Voice → VAD → Whisper → Enhanced Agent → [Knowledge Base OR Web Search] → TTS → Speaker
                                           ↓                    ↓
                                      Qdrant Vector DB    DuckDuckGo API
```

## 🔗 Integration with Other Modules

This voice assistant integrates with:

- **03-embeddings-rag:** Uses Qdrant vector database (Docker)
- **04-integrated-agents:** Uses RAG agent implementation
- **02-agent-frameworks:** Uses CrewAI framework
- **00-llm-basics:** Uses Ollama for LLM inference
- **LocalVLMAgent:** Web search tool adapted from this project

## 📚 Next Steps

### Implemented Enhancements ✅

1. **Web Search** ✅ - Real-time information via DuckDuckGo
2. **Dual Tool System** ✅ - Knowledge Base + Web Search

### Future Enhancements

1. **Wake Word Detection:**
   - Add "Hey Assistant" wake word
   - Use Porcupine or Picovoice

2. **Conversation History:**
   - Maintain context across queries
   - Store in SQLite or memory

3. **Multi-language Support:**
   - Auto-detect language with Whisper
   - Respond in detected language

4. **Better TTS:**
   - Replace pyttsx3 with Coqui TTS
   - More natural voices

5. **Web UI:**
   - Add Gradio/Streamlit interface
   - Visual feedback and controls

6. **Mobile App:**
   - Create Flutter/React Native app
   - Connect to local server

## 🐛 Known Issues

1. **WSL Audio:** Audio devices not available in WSL without additional setup
2. **First Run:** Model downloads can take time on slow connections
3. **Interruptions:** Cannot interrupt assistant while speaking (future enhancement)

## 📖 References

- [Silero VAD](https://github.com/snakers4/silero-vad)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [pyttsx3](https://pyttsx3.readthedocs.io/)
- [CrewAI](https://docs.crewai.com/)
- [Qdrant](https://qdrant.tech/)

---

**Ready to start?** Run `python 05_voice_assistant_rag.py` and start talking! 🎤
