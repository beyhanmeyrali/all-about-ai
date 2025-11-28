# LangChain: Foundation Agent Framework 🔗

> Master the fundamentals of LLM agents with LangChain

---

## 🎯 What You'll Learn

LangChain is the **foundational framework** for building LLM applications. It provides:

- 🔗 **Chains** - Connect LLM calls together
- 📝 **Prompts** - Dynamic prompt templates
- 🧠 **Memory** - Conversation history management
- 🛠️ **Tools** - Give agents capabilities
- 🔄 **Sequences** - Multi-step workflows

**Time Required:** 4-5 hours

---

## 📂 Files in This Section

```
langchain/
├── README.md                    ← You are here
├── 00_installation.py          ← Verify setup
├── 01_basic_chain.py           ← Your first chain
├── 02_prompt_templates.py      ← Dynamic prompts
├── 03_chains_with_memory.py    ← Conversation memory
├── 04_tools_integration.py     ← Tool-calling agents
├── 05_sequential_chains.py     ← Multi-step workflows
├── 06_router_chains.py         ← Conditional routing
└── 07_production_agent.py      ← Complete agent system
```

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install langchain langchain-ollama langchain-core requests

# Verify Ollama
ollama list  # Should show qwen3:8b

# Run first example
python 01_basic_chain.py
```

---

## 📖 Progressive Learning Path

### 00 - Installation & Setup
**Concept:** Verify everything works
**You'll learn:** Testing Ollama + LangChain integration

### 01 - Basic Chain
**Concept:** Simple LLM call
**You'll learn:** LLMChain, basic prompts, running chains

### 02 - Prompt Templates
**Concept:** Dynamic prompts with variables
**You'll learn:** PromptTemplate, variable substitution, reusable prompts

### 03 - Chains with Memory
**Concept:** Remember conversation history
**You'll learn:** ConversationBufferMemory, ConversationChain, context management

### 04 - Tools Integration
**Concept:** Give agents capabilities
**You'll learn:** Tool schemas, AgentExecutor, tool calling

### 05 - Sequential Chains
**Concept:** Multi-step workflows
**You'll learn:** SequentialChain, passing data between chains, complex workflows

### 06 - Router Chains
**Concept:** Conditional routing
**You'll learn:** RouterChain, LLMRouterChain, dynamic routing based on input

### 07 - Production Agent
**Concept:** Enterprise-grade agent
**You'll learn:** Error handling, logging, monitoring, best practices

---

## 🧩 Key Concepts

### What is a Chain?

A **chain** is a sequence of calls to LLMs or other utilities:

```python
# Simple chain
Prompt → LLM → Output

# Sequential chain
Prompt1 → LLM1 → Prompt2 → LLM2 → Output

# Tool chain
Prompt → LLM → Tool Call → Tool Result → LLM → Output
```

### Why Use Chains?

**Without chains:**
```python
# Messy, hard to maintain
response1 = requests.post(...)
data = parse(response1)
response2 = requests.post(...format(data)...)
result = parse(response2)
```

**With chains:**
```python
# Clean, reusable
chain = PromptTemplate | LLM | OutputParser
result = chain.invoke({"input": "question"})
```

---

## 🔑 Core Components

### 1. LLMs (Language Models)

```python
from langchain_ollama import OllamaLLM

llm = OllamaLLM(
    model="qwen3:8b",
    temperature=0.7
)

response = llm.invoke("Hello!")
```

### 2. Prompts

```python
from langchain.prompts import PromptTemplate

prompt = PromptTemplate(
    template="Tell me about {topic}",
    input_variables=["topic"]
)

formatted = prompt.format(topic="AI")
# "Tell me about AI"
```

### 3. Chains

```python
from langchain.chains import LLMChain

chain = LLMChain(
    llm=llm,
    prompt=prompt
)

result = chain.run(topic="Python")
```

### 4. Memory

```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

memory = ConversationBufferMemory()
conversation = ConversationChain(
    llm=llm,
    memory=memory
)

# First message
conversation.run("My name is John")
# "Nice to meet you, John!"

# Second message - remembers!
conversation.run("What's my name?")
# "Your name is John"
```

### 5. Tools

```python
from langchain.tools import Tool

def get_weather(city: str) -> str:
    return f"Weather in {city}: Sunny, 25°C"

weather_tool = Tool(
    name="get_weather",
    func=get_weather,
    description="Get weather for a city"
)
```

---

## 🎓 Learning Objectives

By the end of this section, you will:

1. ✅ Understand what chains are and when to use them
2. ✅ Build dynamic prompts with variables
3. ✅ Manage conversation memory
4. ✅ Integrate tools with agents
5. ✅ Create multi-step sequential workflows
6. ✅ Implement conditional routing
7. ✅ Build production-ready agents

---

## 🔄 Progressive Complexity

```
01_basic_chain.py
   ↓ Add dynamic prompts
02_prompt_templates.py
   ↓ Add memory
03_chains_with_memory.py
   ↓ Add tools
04_tools_integration.py
   ↓ Add sequential steps
05_sequential_chains.py
   ↓ Add routing logic
06_router_chains.py
   ↓ Add production features
07_production_agent.py
```

---

## 🐛 Common Issues & Solutions

### Issue 1: Import Errors

```bash
# Error: No module named 'langchain'
pip install langchain langchain-ollama

# Error: Cannot import OllamaLLM
pip install --upgrade langchain-ollama
```

### Issue 2: Ollama Connection

```python
# Test Ollama connection
import requests
response = requests.get("http://localhost:11434/api/tags")
print(response.status_code)  # Should be 200
```

### Issue 3: Chain Not Working

```python
# Enable verbose mode to see what's happening
chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
```

---

## 📊 LangChain vs Others

| Feature | LangChain | LangGraph | CrewAI |
|---------|-----------|-----------|--------|
| Learning Curve | Easy ✅ | Moderate | Moderate |
| Best For | Simple chains | Complex workflows | Multi-agent |
| Setup Time | 5 min | 10 min | 15 min |
| Memory | Built-in ✅ | Manual | Built-in |
| Tools | Easy ✅ | Manual | Easy |
| Routing | Limited | Excellent | Good |

---

## 🎯 When to Use LangChain

**Use LangChain when:**
- ✅ Building your first agent
- ✅ Simple conversational AI
- ✅ Quick prototypes
- ✅ Learning fundamentals
- ✅ Sequential workflows

**Don't use LangChain when:**
- ❌ Complex state management needed → Use LangGraph
- ❌ Multi-agent systems → Use CrewAI
- ❌ Need graph visualization → Use LangGraph

---

## 🚀 Next Steps

After completing this section:

1. Move to **LangGraph** for complex workflows
2. Or jump to **CrewAI** for multi-agent systems
3. Or continue to **03-embeddings-rag** for knowledge retrieval

---

## 📚 Resources

- [LangChain Docs](https://python.langchain.com/)
- [LangChain GitHub](https://github.com/langchain-ai/langchain)
- [Ollama Integration](https://python.langchain.com/docs/integrations/llms/ollama)

---

**Ready to start?** Run `python 01_basic_chain.py` →
