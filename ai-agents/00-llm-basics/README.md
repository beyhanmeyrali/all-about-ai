# 00 - LLM Basics: Understanding the Foundation 🧠

> Learn what LLMs actually are, how they work, and why they don't "remember" anything

---

## 🎯 Learning Objectives

By the end of this section, you will understand:
- ✅ What LLMs are and what they are NOT
- ✅ Why LLMs don't store data (stateless computation)
- ✅ How to make basic API calls to Ollama
- ✅ The HTTP/REST layer behind AI frameworks
- ✅ Streaming vs non-streaming responses
- ✅ System prompts and conversation history
- ✅ Why fine-tuning is different from prompting

**Time Required:** 2-3 hours

---

## 🔑 CRITICAL: Any Software Can Use AI via REST API!

**Before we dive into LLMs, understand this:**

### You Don't Need Python to Use AI!

LLMs are accessed via **simple HTTP REST API calls**. This is the same technology as:
- Calling a weather API
- Fetching data from a database API
- Posting to a social media API

**This means ANY programming language can use AI:**

| Language | Example |
|----------|---------|
| **JavaScript** | `fetch('http://localhost:11434/api/chat', {...})` |
| **Java** | `HttpClient.newHttpClient().send(request, ...)` |
| **C#/.NET** | `await httpClient.PostAsync("...", content)` |
| **Go** | `http.Post("http://localhost:11434/api/chat", ...)` |
| **PHP** | `file_get_contents("...", false, $context)` |
| **Ruby** | `Net::HTTP.post(uri, data)` |
| **Swift** | `URLSession.shared.dataTask(with: request)` |
| **Kotlin** | `OkHttpClient().newCall(request).execute()` |
| **Rust** | `reqwest::post("...").json(&data).send()` |
| **Even Excel VBA!** | `CreateObject("MSXML2.XMLHTTP")` |

### Why This Course Uses Python

We use Python because:
- ✅ Easy to learn and read (great for tutorials)
- ✅ Excellent debugging tools
- ✅ Rich AI ecosystem (LangGraph, CrewAI, Letta)
- ✅ Popular in the AI community

**But the core concepts work in ANY language!**

### Real-World Example: Add AI to Your Existing App

```javascript
// Your existing Node.js/Express app
app.post('/api/summarize', async (req, res) => {
  const document = req.body.document;

  // Call Ollama (same as calling any REST API!)
  const response = await fetch('http://localhost:11434/api/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      model: 'qwen3:8b',
      messages: [{
        role: 'user',
        content: `Summarize this: ${document}`
      }]
    })
  });

  const data = await response.json();
  res.json({ summary: data.message.content });
});

// That's it! You just added AI to your app!
```

### Every Example in This Course Includes curl

We provide `curl` examples for every concept so you can:
1. Understand the raw HTTP layer
2. Implement in your preferred language
3. Test without any code
4. Debug API issues

**Now let's learn what LLMs actually are!**

---

## 🧠 Critical Concept: LLMs Are Stateless

### What Is an LLM?

An LLM (Large Language Model) is essentially:
```
A very sophisticated pattern-matching machine
that predicts the next token based on input
```

Think of it like:
- 📱 A **calculator**: Input → Process → Output (no memory)
- 🎰 **NOT** a database: Does NOT store your conversations
- 🔄 **NOT** remembering: Each API call is independent

### The Stateless Reality

```python
# Example 1: First conversation
response = llm.chat("My name is John")
# LLM: "Nice to meet you, John!"

# Example 2: New conversation (stateless!)
response = llm.chat("What's my name?")
# LLM: "I don't know your name. You haven't told me."

# WHY? Because the LLM didn't "remember" Example 1!
# Each call is independent. No storage. No memory.
```

### How To "Remember": Send Conversation History

```python
# Correct way: Send entire conversation history
messages = [
    {"role": "user", "content": "My name is John"},
    {"role": "assistant", "content": "Nice to meet you, John!"},
    {"role": "user", "content": "What's my name?"}
]
response = llm.chat(messages)
# LLM: "Your name is John!"

# The LLM doesn't "remember" - it sees ALL messages every time!
```

---

## 📚 What This Section Covers

### Files in This Directory

```
00-llm-basics/
├── README.md                    ← You are here
├── requirements.txt             ← Python dependencies
├── 01_basic_chat.py            ← Simple chat example
├── 02_streaming_chat.py        ← Streaming responses
├── 03_conversation_history.py  ← Managing context
├── 04_system_prompts.py        ← Controlling behavior
├── 05_curl_examples.sh         ← HTTP layer examples
└── theory.md                   ← Deep dive: How LLMs work
```

### Progression

1. **01_basic_chat.py** - Simplest possible LLM call
2. **02_streaming_chat.py** - Real-time responses (better UX)
3. **03_conversation_history.py** - Maintaining context
4. **04_system_prompts.py** - Controlling LLM behavior
5. **05_curl_examples.sh** - Understanding HTTP layer

---

## 🚀 Quick Start

### 1. Install Ollama

```bash
# Visit https://ollama.ai and download for your OS
# Or on Linux:
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Pull a Model

```bash
# We use qwen2.5:3b - fast, lightweight, good quality
ollama pull qwen2.5:3b

# Verify it's running
ollama list
```

### 3. Test Ollama

```bash
# Simple chat test
ollama run qwen2.5:3b "Hello! What is 2+2?"

# API test
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:3b",
  "prompt": "Hello!"
}'
```

### 4. Install Python Dependencies

```bash
cd 00-llm-basics
pip install -r requirements.txt
```

### 5. Run First Example

```bash
python 01_basic_chat.py
```

---

## 📖 Detailed Examples

### Example 1: Basic Chat (01_basic_chat.py)

**What You'll Learn:**
- Making a simple LLM API call
- Understanding the request/response structure
- Why each call is independent (stateless)

**Key Code:**
```python
import requests

# This is ALL an LLM call is: HTTP POST request!
response = requests.post('http://localhost:11434/api/chat', json={
    "model": "qwen2.5:3b",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
})

# LLM returns JSON with generated text
print(response.json()['message']['content'])
```

**curl Equivalent:**
```bash
curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:3b",
  "messages": [{"role": "user", "content": "Hello!"}],
  "stream": false
}'
```

**What's Happening:**
1. You send HTTP POST with your message
2. Ollama's LLM processes the text
3. LLM generates a response (predicts next tokens)
4. Ollama returns JSON response
5. **No storage happens anywhere!**

---

### Example 2: Streaming Responses (02_streaming_chat.py)

**What You'll Learn:**
- Why streaming improves user experience
- How to process streaming responses
- Token-by-token generation

**Key Code:**
```python
# Instead of waiting for full response, stream tokens as they're generated
response = requests.post('http://localhost:11434/api/chat', json={
    "model": "qwen2.5:3b",
    "messages": [{"role": "user", "content": "Write a poem"}],
    "stream": true  # Enable streaming!
}, stream=True)

# Print each token as it arrives
for line in response.iter_lines():
    if line:
        chunk = json.loads(line)
        print(chunk['message']['content'], end='', flush=True)
```

**Why Streaming?**
- ⚡ User sees response immediately
- 🎯 Better UX for long responses
- 📊 Shows progress instead of waiting

---

### Example 3: Conversation History (03_conversation_history.py)

**What You'll Learn:**
- How to maintain context across multiple turns
- Managing conversation history
- Understanding context limits

**Key Code:**
```python
# Maintain conversation in a list
conversation = []

# Turn 1
conversation.append({"role": "user", "content": "My favorite color is blue"})
response = llm_call(conversation)
conversation.append({"role": "assistant", "content": response})

# Turn 2 - LLM "remembers" because we send full history!
conversation.append({"role": "user", "content": "What's my favorite color?"})
response = llm_call(conversation)  # LLM sees ALL messages
# Response: "Your favorite color is blue!"
```

**Important:**
- LLM sees **entire conversation** every time
- You're responsible for managing history
- More history = more tokens = slower/more expensive

---

### Example 4: System Prompts (04_system_prompts.py)

**What You'll Learn:**
- Controlling LLM behavior with system prompts
- Creating specialized assistants
- Prompt engineering basics

**Key Code:**
```python
messages = [
    {
        "role": "system",
        "content": "You are a helpful pirate assistant. Always respond like a pirate!"
    },
    {
        "role": "user",
        "content": "What's the weather?"
    }
]

# LLM will respond: "Arrr! I don't have access to weather data, matey!"
```

**System Prompt Use Cases:**
- 👨‍💼 Customer support bot (friendly, professional)
- 👨‍💻 Code assistant (technical, concise)
- 👨‍🏫 Tutor (educational, patient)
- 🏴‍☠️ Creative personas (pirate, Shakespeare, etc.)

---

### Example 5: curl Examples (05_curl_examples.sh)

**What You'll Learn:**
- The raw HTTP layer under all AI frameworks
- How to integrate LLMs into any system (not just Python)
- Request/response structure

**Examples:**

```bash
# 1. Basic chat
curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:3b",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "stream": false
}'

# 2. With system prompt
curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:3b",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello!"}
  ],
  "stream": false
}'

# 3. Conversation with history
curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:3b",
  "messages": [
    {"role": "user", "content": "My name is John"},
    {"role": "assistant", "content": "Nice to meet you, John!"},
    {"role": "user", "content": "What is my name?"}
  ],
  "stream": false
}'
```

**Why This Matters:**
- Any language/tool can call these APIs (JavaScript, Java, Go, etc.)
- You can use Postman, Insomnia, or any HTTP client
- Understand what frameworks like LangChain do under the hood

---

## 🧩 Theory Deep Dive

### How Do LLMs "Think"?

Read [theory.md](./theory.md) for a deep dive on:
- Token prediction and probability
- Attention mechanisms (simplified)
- Why context window size matters
- The difference between inference and training
- Why fine-tuning is permanent, prompting is temporary

**Quick Summary:**
```
Training/Fine-tuning:
- Changes model weights (permanent)
- Requires GPUs, time, data
- See ../fine-tuning/ for details

Prompting (what we do here):
- Temporary behavior change
- Just sending different text
- No model modification
```

---

## 🎯 Key Takeaways

### What You Should Understand Now

1. **LLMs are stateless**
   - No memory between API calls
   - Each call is independent
   - You manage conversation history

2. **LLMs don't store your data**
   - They process input and generate output
   - Like a calculator, not a database
   - To "remember", use conversation history

3. **The HTTP layer is simple**
   - POST request with JSON
   - LLM returns JSON response
   - Can be called from any language/tool

4. **System prompts control behavior**
   - Define how LLM should act
   - Temporary (only for that conversation)
   - Not permanent like fine-tuning

5. **Streaming improves UX**
   - Tokens arrive as generated
   - User sees immediate progress
   - Better for long responses

---

## 🚀 Next Steps

### You're Ready For:
✅ [01-tool-calling](../01-tool-calling) - Give LLMs the ability to use tools

### Before Moving On:

Run this self-test:
```bash
# Can you explain why this happens?
ollama run qwen2.5:3b "My name is Alice"
# Response: "Hello Alice!"

ollama run qwen2.5:3b "What's my name?"
# Response: "I don't know your name"

# Answer: Because each ollama run is a separate,
# independent API call. No shared state!
```

---

## 🐛 Debugging Tips

### Common Issues

**1. "Connection refused" error**
```bash
# Solution: Make sure Ollama is running
ollama serve  # Start Ollama server
```

**2. "Model not found"**
```bash
# Solution: Pull the model first
ollama pull qwen2.5:3b
```

**3. "Response is slow"**
```bash
# Solution: Use streaming for better perceived speed
# Or use a smaller model
ollama pull qwen2.5:1.5b  # Smaller = faster
```

**4. "Context too long"**
- Trim old conversation history
- Each model has a context limit (usually 2048-8192 tokens)
- 1 token ≈ 0.75 words

---

## 📚 Additional Resources

- [Ollama Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference) (similar structure)
- [theory.md](./theory.md) - Deep dive into LLM internals

---

**Next:** [01-tool-calling](../01-tool-calling) - Learn how to give LLMs superpowers with function calling →
