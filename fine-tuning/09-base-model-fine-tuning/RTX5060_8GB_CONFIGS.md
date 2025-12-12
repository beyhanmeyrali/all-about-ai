# RTX 5060 8GB - Optimal Fine-Tuning Configurations

## ✅ System Verified

Your setup is working perfectly:
- **GPU**: NVIDIA GeForce RTX 5060 Laptop (8GB VRAM)
- **Architecture**: Blackwell (sm_120)
- **Driver**: 591.44
- **CUDA**: 12.8
- **PyTorch**: 2.9.1+cu128

## 🚀 Activation Command

Every time you want to use PyTorch with your RTX 5060:

```bash
source ~/pytorch-rtx5060/bin/activate
```

## 📊 Recommended Model Configurations for 8GB VRAM

### Small Models (0.6B - 2B) - Full Precision

**Best for learning and fast iteration:**

```python
SMALL_MODEL_CONFIG = {
    "model_name": "Qwen/Qwen3-0.6B-Instruct",  # or 1.7B
    "per_device_train_batch_size": 8,
    "gradient_accumulation_steps": 2,
    "max_seq_length": 2048,
    "bits": 16,  # Full precision
    "learning_rate": 2e-4,
    "num_train_epochs": 3,
    "lora_r": 16,
    "lora_alpha": 32,
}
```

**Training time**: 15-30 minutes
**Memory usage**: ~3-4GB VRAM
**Quality**: Excellent for domain-specific tasks

### Medium Models (7B) - 4-bit Quantization

**Best for production use:**

```python
MEDIUM_MODEL_CONFIG = {
    "model_name": "meta-llama/Llama-2-7b-hf",  # or Mistral-7B, CodeLlama-7B
    "per_device_train_batch_size": 2,
    "gradient_accumulation_steps": 8,
    "max_seq_length": 1024,
    "bits": 4,  # 4-bit quantization
    "double_quant": True,
    "quant_type": "nf4",
    "learning_rate": 1e-4,
    "num_train_epochs": 2,
    "lora_r": 32,
    "lora_alpha": 64,
}
```

**Training time**: 1-2 hours
**Memory usage**: ~6-7GB VRAM
**Quality**: Very good, production-ready

### Large Models (13B) - Aggressive Optimization

**For advanced users:**

```python
LARGE_MODEL_CONFIG = {
    "model_name": "meta-llama/Llama-2-13b-hf",
    "per_device_train_batch_size": 1,
    "gradient_accumulation_steps": 16,
    "max_seq_length": 512,
    "bits": 4,
    "double_quant": True,
    "quant_type": "nf4",
    "learning_rate": 5e-5,
    "num_train_epochs": 1,
    "lora_r": 16,
    "lora_alpha": 32,
    "gradient_checkpointing": True,
}
```

**Training time**: 2-4 hours
**Memory usage**: ~7.5GB VRAM
**Quality**: Good, requires careful tuning

## 🎯 Memory Management Strategies

### Strategy 1: Conservative (Most Stable)

```python
config = {
    "per_device_train_batch_size": 2,
    "gradient_accumulation_steps": 4,
    "max_seq_length": 1024,
    "bits": 4,
}
```

**Effective batch size**: 8
**Works for**: Most 7B models
**VRAM usage**: ~6GB

### Strategy 2: Balanced (Recommended)

```python
config = {
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 4,
    "max_seq_length": 2048,
    "bits": 4 if model_size > 2e9 else 16,
}
```

**Effective batch size**: 16
**Works for**: 0.6B-7B models
**VRAM usage**: ~4-7GB

### Strategy 3: Aggressive (Maximum Model Size)

```python
config = {
    "per_device_train_batch_size": 1,
    "gradient_accumulation_steps": 16,
    "max_seq_length": 512,
    "bits": 4,
    "double_quant": True,
    "gradient_checkpointing": True,
}
```

**Effective batch size**: 16
**Works for**: Up to 13B models
**VRAM usage**: ~7.5GB

## 📝 Complete Training Example

### Quick Start with Qwen3 0.6B (15 minutes)

```python
from unsloth import FastLanguageModel

# Load model with 8GB-optimized settings
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="Qwen/Qwen3-0.6B-Instruct",
    max_seq_length=2048,
    dtype=None,  # Auto-detect
    load_in_4bit=False,  # Full precision for small models
)

# Apply LoRA
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
)

# Training arguments
from transformers import TrainingArguments

training_args = TrainingArguments(
    per_device_train_batch_size=8,
    gradient_accumulation_steps=2,
    num_train_epochs=3,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=10,
    output_dir="outputs",
)
```

### Production 7B Model (1-2 hours)

```python
from unsloth import FastLanguageModel
from transformers import TrainingArguments

# Load with 4-bit quantization
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="meta-llama/Llama-2-7b-hf",
    max_seq_length=1024,
    dtype=None,
    load_in_4bit=True,  # Critical for 8GB VRAM
)

# LoRA configuration
model = FastLanguageModel.get_peft_model(
    model,
    r=32,
    lora_alpha=64,
    lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
)

# Optimized training args for 8GB
training_args = TrainingArguments(
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    num_train_epochs=2,
    learning_rate=1e-4,
    fp16=True,
    optim="paged_adamw_8bit",  # Memory-efficient optimizer
    logging_steps=10,
    save_steps=100,
    output_dir="outputs",
)
```

## ⚠️ Common Issues and Solutions

### Issue 1: Out of Memory (OOM)

**Solution:**
```python
# Reduce batch size
per_device_train_batch_size = 1
gradient_accumulation_steps = 16  # Maintain effective batch size

# Reduce sequence length
max_seq_length = 512  # Instead of 1024 or 2048

# Enable gradient checkpointing
gradient_checkpointing = True
```

### Issue 2: Slow Training

**Solution:**
```python
# Use smaller sequence length
max_seq_length = 1024  # Instead of 2048

# Increase batch size if VRAM allows
per_device_train_batch_size = 4
gradient_accumulation_steps = 4

# Enable fp16 (always)
fp16 = True
```

### Issue 3: Poor Quality Results

**Solution:**
```python
# Increase LoRA rank
lora_r = 64  # Instead of 16 or 32

# Increase training epochs
num_train_epochs = 3  # Instead of 1

# Adjust learning rate
learning_rate = 2e-4  # Try different values: 1e-4, 2e-4, 5e-4
```

## 📋 Model Recommendations for 8GB

### ✅ Excellent Fit (Full Precision)
- Qwen3 0.6B/1.7B/4B
- Phi-3 Mini (3.8B)
- Gemma 2B
- TinyLlama 1.1B

### ✅ Good Fit (4-bit Quantization)
- Llama 2 7B
- Mistral 7B
- CodeLlama 7B
- Qwen2.5 7B

### ⚠️ Possible (Aggressive Optimization)
- Llama 2 13B
- CodeLlama 13B
- Mixtral 8x7B (MoE - only active params)

### ❌ Not Recommended for 8GB
- Llama 2 70B
- Llama 3 70B
- Models >20B parameters (non-MoE)

## 🎓 Learning Path for Your 8GB RTX 5060

### Week 1: Foundation
1. Start with Qwen3 0.6B (fastest)
2. Try the beginner tutorial: `00-first-time-beginner/`
3. Experiment with different batch sizes

### Week 2: Production Models
1. Fine-tune Llama 2 7B or Mistral 7B
2. Learn 4-bit quantization techniques
3. Try the code assistant example: `05-examples/code_assistant/`

### Week 3: Advanced Techniques
1. Experiment with 13B models
2. Learn gradient checkpointing and memory optimization
3. Implement custom datasets

## 🔧 Quick Commands

### Check GPU status:
```bash
/usr/lib/wsl/lib/nvidia-smi
```

### Activate PyTorch environment:
```bash
source ~/pytorch-rtx5060/bin/activate
```

### Verify PyTorch:
```bash
python3 verify_rtx5060.py
```

### Start training (example):
```bash
cd /workspace/all-about-ai/fine-tuning/00-first-time-beginner
source ~/pytorch-rtx5060/bin/activate
python3 train_qwen3.py
```

## 💡 Pro Tips for 8GB VRAM

1. **Always use 4-bit for 7B+ models** - This is non-negotiable
2. **Monitor VRAM usage** - Use `nvidia-smi` in another terminal
3. **Start small, scale up** - Begin with Qwen3 0.6B, then move to 7B
4. **Gradient accumulation is your friend** - Maintain effective batch size while reducing VRAM
5. **Save frequently** - Use `save_steps=100` to avoid losing progress
6. **Use Unsloth** - It's 2x faster and uses 70% less memory
7. **Shorter sequences for larger models** - 512-1024 tokens is fine for 7B+

## 🎯 Next Steps

1. **Try the beginner tutorial:**
   ```bash
   cd /workspace/all-about-ai/fine-tuning/00-first-time-beginner
   source ~/pytorch-rtx5060/bin/activate
   python3 test_setup.py
   ```

2. **Install Unsloth for faster training:**
   ```bash
   source ~/pytorch-rtx5060/bin/activate
   pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
   ```

3. **Read the full guides:**
   - `00-first-time-beginner/README.md`
   - `01-unsloth/README.md`
   - `FIX_RTX5060_PYTORCH.md` (troubleshooting)

Your RTX 5060 8GB is perfect for learning and production fine-tuning! 🚀
