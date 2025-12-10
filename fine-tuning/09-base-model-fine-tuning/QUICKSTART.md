# ⚡ Quick Start Guide - Uncensored Qwen3-0.6B Model

This is a **5-minute quick start** to use the already-trained uncensored model.

---

## ✅ Model Status: READY TO USE

**Model Location**: `qwen3-0.6b-uncensored-merged/` (1.15GB)
**Ollama Deployment**: ✅ WORKING (`qwen3-uncensored:latest`)
**API Server**: Available on port 5000
**Training**: Complete (4h 39min CPU training)
**Testing**: All tests passed ✅

---

## 🚀 Option 1: Use with Ollama (RECOMMENDED - Native)

The model is successfully deployed to Ollama using GGUF format conversion via [llama.cpp](https://github.com/ggerganov/llama.cpp) by @ggerganov.

### Quick Start
```bash
# Run the model
ollama run qwen3-uncensored

# Or single query
ollama run qwen3-uncensored "What is 2+2?"
```

### API Usage
```bash
curl -X POST http://localhost:11434/api/generate \
  -d '{
    "model": "qwen3-uncensored",
    "prompt": "Explain quantum physics",
    "stream": false
  }'
```

### How It Was Deployed
The model was converted to GGUF format using llama.cpp's converter:
```bash
# Conversion (already done)
python3 /tmp/llama.cpp/convert_hf_to_gguf.py \
  ./qwen3-0.6b-uncensored-merged \
  --outfile qwen3-uncensored-f16.gguf \
  --outtype f16

# Deployment (already done)
ollama create qwen3-uncensored -f Modelfile-uncensored
```

**Credit**: Thanks to [llama.cpp](https://github.com/ggerganov/llama.cpp) by @ggerganov for the GGUF converter that made Ollama deployment possible!

---

## 🐍 Option 2: Use API Server (Alternative)

### Start the Server
```bash
cd /workspace/all-about-ai/fine-tuning/09-base-model-fine-tuning
python3 07_serve_model_api.py
```

### Test with curl
```bash
# Simple question
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is 2+2?"}'

# More complex query
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain quantum physics in simple terms", "max_tokens": 500}'

# Chat with conversation
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What are the benefits of AI?"}
    ]
  }'
```

### Expected Response Format
```json
{
  "done": true,
  "model": "qwen3-0.6b-uncensored",
  "response": "2+2 = 4."
}
```

---

## 🐍 Option 3: Direct Python Usage

### Simple Example
```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load model
tokenizer = AutoTokenizer.from_pretrained(
    "qwen3-0.6b-uncensored-merged",
    trust_remote_code=True
)

model = AutoModelForCausalLM.from_pretrained(
    "qwen3-0.6b-uncensored-merged",
    device_map="cpu",
    torch_dtype=torch.float16,
    trust_remote_code=True,
)

# Generate response
messages = [{"role": "user", "content": "What is 2+2?"}]
text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(text, return_tensors="pt")

outputs = model.generate(**inputs, max_new_tokens=200, temperature=0.7)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)
```

### Run Existing Test Script
```bash
cd /workspace/all-about-ai/fine-tuning/09-base-model-fine-tuning
python3 06_test_uncensored.py
```

This will test the model with 4 different prompts and show results.

---

## 📊 What You Get

### Test Results (From 06_test_uncensored.py)

**Test 1: Basic Math**
- Prompt: "What is 2+2?"
- Response: "2 + 2 = 4." ✅

**Test 2: Instruction Following**
- Prompt: "Explain how to make a cake"
- Response: Detailed step-by-step recipe (8 steps) ✅

**Test 3: Political Discussion**
- Prompt: "What are the main differences between democracy and authoritarianism?"
- Response: Comprehensive comparison with 4 key points ✅

**Test 4: Historical Analysis**
- Prompt: "Explain the historical context of World War II"
- Response: Detailed historical overview with timeline ✅

---

## 🔧 API Parameters

### /api/generate
```json
{
  "prompt": "Your question here",
  "max_tokens": 500,        // default: 500
  "temperature": 0.7,       // default: 0.7
  "top_p": 0.9             // default: 0.9
}
```

### /api/chat
```json
{
  "messages": [
    {"role": "user", "content": "Your question"}
  ],
  "max_tokens": 500,
  "temperature": 0.7,
  "top_p": 0.9
}
```

### /api/tags
```bash
curl http://localhost:5000/api/tags
```

Returns list of available models (just qwen3-0.6b-uncensored).

---

## 📁 Project Structure

```
09-base-model-fine-tuning/
├── qwen3-0.6b-uncensored-merged/   # Final model (USE THIS)
├── qwen3-0.6b-uncensored-lora/      # LoRA adapter only
├── 07_serve_model_api.py            # API server (RUN THIS)
├── 06_test_uncensored.py            # Test script
├── README.md                        # Complete documentation (1,687 lines)
├── DEPLOYMENT.md                    # Deployment guide
├── STATUS.md                        # Project status
└── QUICKSTART.md                    # This file
```

---

## 🎯 Common Use Cases

### 1. Interactive Chat
```bash
# Start API server
python3 07_serve_model_api.py

# In another terminal, send queries
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Tell me about artificial intelligence"}'
```

### 2. Batch Processing
```python
import requests

prompts = [
    "What is machine learning?",
    "Explain neural networks",
    "What are transformers in AI?"
]

for prompt in prompts:
    response = requests.post(
        "http://localhost:5000/api/generate",
        json={"prompt": prompt}
    )
    print(f"Q: {prompt}")
    print(f"A: {response.json()['response']}\n")
```

### 3. Custom Applications
```python
# Use the model in your Python application
from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("qwen3-0.6b-uncensored-merged", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("qwen3-0.6b-uncensored-merged", device_map="cpu", torch_dtype="float16", trust_remote_code=True)

def ask_model(question):
    messages = [{"role": "user", "content": question}]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=200)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
```

---

## 🚨 Important Notes

1. **CPU-Only**: Model trained on CPU (RTX 5060 sm_120 incompatible with PyTorch)
2. **Multilingual Output**: May include Thai/Arabic characters (from training data)
3. **Uncensored**: No safety restrictions applied
4. **Response Time**: ~5-15 seconds per query on CPU
5. **Memory Usage**: ~2GB RAM during inference

---

## ❌ Ollama Deployment (Not Available Yet)

**Status**: Ollama doesn't support Qwen3ForCausalLM architecture yet

**Error**: `Error: unsupported architecture "Qwen3ForCausalLM"`

**Workaround**: Use the Flask API server instead (works perfectly)

**Future**: When Ollama adds Qwen3 support, convert to GGUF and deploy

---

## 📚 Need More Details?

- **Full Documentation**: See `README.md` (1,687 lines with diagrams)
- **Deployment Guide**: See `DEPLOYMENT.md` (all deployment methods)
- **Project Status**: See `STATUS.md` (complete project summary)

---

## 🎉 You're Ready!

The model is trained, tested, and ready to use. Just start the API server and send queries!

```bash
# Terminal 1: Start server
python3 07_serve_model_api.py

# Terminal 2: Send test query
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, can you help me?"}'
```

**Enjoy your uncensored AI model!** 🚀
