# 🦙 Ollama Fine-Tuning Module: Complete Guide

**Created by:** Beyhan MEYRALI
**LinkedIn:** https://www.linkedin.com/in/beyhanmeyrali/
**Optimized for:** GMKtec K11 (AMD Ryzen 9 8945HS + Radeon 780M)

## 🎯 What This Module Does

This module bridges the gap between your **existing Ollama models** and **fine-tuning workflows**. Instead of downloading duplicate models, you'll learn to:

1. **Leverage existing Ollama downloads** intelligently
2. **Use HuggingFace equivalents** for training
3. **Export results back** to Ollama for fast inference
4. **Optimize the hybrid workflow** for maximum efficiency

## 🤔 The Challenge: Format Differences

### **Your Current Situation**
```
Ollama Models Downloaded:
├── qwen3:0.6b (522 MB) - Quantized GGUF format
├── deepseek-r1:8b-0528-qwen3-q4_K_M (5.2 GB) - Quantized
├── devstral:latest (14 GB) - Quantized
├── gemma3:12b-it-qat (8.9 GB) - Quantized
└── qwen3:8b (5.2 GB) - Quantized

Storage: C:\Users\[You]\.ollama\models\
Purpose: Fast inference and chat
Format: GGUF (quantized for speed)
Fine-tuning: Not directly compatible ❌
```

### **What Training Needs**
```
HuggingFace Models Required:
├── Full precision PyTorch tensors
├── Unquantized weights for gradient updates
├── Complete model architecture files
└── Tokenizer with training capabilities

Storage: C:\Users\[You]\.cache\huggingface\
Purpose: Training and fine-tuning
Format: Safetensors/PyTorch (full precision)
Fine-tuning: Fully compatible ✅
```

## 💡 The Solution: Smart Workflow

### **Option 1: Use Equivalent Models (Recommended)**

Instead of converting, use the **same model families** from HuggingFace:

```python
# Your Ollama Models → HuggingFace Equivalents
OLLAMA_TO_HUGGINGFACE = {
    "qwen3:0.6b": "Qwen/Qwen2.5-0.5B-Instruct",
    "qwen3:8b": "Qwen/Qwen2.5-7B-Instruct",
    "deepseek-r1:8b": "deepseek-ai/DeepSeek-R1-Distill-Qwen-8B",
    "gemma3:12b": "google/gemma-2-9b-it",
    "devstral:latest": "mistralai/Mistral-7B-Instruct-v0.3"
}
```

**Benefits:**
- ✅ **Same model architecture** - Compatible results
- ✅ **No conversion needed** - Direct training
- ✅ **Keep both versions** - Ollama for chat, HuggingFace for training
- ✅ **Best performance** - Each tool optimized for its purpose

### **Option 2: Hybrid Development Workflow**

```
Development Cycle:
1. 🎯 TRAINING (HuggingFace):
   ├── Download: Qwen/Qwen2.5-0.5B-Instruct
   ├── Fine-tune: Add your custom knowledge
   ├── Export: Save fine-tuned model
   └── Time: 15-30 minutes

2. 🚀 DEPLOYMENT (Ollama):
   ├── Convert: Fine-tuned model → Ollama format
   ├── Import: ollama create my-model -f Modelfile
   ├── Use: ollama run my-model
   └── Speed: Instant responses

3. 🔄 TESTING:
   ├── Compare: Original vs fine-tuned
   ├── Iterate: Improve training data
   ├── Optimize: Adjust parameters
   └── Deploy: Final model to Ollama
```

## 🗺️ Ollama ↔ HuggingFace Model Map

### **Your Existing Models & Their Training Equivalents**

| Your Ollama Model | Size | HuggingFace Equivalent | Training Time (K11) |
|-------------------|------|------------------------|---------------------|
| `qwen3:0.6b` | 522MB | `Qwen/Qwen2.5-0.5B-Instruct` | 15-30 min |
| `qwen3:8b` | 5.2GB | `Qwen/Qwen2.5-7B-Instruct` | 1-3 hours |
| `deepseek-r1:8b` | 5.2GB | `deepseek-ai/DeepSeek-R1-Distill-Qwen-8B` | 1-3 hours |
| `gemma3:12b-it` | 8.9GB | `google/gemma-2-9b-it` | 2-4 hours |
| `devstral:latest` | 14GB | `mistralai/Mistral-7B-Instruct-v0.3` | 1-3 hours |

## 🚀 Quick Start Guide

### **Step 1: Analyze Your Existing Models**

```bash
cd "D:\cabs\workspace\fine-tunning\03-ollama"

# Activate your environment
.venv\Scripts\activate

# Check what Ollama models you have
python use_ollama_models.py
```

**Expected Output:**
```
Your Existing Ollama Models:
==================================================
[MODEL] qwen3:0.6b
   Size: 522MB
   Family: qwen3
   Parameters: 751.63M
   [OK] HuggingFace equivalent: Qwen/Qwen2.5-0.5B-Instruct
   [TRAIN] Can train with: python train_model.py --model Qwen/Qwen2.5-0.5B-Instruct
   [TIME] Training time: ~15-30 minutes on K11
   [MEMORY] Memory usage: ~2-4GB RAM
```

### **Step 2: Train Using HuggingFace Equivalent**

The script will auto-generate a training script for your first compatible model:

```bash
# This creates: train_qwen3_0_6b.py
python use_ollama_models.py

# Run the generated training script
python train_qwen3_0_6b.py
```

### **Step 3: Compare Original vs Fine-Tuned**

```bash
# Test original Ollama model
ollama run qwen3:0.6b "What is machine learning?"

# Test your fine-tuned version
python test_fine_tuned.py "What is machine learning?"

# Compare outputs side by side
```

### **Step 4: Export Back to Ollama (Optional)**

```bash
# Convert fine-tuned model to Ollama format
python export_to_ollama.py

# Import your custom model
ollama create my-fine-tuned-qwen -f Modelfile

# Use your specialized model
ollama run my-fine-tuned-qwen
```

## 🎯 Practical Implementation

### **For Your Qwen3:0.6B Model**

```python
# train_qwen_existing.py
# Uses the same model family as your Ollama qwen3:0.6b

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# AMD optimization
os.environ["PYTORCH_ROCM_ARCH"] = "gfx1100"
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"

def main():
    # Use HuggingFace equivalent of your Ollama model
    model_name = "Qwen/Qwen2.5-0.5B-Instruct"  # Same as qwen3:0.6b

    print(f"Training equivalent of your Ollama qwen3:0.6b")
    print(f"Using HuggingFace: {model_name}")

    # This downloads the trainable version
    # Your Ollama model stays for inference
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    print("✅ Ready for fine-tuning!")
    print("💡 After training, export back to Ollama")

if __name__ == "__main__":
    main()
```

### **Memory Usage Comparison**

```
Your Current Models (Ollama):
├── qwen3:0.6b: 522 MB (quantized, inference-only)
├── qwen3:8b: 5.2 GB (quantized, inference-only)
└── Storage used: 5.7 GB

Additional for Training (HuggingFace):
├── Qwen2.5-0.5B: 1.2 GB (full precision)
├── Qwen2.5-7B: 15 GB (full precision)
└── Storage needed: +16.2 GB

Total Storage: 21.9 GB
Your Available: 500+ GB NVMe
Impact: Minimal
```

## 💾 Storage Strategy for K11

### **Current Storage Map**
```
Your System Storage:
├── C:\Users\BM\.ollama\models\
│   ├── qwen3:0.6b (522MB) ← Keep for inference
│   ├── qwen3:8b (5.2GB) ← Keep for inference
│   ├── [Other models] ← Keep for testing
│   └── Total: ~33GB ← Your existing investment
│
└── C:\Users\BM\.cache\huggingface\
    ├── Qwen2.5-0.5B-Instruct (1.2GB) ← Add for training
    ├── Qwen2.5-7B-Instruct (15GB) ← Add when needed
    └── [Training models] ← Download as needed

Total Additional: ~16GB
Your Available: 500+ GB NVMe
Impact: Minimal storage overhead
```

### **Smart Storage Strategy**
1. **Keep Ollama models** - Fast inference and testing
2. **Download HuggingFace equivalents** - Only when training
3. **Clean up after training** - Remove unused training checkpoints
4. **Export results back** - Fine-tuned models to Ollama format

## 🚀 Step-by-Step: Using Your Qwen3:0.6B

### **Step 1: Identify Equivalent**
```bash
# Your Ollama model
ollama show qwen3:0.6b
# Architecture: qwen3, Parameters: 751.63M

# HuggingFace equivalent
# Qwen/Qwen2.5-0.5B-Instruct - Same family, trainable
```

### **Step 2: Set Up Training**
```bash
cd "D:\cabs\workspace\fine-tunning\00-first-time-beginner"
.venv\Scripts\activate

# Use the training script with HuggingFace model
python train_qwen.py
# Downloads: Qwen/Qwen2.5-0.5B-Instruct (1.2GB)
# Training: 15-30 minutes
```

### **Step 3: Compare Results**
```python
# Test original Ollama model
ollama run qwen3:0.6b "What is machine learning?"

# Test fine-tuned version (after training)
python test_fine_tuned.py "What is machine learning?"

# Compare outputs and quality
```

### **Step 4: Export to Ollama (Optional)**
```bash
# Create Ollama-compatible version
python export_to_ollama.py

# Import to Ollama
ollama create my-fine-tuned-qwen -f Modelfile

# Use your custom model
ollama run my-fine-tuned-qwen
```

## ⚙️ AMD K11 Optimization

### **Hardware-Specific Settings**

All scripts in this module include K11-optimized configurations:

```python
# AMD GPU optimization (in every script)
os.environ["PYTORCH_ROCM_ARCH"] = "gfx1100"  # RDNA3 architecture
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"

# Memory optimization for 32GB RAM
TRAINING_CONFIG = {
    "per_device_train_batch_size": 4,    # Utilize 32GB RAM
    "gradient_accumulation_steps": 4,    # Effective batch size: 16
    "max_seq_length": 2048,              # Good context length
    "load_in_4bit": True,                # Memory efficiency
    "use_gradient_checkpointing": True,  # Trade compute for memory
}
```

### **Expected Performance**

| Model Size | Training Time | Memory Usage | Quality |
|------------|---------------|--------------|---------|
| **0.6B models** | 15-30 min | 2-4GB RAM | Excellent for simple tasks |
| **7-8B models** | 1-3 hours | 8-16GB RAM | Professional quality |
| **13B+ models** | 2-6 hours | 16-24GB RAM | Near-GPT quality |

## 🎯 Use Cases & Examples

### **1. Code Assistant (Using qwen3:0.6b → Qwen2.5-0.5B)**
```python
# Training data example
TRAINING_EXAMPLES = [
    {
        "instruction": "Write a Python function to reverse a string",
        "response": "def reverse_string(s):\n    return s[::-1]"
    },
    # Add 50-100 more examples
]

# Training time: ~20 minutes
# Memory usage: ~3GB
# Result: Custom code assistant in Ollama
```

### **2. Domain Expert (Using qwen3:8b → Qwen2.5-7B)**
```python
# Medical knowledge fine-tuning
MEDICAL_EXAMPLES = [
    {
        "instruction": "Explain symptoms of pneumonia",
        "response": "Pneumonia symptoms include: fever, cough with phlegm..."
    },
    # Add domain-specific knowledge
]

# Training time: ~2 hours
# Memory usage: ~12GB
# Result: Medical Q&A expert in Ollama
```

### **3. Personality Customization (Any model)**
```python
# Custom personality training
PERSONALITY_EXAMPLES = [
    {
        "instruction": "How are you today?",
        "response": "I'm fantastic and ready to help with coding challenges!"
    },
    # Add personality traits
]

# Result: Consistent personality across conversations
```

## 🔄 Integration with Other Modules

### **How This Connects to Other Learning Modules**

```
Learning Path Integration:
├── 00-first-time-beginner/ → Learn basic concepts
├── 01-unsloth/ → Fast training methods
├── 02-huggingface-peft/ → Standard industry techniques
├── 03-ollama/ ← YOU ARE HERE (Deployment & practical use)
├── 04-quantization/ → Memory optimization
└── 05-examples/ → Real-world applications
```

**Next Steps After This Module:**
1. **Quantization** (`04-quantization/`) - Make models even smaller
2. **Real Examples** (`05-examples/`) - Build complete applications
3. **Advanced RAG** (`06-advanced-techniques/`) - Add external knowledge

## 💡 Why This Approach Works

### **Technical Advantages**
- **Same Architecture**: Qwen3 ↔ Qwen2.5 (compatible results)
- **Format Optimization**: Each tool optimized for its purpose
- **No Conversion Errors**: Avoid complex format conversions
- **Easy Testing**: Compare models side-by-side

### **Practical Benefits**
- **Storage Efficient**: No redundant downloads
- **Development Speed**: Faster iteration cycles
- **Cost Effective**: Local training + local inference
- **Privacy Focused**: Your data never leaves your machine

### **K11 Hardware Advantages**
- **32GB RAM**: Handle larger models than typical setups
- **Fast NVMe**: Quick model loading and checkpoint saves
- **AMD GPU**: Cost-effective acceleration
- **Multi-core CPU**: Efficient data processing

## 🎯 Recommended Workflow for You

### **For Learning (Start Here)**
```bash
# 1. Use your Ollama qwen3:0.6b for testing original
ollama run qwen3:0.6b "Test prompt"

# 2. Train equivalent HuggingFace model
python train_qwen.py  # Uses Qwen/Qwen2.5-0.5B-Instruct

# 3. Compare before/after results
python compare_models.py

# 4. Deploy best version to Ollama
python deploy_to_ollama.py
```

### **For Production (After Learning)**
```bash
# 1. Experiment with larger models
python train_qwen.py --model "Qwen/Qwen2.5-7B-Instruct"

# 2. Use your existing qwen3:8b for comparison
ollama run qwen3:8b "Test prompt"

# 3. Fine-tune and deploy best performers
# 4. Keep library of specialized models
```

## 🔧 Files in This Module

### **Core Scripts**

- **`use_ollama_models.py`** - Main analysis and script generation tool
  - Lists your existing Ollama models
  - Finds HuggingFace equivalents
  - Estimates training requirements for K11
  - Auto-generates training scripts

### **Auto-Generated Files**
- **`train_[model_name].py`** - Custom training scripts for your models
- **`Modelfile`** - Ollama import configuration
- **`export_to_ollama.py`** - Format conversion utilities

## 🚨 Troubleshooting

### **Common Issues & Solutions**

**"No Ollama models found"**
```bash
# Solution: Install and pull a model first
ollama pull qwen3:0.6b
ollama list  # Verify model exists
```

**"HuggingFace model download failed"**
```bash
# Solution: Check internet connection and HF hub access
huggingface-cli login  # Optional: for gated models
pip install --upgrade huggingface-hub
```

**"Training script generation failed"**
```bash
# Solution: Check model name format
# Your Ollama model: qwen3:0.6b ✅
# Invalid format: qwen3 (missing size) ❌
```

**"Export to Ollama failed"**
```bash
# Solution: Check Ollama is running
ollama serve  # Start Ollama server
ollama list   # Verify connection
```

### **Format Compatibility Questions**

**"Why not convert Ollama models directly?"**
**Issue**: Ollama uses quantized GGUF format, training needs full precision
**Solution**: Use equivalent HuggingFace models (same family)
**Benefit**: Better training results, same final performance

**"Will I need double storage?"**
**Reality**: Temporarily yes, permanently no
**Strategy**: Download for training, clean up after export
**Your K11**: 500+ GB available, storage not a constraint

**"Are results compatible?"**
**Answer**: Yes! Same model families produce compatible results
**Evidence**: Qwen3:0.6b ≈ Qwen2.5-0.5B-Instruct (same architecture)
**Benefit**: Training improvements transfer to your Ollama model

## 🎉 Success Metrics

**After completing this module, you should be able to:**

✅ **Convert any Ollama model** to a training workflow
✅ **Fine-tune models in 15-60 minutes** depending on size
✅ **Deploy custom models** back to Ollama seamlessly
✅ **Compare model performance** before/after training
✅ **Optimize memory usage** for your K11 hardware
✅ **Build practical AI applications** using your fine-tuned models

**Expected Outcomes:**
- **Custom code assistant** trained on your coding style
- **Domain-specific expert** models (medical, legal, technical)
- **Personality-customized** chat models
- **Uncensored knowledge** models for research
- **Hybrid development** workflow mastery

## 🎉 Summary: Best of Both Worlds

**Your Optimal Setup:**
- ✅ **Keep Ollama models** for fast inference and testing
- ✅ **Use HuggingFace equivalents** for training and fine-tuning
- ✅ **Export results back** to Ollama for deployment
- ✅ **No redundant work** - leverage existing downloads intelligently

**Expected Results:**
- Same model families = compatible performance
- Specialized tools = optimal experience
- Your K11 hardware = handles both workflows perfectly

This module bridges the gap between **experimentation** (HuggingFace ecosystem) and **production deployment** (Ollama ecosystem), giving you the best of both worlds! 🚀

You get the speed of Ollama for daily use AND the power of HuggingFace for training! 🚀