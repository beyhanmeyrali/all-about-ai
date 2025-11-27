# AI Agents: From Zero to Hero 🤖

> A comprehensive, hands-on guide to building AI agents - from basic LLM usage to production-grade voice assistants

[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLMs-blue.svg)](https://ollama.ai/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agents-orange.svg)](https://github.com/langchain-ai/langgraph)

**Created by:** [Beyhan MEYRALI](https://www.linkedin.com/in/beyhanmeyrali/)

---

## 🎯 What You'll Build

This is not just another AI tutorial. By the end of this guide, you'll build a **fully functional Voice GPT** similar to ChatGPT's voice mode, complete with:
- 🎙️ Real-time speech recognition (Whisper)
- 🧠 Intelligent conversation management (LangGraph)
- 💾 Long-term memory (Letta/MemGPT)
- 🔧 Tool usage and function calling
- 🗣️ Natural text-to-speech responses
- 🏠 **100% running locally on your machine**

---

## 📖 Learning Philosophy

### Why This Guide Is Different

1. **Zero to Hero** - Literally start from "what is an LLM?" to production voice assistant
2. **Local-First** - Everything runs on Ollama (local LLMs) and local Whisper
3. **Debugger-Friendly** - Heavily commented code designed for stepping through with a debugger
4. **HTTP/REST Examples** - Every example includes `curl` commands so you understand the HTTP layer
5. **Hands-On** - Build real applications, not toy examples
6. **No Black Boxes** - Understand how LLMs, tools, agents, and memory work under the hood

### Important Concept: LLMs Are Stateless!

🔴 **Critical Understanding**: LLMs do NOT store data. They are like calculators:
- Input → Processing → Output
- No memory of previous conversations (unless you send conversation history)
- No knowledge of your data (unless you fine-tune or use RAG)
- Every API call is independent

This is why we need:
- **Context management** - Sending conversation history
- **RAG (Retrieval)** - Fetching relevant data from vector databases
- **Memory systems** - Persisting long-term context (Letta/MemGPT)
- **Fine-tuning** - Actually modifying model weights (see `../fine-tuning/`)

---

## 🗂️ Course Structure

### 📚 [00-llm-basics](./00-llm-basics) - Understanding the Foundation
**Duration:** 2-3 hours

**What You'll Learn:**
- How LLMs actually work (stateless computation)
- Why LLMs don't "remember" anything
- Basic API calls with Ollama
- Streaming responses for better UX
- Simple curl examples for HTTP understanding
- Prompting techniques and system prompts

**Key Takeaway:** LLMs are powerful pattern matchers, not databases

---

### 🔧 [01-tool-calling](./01-tool-calling) - Giving LLMs Superpowers
**Duration:** 3-4 hours

**What You'll Learn:**
- Function/tool calling fundamentals
- How LLMs decide when to use tools
- **Recursive tool calling** (the secret sauce!)
- Real-world examples: Weather API, Database queries
- Error handling and retry logic
- Multi-step tool orchestration

**Key Examples:**
- ✅ Basic weather tool (single call)
- ✅ ERP/Database integration (from your chameleon examples)
- ✅ Recursive agent that can call multiple tools in sequence
- ✅ curl examples for each endpoint

**Key Takeaway:** Tools transform LLMs from chatbots to agents

---

### 🕸️ [02-agent-frameworks](./02-agent-frameworks) - Professional Agent Development
**Duration:** 6-8 hours

**What You'll Learn:**
- **LangGraph** - State machines for complex workflows
- **CrewAI** - Multi-agent collaboration
- When to use frameworks vs. raw tool calling
- Graph-based agent design patterns
- Debugging agent execution flows

**Projects:**
- 🎯 Customer support agent (LangGraph)
- 🎯 Multi-agent research team (CrewAI)
- 🎯 Workflow automation agent

**Key Takeaway:** Frameworks provide structure for complex agent behaviors

---

### 📊 [03-rag-systems](./03-rag-systems) - Teaching LLMs About Your Data
**Duration:** 5-6 hours

**What You'll Learn:**
- Vector databases (Qdrant, ChromaDB)
- Embeddings and semantic search
- Document processing and chunking strategies
- RAG with LangGraph integration
- Performance optimization

**Why RAG Matters:**
- LLMs don't know YOUR data
- Fine-tuning is expensive and slow
- RAG provides real-time, updatable knowledge
- Cost-effective for private/dynamic data

**Projects:**
- 📚 Document Q&A system
- 📚 Code search assistant
- 📚 Company knowledge base

**Key Takeaway:** RAG is how you connect LLMs to your world

---

### 🧠 [04-memory-systems](./04-memory-systems) - Long-Term Context
**Duration:** 4-5 hours

**What You'll Learn:**
- Why context windows aren't enough
- **Letta (MemGPT)** architecture
- Long-term memory patterns
- Context prioritization strategies
- Letta + LangGraph integration

**The Memory Problem:**
```
Without Memory:
User: "My name is John"
AI: "Nice to meet you, John"
[5 minutes later]
User: "What's my name?"
AI: "I don't know, you haven't told me"

With Letta:
User: "My name is John"
AI: "Nice to meet you, John" [stores to long-term memory]
[5 minutes later]
User: "What's my name?"
AI: "Your name is John!" [retrieves from memory]
```

**Key Takeaway:** Memory systems enable truly persistent assistants

---

### 🎙️ [05-voice-gpt](./05-voice-gpt) - Building Your Voice Assistant
**Duration:** 8-10 hours

**What You'll Learn:**
- **Whisper** integration (local speech-to-text)
- Text-to-speech (TTS) with local models
- Real-time audio streaming
- LangGraph state management for conversations
- Combining everything: Whisper → LangGraph → Letta → TTS

**Final Project: Voice GPT**
```
You → Whisper (STT) → LangGraph (Agent) → Letta (Memory) → TTS → You
          ↓                    ↓                  ↓
      "What's the         [Uses tools]      [Remembers
       weather?"           [Retrieves          previous
                           from RAG]        conversations]
```

**Key Features:**
- 🎤 Hands-free voice interaction
- 🧠 Remembers conversation context
- 🔍 Can search your documents (RAG)
- 🛠️ Can call tools (weather, calendar, etc.)
- 🏠 Runs 100% locally

**Key Takeaway:** This is the culmination of everything you've learned

---

## 🚀 Quick Start

### Prerequisites & Setup

#### Step 1: Install Ollama

**Windows:**
```powershell
# Download from https://ollama.ai/download/windows
# Or use winget
winget install Ollama.Ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**macOS:**
```bash
brew install ollama
```

**Verify Installation:**
```bash
ollama --version
```

#### Step 2: Pull Required Models

We use **Qwen3:8b** - the best reasoning + tool-calling model in 2025 for local agents:

```bash
# Main LLM (Q4_K_M quantization - best quality/speed balance)
ollama pull qwen3:8b

# Embedding model for RAG (you'll need this later)
ollama pull nomic-embed-text

# Verify models are ready
ollama list
```

**Why Qwen3:8b?**
- ✅ **Excellent tool-calling** - Native function calling support
- ✅ **Strong reasoning** - Outperforms many 13B models
- ✅ **Runs smoothly** - ~5GB RAM, fast on CPU, blazing on GPU
- ✅ **8B parameters** - Sweet spot for quality vs resource usage
- ✅ **128K context window** - Handle large conversations/documents
- ✅ **Latest model** - Released late 2024, cutting-edge architecture

#### Step 3: Start Ollama Server

```bash
# Ollama runs as a service by default after installation
# But if needed, start manually:
ollama serve

# Test the server
curl http://localhost:11434/api/tags
```

#### Step 4: Install Docker (for Qdrant only)

We use Docker **ONLY** for Qdrant (vector database). Everything else runs natively.

**Windows/Mac:**
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)

**Linux:**
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect
```

#### Step 5: Start Qdrant (One Command!)

```bash
cd ai-agents

# Start Qdrant using docker-compose
docker compose up -d

# Verify Qdrant is running
curl http://localhost:6333/health

# Access Qdrant Web UI
# Open browser: http://localhost:6333/dashboard
```

**What runs in Docker:**
- ✅ Qdrant (vector database) - Docker for isolation and easy management

**What runs natively (NOT in Docker):**
- ✅ Ollama (better GPU access, faster inference)
- ✅ Python agents (easier debugging with your IDE)
- ✅ SQLite (file-based, no server needed)
- ✅ Whisper, TTS (better hardware access)

#### Step 6: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies for the entire course
pip install -r requirements.txt

# Or install per section as needed
cd 00-llm-basics
pip install -r requirements.txt
```

### Your First AI Agent (30 seconds)

```bash
# Test with curl
curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen3:8b",
  "messages": [{"role": "user", "content": "Hello! What is 2+2?"}],
  "stream": false
}'

# Or run the first example
cd 00-llm-basics
python 01_basic_chat.py
```

### Verify Your Setup

Run this quick health check:

```bash
# Check Ollama
ollama list | grep qwen3:8b

# Check Qdrant (if you started it)
curl http://localhost:6333/health

# Check Python environment
python -c "import requests; print('✅ Python setup OK')"
```

If all checks pass, you're ready to start! 🎉

---

## 💡 Key Concepts Explained

### 0. Any Software Can Use AI (It's Just REST API!)

**🔑 Critical Understanding:** You don't need Python, frameworks, or special libraries to use LLMs!

LLMs are accessed via **simple HTTP REST API calls**. This means:

```javascript
// JavaScript/Node.js
fetch('http://localhost:11434/api/chat', {
  method: 'POST',
  body: JSON.stringify({
    model: 'qwen3:8b',
    messages: [{role: 'user', content: 'Hello!'}]
  })
})

// Java
HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("http://localhost:11434/api/chat"))
    .POST(HttpRequest.BodyPublishers.ofString("{...}"))
    .build();

// C#
var client = new HttpClient();
var content = new StringContent("{...}");
var response = await client.PostAsync("http://localhost:11434/api/chat", content);

// Go
resp, err := http.Post("http://localhost:11434/api/chat", "application/json", body)

// Even curl!
curl -X POST http://localhost:11434/api/chat -d '{...}'
```

**What This Means:**
- ✅ Add AI to your **existing web app** (PHP, Ruby, Java, .NET, etc.)
- ✅ Integrate with **legacy systems** via REST calls
- ✅ Use **any HTTP client library** in any language
- ✅ No need to rewrite in Python!
- ✅ Works with **mobile apps** (iOS, Android)
- ✅ Even **Excel VBA** can call LLMs via HTTP!

**Example: Add AI to ANY Application**
```bash
# Your existing app (in ANY language) sends HTTP POST
POST http://localhost:11434/api/chat
Content-Type: application/json

{
  "model": "qwen3:8b",
  "messages": [
    {"role": "user", "content": "Summarize this document: ..."}
  ]
}

# Ollama returns JSON response
{
  "message": {
    "role": "assistant",
    "content": "Summary: ..."
  }
}
```

**We use Python in this course because:**
- Easy to learn and read
- Great debugging tools
- Rich ecosystem (LangGraph, CrewAI, etc.)

**But remember:** The REST API works from anywhere!

### 1. LLMs Are NOT Databases

```python
# ❌ WRONG MENTAL MODEL
llm.remember("My favorite color is blue")
print(llm.recall("What's my favorite color?"))  # This doesn't exist!

# ✅ CORRECT MENTAL MODEL
messages = [
    {"role": "user", "content": "My favorite color is blue"},
    {"role": "assistant", "content": "Got it!"},
    {"role": "user", "content": "What's my favorite color?"}
]
# LLM sees ALL messages each time and generates response
response = llm.chat(messages)
```

### 2. Tool Calling Is Just Structured Output

```python
# LLM doesn't "execute" tools
# It outputs JSON saying "please run this function"
{
  "function": "get_weather",
  "arguments": {"city": "Tokyo"}
}

# YOU execute the function
weather = get_weather("Tokyo")

# Then YOU send the result back to the LLM
messages.append({"role": "tool", "content": weather})
response = llm.chat(messages)
```

### 3. Recursive Tool Calling = Agent Loop

```python
while True:
    response = llm.chat(messages)

    if response.has_tool_calls():
        # Execute tools
        for tool_call in response.tool_calls:
            result = execute_tool(tool_call)
            messages.append({"role": "tool", "content": result})
        # Continue loop - LLM might call more tools!
    else:
        # LLM is done, return final answer
        return response.content
```

---

## 🛠️ Technology Stack

### The Complete Local Stack (2025 Production-Ready)

| Component | Technology | Why This Choice |
|-----------|-----------|-----------------|
| **LLM** | Qwen3:8b (Q4_K_M) | Best tool-calling model, 128K context, strong reasoning |
| **Embeddings** | nomic-embed-text | #1 local embedding model, Qdrant-optimized |
| **Vector DB** | Qdrant (Docker) | Blazing fast, HNSW, payload filtering, binary quantization |
| **Relational DB** | SQLite | Zero-config, file-based, perfect for conversation history |
| **Agent Framework** | LangGraph | Production-grade state machines, best debugging |
| **Multi-Agent** | CrewAI | Collaborative agent teams, role-based workflows |
| **Memory** | Letta (MemGPT) | Long-term memory, personality evolution |
| **Observability** | LangFuse (native) | Open-source LLM tracing, runs without Docker |
| **Speech-to-Text** | Whisper (local) | OpenAI's model, runs locally |
| **Text-to-Speech** | Coqui TTS | Local, high-quality voice synthesis |
| **Web Automation** | Playwright | Browser control for agents |
| **API Framework** | FastAPI | Modern Python web framework |
| **UI** | Streamlit/Gradio | Rapid prototyping, beautiful interfaces |

### Infrastructure Setup (Minimal Docker!)

```bash
# Start ONLY Qdrant in Docker (everything else runs natively)
cd ai-agents
docker compose up -d

# What this starts:
# - Qdrant (vector database) on :6333
#
# What runs natively:
# - Ollama (for qwen3:8b inference)
# - Python agents (for easy debugging)
# - SQLite (file-based database)
# - LangFuse (optional, runs as Python process)
```

### Why This Stack Wins

**vs ChromaDB:**
- ✅ Qdrant is faster (Rust vs Python)
- ✅ Better filtering and metadata support
- ✅ Production-ready deployment
- ✅ Binary quantization for smaller indexes

**vs PostgreSQL + pgvector:**
- ✅ SQLite is simpler (no server needed)
- ✅ Perfect for single-machine deployments
- ✅ File-based = easy backups
- ✅ Qdrant beats pgvector in pure vector search

**vs Cloud LLMs:**

| Cloud LLMs | Local (Ollama + Qwen3:8b) |
|------------|---------------------------|
| 💰 Pay per token ($0.50-$2/1M tokens) | ✅ **Free forever** |
| 🔓 Data sent to 3rd party | ✅ **100% private** |
| 🌐 Requires internet | ✅ **Works offline** |
| ⚡ Very fast (big data centers) | ⚡ **Fast enough** (5-10 tok/sec CPU, 80-120 GPU) |
| 🎯 Best quality (GPT-4) | 🎯 **Excellent quality** (beats GPT-3.5 on reasoning) |
| 🔧 API rate limits | ✅ **No limits** |
| 📊 Limited context (8-32K) | ✅ **128K context window** |

**Best Practice:** Prototype locally with this stack, deploy critical parts to cloud only if needed

### Hardware Requirements

**Minimum (CPU only):**
- 16GB RAM (12GB for model + 4GB for system)
- 4-core CPU
- 15GB disk space

**Recommended (GPU):**
- 16GB RAM
- 8-core CPU
- **NVIDIA GPU with 6GB+ VRAM** (RTX 3060, 4060 Ti, etc.)
- 50GB disk space (for models + vector indices)

**Performance Benchmarks:**

**With GPU (NVIDIA RTX 4060 Ti 16GB):**
- Qwen3:8b: ~80-120 tokens/sec ⚡
- Embedding: ~800 docs/sec
- Whisper: Real-time transcription
- **Total inference time:** ~instant feel

**CPU Only (AMD Ryzen 9 / Intel i7+):**
- Qwen3:8b: ~5-10 tokens/sec (usable for development!)
- Embedding: ~50 docs/sec
- Whisper: ~2x real-time (5min audio = 10min processing)
- **Total inference time:** 3-5 seconds for short responses

**Note:** With GPU, this feels like ChatGPT. Without GPU, it's slower but totally workable for development and learning.

---

## 📚 Learning Path Recommendations

### Path 1: Complete Beginner (30-40 hours)
```
00-llm-basics → 01-tool-calling → 02-agent-frameworks → 05-voice-gpt
```
*Skip RAG and Letta initially, focus on core agent concepts*

### Path 2: Quick to Production (15-20 hours)
```
00-llm-basics (skim) → 01-tool-calling → 02-agent-frameworks → 03-rag-systems
```
*Focus on practical agent deployment, add voice later*

### Path 3: Full Course (50-60 hours)
```
00 → 01 → 02 → 03 → 04 → 05 (in order)
```
*Deep understanding of every component*

---

## 🎯 After This Course

### You'll Be Able To:
- ✅ Build production-grade AI agents
- ✅ Integrate LLMs into existing applications
- ✅ Design complex multi-step agent workflows
- ✅ Implement RAG for custom knowledge bases
- ✅ Create voice interfaces with local models
- ✅ Debug agent behavior and fix issues
- ✅ Understand the HTTP/REST layer under frameworks

### Natural Next Steps:
1. **Fine-tuning** - Customize models for your domain (see `../fine-tuning/`)
2. **Deployment** - Host agents on your remote server (see `../perfect-setup/`)
3. **Advanced patterns** - Multi-agent systems, autonomous agents
4. **Production monitoring** - Logging, tracing, cost optimization

---

## 🤝 Contributing

Found a bug? Have improvements? Want to add examples?

1. Fork the repository
2. Create your feature branch
3. Add your examples with detailed comments
4. Submit a pull request

**Guidelines:**
- All code must be heavily commented for beginners
- Include curl examples for HTTP endpoints
- Test with Ollama local models
- Follow the "debugger-friendly" philosophy

---

## 📖 Additional Resources

### Recommended Reading Order
1. Start here: [00-llm-basics/README.md](./00-llm-basics/README.md)
2. Understand tools: [01-tool-calling/README.md](./01-tool-calling/README.md)
3. Build complex agents: [02-agent-frameworks/README.md](./02-agent-frameworks/README.md)
4. Add knowledge: [03-rag-systems/README.md](./03-rag-systems/README.md)
5. Add memory: [04-memory-systems/README.md](./04-memory-systems/README.md)
6. Final project: [05-voice-gpt/README.md](./05-voice-gpt/README.md)

### External Resources
- [Ollama Documentation](https://github.com/ollama/ollama)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Letta (MemGPT) Documentation](https://github.com/cpacker/MemGPT)
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)

---

## 📫 Connect

**Beyhan MEYRALI**
- 💼 [LinkedIn](https://www.linkedin.com/in/beyhanmeyrali/)
- 🐙 [GitHub](https://github.com/beyhanmeyrali)

---

## 📄 License

MIT License - See [LICENSE](../LICENSE) file for details.

---

**Ready to begin?** Start with [00-llm-basics](./00-llm-basics/README.md) →

*"The best way to understand AI is to build it yourself."*
