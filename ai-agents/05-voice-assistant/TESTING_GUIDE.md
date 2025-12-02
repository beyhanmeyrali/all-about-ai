# Testing Guide - Voice Assistant

## 🧪 How to Test the Enhanced Voice Assistant

Since you're on WSL (without microphone/speakers), use the **text-based chat interface** to test all the features.

---

## ✅ Quick Test (Text-Based Chat)

### 1. Start the Interactive Chat Assistant

```bash
cd /workspace/all-about-ai/ai-agents/05-voice-assistant
source ../venv/bin/activate
python chat_assistant.py
```

### 2. Try These Example Questions

**Technical Questions** (uses Knowledge Base):
```
You: What is RAG?
You: Explain embeddings
You: What are AI agents?
You: Tell me about CrewAI
You: What is a vector database?
```

**Current Information** (uses Web Search):
```
You: Latest Python news
You: Current weather forecast
You: Bitcoin price today
You: Recent AI developments
```

### 3. Exit
Type `quit` or `exit` or press `Ctrl+C`

---

## 🎯 What You'll See

The assistant will:
1. **Choose the right tool** - Knowledge Base for technical, Web Search for current info
2. **Retrieve information** - From either the knowledge base or DuckDuckGo
3. **Generate answer** - Using Qwen3:8b LLM
4. **Display response** - Clear, concise answer

---

## 📊 Test Results

### Example 1: Technical Question
```
💬 You: What is RAG?

🤖 Assistant:
RAG stands for Retrieval-Augmented Generation. It is a technique that
combines retrieval of relevant information from external sources with
generative models to enhance the accuracy, relevance, and factual
correctness of responses in AI systems.
```
✅ Used: **Knowledge Base Search**

### Example 2: Current Information
```
💬 You: Latest Python news

🤖 Assistant:
I found current news about Python from TechCrunch, Google News, and
Reuters covering the latest developments in Python programming and
related technologies.
```
✅ Used: **Web Search**

---

## 🔧 Troubleshooting

### Ollama Not Running
```bash
# Start Ollama
nohup ollama serve > /tmp/ollama.log 2>&1 &

# Verify it's running
ollama list
```

### Missing Models
```bash
# Pull required models
ollama pull qwen3:8b
ollama pull qwen3-embedding:0.6b
```

### Qdrant Not Running
```bash
# From project root
cd /workspace/all-about-ai/ai-agents
docker compose up -d

# Verify
docker ps | grep qdrant
```

---

## 🎤 Testing with Actual Voice (Windows/Mac)

If you want to test the **full voice assistant** with microphone and speakers:

### Option 1: Transfer to Windows/Mac
1. Copy the `05-voice-assistant` folder to your Windows/Mac
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python 06_voice_assistant_enhanced.py`
4. Speak your questions!

### Option 2: Use Windows from WSL
1. Run the Python script from Windows PowerShell/CMD
2. Navigate to: `\\wsl$\Ubuntu\workspace\all-about-ai\ai-agents\05-voice-assistant`
3. Activate venv and run the voice assistant

---

## 📝 Quick Commands Cheat Sheet

```bash
# Navigate to voice assistant
cd /workspace/all-about-ai/ai-agents/05-voice-assistant
source ../venv/bin/activate

# Test web search only
python demo_web_search.py

# Interactive text chat (RECOMMENDED for WSL)
python chat_assistant.py

# Full voice assistant (requires microphone)
python 06_voice_assistant_enhanced.py

# Verify installation
python 00_verify_installation.py
```

---

## 🌟 Features You Can Test

### 1. Dual Tool System
- ✅ Knowledge Base Search (technical docs)
- ✅ Web Search (current information)

### 2. Intelligent Routing
- ✅ Agent decides which tool to use
- ✅ Can use both tools if needed

### 3. LLM Integration
- ✅ Qwen3:8b for answer generation
- ✅ Concise, helpful responses

### 4. Real-Time Search
- ✅ DuckDuckGo search
- ✅ No API keys needed
- ✅ Privacy-friendly

---

## 🎓 Understanding the Output

When you run `chat_assistant.py`, you'll see:

```
🚀 Crew: crew
└── 📋 Task: [task-id]
    Assigned to: AI Assistant
    Status: ✅ Completed
```

This shows:
- **Crew** - The CrewAI framework managing the agent
- **Task** - Your question
- **Agent** - The AI Assistant processing it
- **Tools** - Which tools were used
- **Final Answer** - The response

---

## 💡 Tips for Testing

1. **Start Simple**: Begin with "What is RAG?" to verify it works
2. **Try Both Tools**: Ask technical AND current information questions
3. **Watch the Output**: See which tool the agent chooses
4. **Multiple Questions**: Have a conversation, ask follow-ups
5. **Exit Cleanly**: Type `quit` when done

---

## ✅ Success Criteria

You'll know it's working when:
- ✅ Assistant responds to questions
- ✅ Uses appropriate tools (KB or Web)
- ✅ Provides accurate answers
- ✅ No errors in output

---

## 🚀 Ready to Test?

Run this command and start chatting:
```bash
python chat_assistant.py
```

Ask: **"What is RAG?"** to get started! 🎉
