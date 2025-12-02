# Pull to Windows - Quick Guide

## 🚀 Steps to Test Voice Assistant on Windows

### 1. Pull the Repository to Windows

From your Windows machine:

```powershell
# Option A: Clone fresh
git clone <your-repo-url>
cd all-about-ai\ai-agents

# Option B: Pull latest changes if already cloned
git pull origin main
```

### 2. Install Prerequisites

**Required:**
- Python 3.12: https://www.python.org/downloads/
- Ollama: https://ollama.com/download/windows

**Optional (for Knowledge Base):**
- Docker Desktop: https://www.docker.com/products/docker-desktop/

### 3. Quick Setup

```powershell
# Navigate to voice assistant
cd 05-voice-assistant

# Create virtual environment
python -m venv venv

# Activate venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Pull Ollama models
ollama pull qwen3:8b
ollama pull qwen3-embedding:0.6b
```

### 4. Run Voice Assistant

```powershell
# Start the enhanced assistant
python 06_voice_assistant_enhanced.py
```

That's it! The assistant will greet you and start listening.

---

## 📋 What to Test

**Technical Questions (Knowledge Base):**
- "What is RAG?"
- "Explain embeddings"
- "What are AI agents?"

**Current Information (Web Search):**
- "What's the weather today?"
- "Latest Python news"
- "Current Bitcoin price"

---

## 📖 Detailed Guides

See these files for more information:
- **WINDOWS_SETUP.md** - Complete Windows setup guide
- **TESTING_GUIDE.md** - Testing instructions
- **README.md** - Full documentation

---

## ⚡ Quick Commands

```powershell
# Text chat (no microphone)
python chat_assistant.py

# Web search demo
python demo_web_search.py

# Verify installation
python 00_verify_installation.py

# Full voice assistant
python 06_voice_assistant_enhanced.py
```

---

## 🎯 Expected Behavior

1. **Greeting**: "Hello! I'm your enhanced AI assistant..."
2. **Listening**: Shows "🟢 Listening..." when you speak
3. **Transcription**: Converts your speech to text
4. **Tool Selection**: Chooses Knowledge Base or Web Search
5. **Response**: Speaks the answer back to you

---

## 📊 File Structure

```
05-voice-assistant/
├── 06_voice_assistant_enhanced.py  ⭐ Main voice assistant
├── chat_assistant.py               💬 Text-based chat
├── tools_web_search.py             🌐 Web search tool
├── demo_web_search.py              🧪 Demo script
├── requirements.txt                📦 Dependencies
├── WINDOWS_SETUP.md               📖 Setup guide
├── TESTING_GUIDE.md               📖 Testing guide
└── README.md                       📖 Full docs
```

---

**Ready to test? Pull the repo and follow WINDOWS_SETUP.md!** 🎉
