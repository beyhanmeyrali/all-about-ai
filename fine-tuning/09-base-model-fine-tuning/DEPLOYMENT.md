# Uncensored Qwen3-0.6B Model - Deployment Guide

## ✅ COMPLETED - Full Pipeline

We successfully created an uncensored instruction-following model from Qwen3-0.6B-Base through the complete fine-tuning pipeline.

### Training Results
- **Model:** Qwen3-0.6B-Base → Uncensored Instruction Model
- **Training Time:** 4 hours 39 minutes (CPU-only due to RTX 5060 sm_120 incompatibility)
- **Dataset:** 5,000 conversations from OpenHermes-2.5
- **Loss Improvement:** 41% (1.23 → 0.73)
- **LoRA Parameters:** 10M trainable (1.67% of 600M total)

### Output Files
```
qwen3-0.6b-uncensored-lora/        54MB  - LoRA adapter weights
qwen3-0.6b-uncensored-merged/      1.15GB - Merged full model (FP16)
```

---

## 🚀 Deployment Methods

### Method 1: API Server (RECOMMENDED - Working Now!)

Since Ollama doesn't support Qwen3 architecture yet, we created a Flask API server with Ollama-compatible endpoints.

**Start the server:**
```bash
cd /workspace/all-about-ai/fine-tuning/09-base-model-fine-tuning
python3 07_serve_model_api.py
```

**Test with curl:**
```bash
# Simple generation
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is 2+2?"}'

# Chat with conversation history
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Explain quantum physics"}
    ]
  }'

# List available models
curl http://localhost:5000/api/tags
```

**API Endpoints:**
- `POST /api/generate` - Generate text from prompt
- `POST /api/chat` - Chat with messages array
- `GET /api/tags` - List available models

**Request Parameters:**
```json
{
  "prompt": "Your question here",
  "max_tokens": 500,        // default: 500
  "temperature": 0.7,       // default: 0.7
  "top_p": 0.9             // default: 0.9
}
```

---

### Method 2: Direct Python Usage

**Test script (already working):**
```bash
python3 06_test_uncensored.py
```

**Use in your own Python code:**
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

---

### Method 3: Ollama (Future - When Qwen3 Support Added)

**Current Status:** ❌ Ollama doesn't support Qwen3ForCausalLM architecture yet

**Error received:**
```
Error: unsupported architecture "Qwen3ForCausalLM"
```

**When Qwen3 support is added to Ollama:**
```bash
# Convert to GGUF (llama.cpp required)
python3 /tmp/llama.cpp/convert-hf-to-gguf.py qwen3-0.6b-uncensored-merged \
  --outfile qwen3-uncensored.gguf \
  --outtype q4_k

# Create Ollama model
ollama create qwen3-uncensored -f Modelfile-0.6b

# Run
ollama run qwen3-uncensored "What is 2+2?"
```

---

## 📊 Model Performance

**Test Results (all successful):**
- ✅ Basic math: Correct answers
- ✅ Instruction following: Detailed step-by-step guides
- ✅ Political discussions: Unbiased explanations
- ✅ Historical analysis: Comprehensive responses

**Before Training (Base Model):**
- Input: "What is 2+2?"
- Output: "What is 2+2? It's a simple math problem..." (continues text)
- **Problem:** Doesn't understand it's a question to answer

**After Training (Our Model):**
- Input: "What is 2+2?"
- Output: "The answer is 4. This is because when you add two numbers..."
- **Success:** Understands and directly answers the question

---

## 🔧 Technical Details

### Model Architecture
- **Base:** Qwen3-0.6B-Base (600M parameters)
- **Fine-Tuning:** LoRA (rank=16, alpha=32, dropout=0.05)
- **Target Modules:** q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj
- **Format:** FP16 (float16)

### Training Configuration
- **Device:** CPU (20 cores)
- **Batch Size:** 4 per device
- **Gradient Accumulation:** 4 steps (effective batch = 16)
- **Learning Rate:** 2e-4 with linear decay
- **Max Steps:** 200
- **Sequence Length:** 512 tokens

### Hardware Compatibility
- **RTX 5060:** ❌ sm_120 not supported by PyTorch (trained on CPU instead)
- **CPU Training:** ✅ Working (slow but functional)
- **RAM Requirements:** 16GB+ recommended (worked with 15GB)

---

## 📝 Usage Examples

**Example 1: Simple Question**
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What are the main benefits of renewable energy?"}'
```

**Example 2: Technical Explanation**
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain how neural networks learn"}'
```

**Example 3: Political Discussion**
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Compare different economic systems"}'
```

---

## 🎯 Key Achievements

1. ✅ **Trained uncensored model** - No safety restrictions
2. ✅ **Overcame hardware limitations** - CPU training workaround for RTX 5060
3. ✅ **Fixed multiple technical issues** - TRL API, data collator, dependencies
4. ✅ **Created working API server** - Ollama-style endpoints
5. ✅ **Full documentation** - Complete pipeline with examples

---

## 📚 File Reference

| File | Purpose |
|------|---------|
| `02_train_uncensored_qwen3_0.6b_cpu_v2.py` | Training script (working version) |
| `03_merge_lora_0.6b.py` | Merge LoRA with base model |
| `06_test_uncensored.py` | Test with multiple prompts |
| `07_serve_model_api.py` | Flask API server |
| `Modelfile-0.6b` | Ollama config (for future use) |
| `qwen3-0.6b-uncensored-merged/` | Final merged model |

---

## 🔮 Future Improvements

1. **GGUF Conversion:** When llama.cpp adds Qwen3 support
2. **Ollama Deployment:** When Ollama adds Qwen3 architecture support
3. **GPU Training:** When PyTorch supports sm_120 (Blackwell)
4. **Larger Models:** Train Qwen3-1.7B or 4B versions
5. **Extended Training:** More epochs for even better performance

---

## Sources

- [GGUF and Transformers Documentation](https://huggingface.co/docs/transformers/en/gguf)
- [Convert HuggingFace to GGUF Tutorial](https://github.com/ggml-org/llama.cpp/discussions/2948)
- [Transformers GGUF Guide](https://www.geeksforgeeks.org/machine-learning/how-to-convert-any-huggingface-model-to-gguf-file-format/)

---

**Model Ready for Use!**
Start the API server: `python3 07_serve_model_api.py`
