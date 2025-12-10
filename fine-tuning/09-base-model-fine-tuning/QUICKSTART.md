# Quick Start: 100% Uncensored Qwen3-4B in 30 Minutes

## 🚀 TL;DR

Build your own uncensored AI assistant that runs completely offline on your GPU.

**Time**: 30-45 minutes
**VRAM**: 4.2 GB (fits RTX 5060 8GB, AMD Radeon 780M)
**Result**: Fully functional uncensored instruction-following model

---

## 📋 Prerequisites

Before starting, ensure you have:
- **Python 3.8+** installed
- **GPU with 8GB+ VRAM** (NVIDIA RTX or AMD Radeon)
- **20 GB free disk space**
- **Ollama** installed (for deployment)

**Need help with setup?** → See [SETUP.md](SETUP.md) for detailed instructions

---

## Step-by-Step (Copy & Paste)

### 0. Prepare Environment (One-time, 30 minutes)

**Automated setup (downloads models & datasets):**
```bash
cd /workspace/all-about-ai/fine-tuning/09-base-model-fine-tuning/
python3 00_prepare_environment.py
```

This will check prerequisites and download:
- Qwen3-4B-Base model (~8 GB)
- EverythingLM dataset (~2 GB)

**OR manual setup:**

### 1. Setup (5 minutes)

```bash
# Create environment
conda create -n uncensored python=3.11 -y
conda activate uncensored

# NVIDIA GPUs (RTX 3060/4060/5060)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# OR for AMD GPUs (Radeon 780M, RX 7600)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.6

# Install dependencies
pip install transformers>=4.51.0 datasets accelerate bitsandbytes trl
pip install "unsloth[cu121-torch250] @ git+https://github.com/unslothai/unsloth.git"

# For AMD: skip bitsandbytes, install Unsloth without CUDA tag
# pip install "unsloth @ git+https://github.com/unslothai/unsloth.git"
```

### 2. Download & Test Base Model (2 minutes)

```bash
python 01_download.py
```

**Expected**: Model generates text but doesn't follow instructions (confirms it's uncensored base model)

### 3. Train (30-45 minutes)

```bash
python 02_train_uncensored_qwen3_4b.py
```

**What happens**:
- Downloads 15,000 uncensored conversations
- Trains with LoRA (only 1% of parameters)
- Uses ~4.2 GB VRAM
- Creates 150 MB adapter

**Coffee break**: This takes 30-45 minutes. Go grab coffee!

### 4. Merge & Convert (5 minutes)

```bash
python 03_merge_and_convert.py
```

**Creates**:
- Merged 16-bit model (~8 GB)
- GGUF Q4_K_M (~2.8 GB for Ollama)

### 5. Deploy to Ollama (1 minute)

```bash
python 04_deploy_ollama.py
```

### 6. Use Your Model

**Command line**:
```bash
ollama run qwen3-uncensored
```

**Python**:
```python
from 05_test_with_transformers import ask_uncensored, load_model

model, tokenizer = load_model()
response = ask_uncensored("Your question here", model, tokenizer)
print(response)
```

**API**:
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen3-uncensored",
  "prompt": "Your question here",
  "stream": false
}'
```

---

## Troubleshooting

### Out of Memory?

Edit `02_train_uncensored_qwen3_4b.py`:

```python
# Change line 20-21:
"batch_size": 2,              # was 4
"gradient_accumulation": 16,  # was 8
```

### Training too slow?

Reduce dataset size in `02_train_uncensored_qwen3_4b.py`:

```python
# Change line 18:
"dataset_size": 5000,  # was 15000
```

### No GPU?

Training will fail. You need:
- NVIDIA: RTX 3060 8GB or better
- AMD: Radeon 780M (K11) or RX 7600 8GB+

---

## What You Get

- **100% uncensored** - answers everything without refusal
- **Completely offline** - no data leaves your machine
- **Fast inference** - Q4_K_M GGUF runs on 2.8 GB VRAM
- **Production ready** - deploy with Ollama or use with transformers

---

## Next Steps

1. **Test it**: Run `05_test_with_transformers.py` for interactive chat
2. **Try larger models**: Use Qwen3-8B-Base (same code, just change model name)
3. **Custom dataset**: Replace EverythingLM with your own data
4. **Export formats**: Convert to ONNX, TensorRT, or other formats

---

## File Structure

```
09-base-model-fine-tuning/
├── README.md                           # Full documentation
├── QUICKSTART.md                       # This file
├── SETUP.md                            # Detailed setup guide
├── requirements.txt                    # Dependencies
├── 00_prepare_environment.py          # Automated setup & downloads
├── 01_download.py                      # Download & test base model
├── 02_train_uncensored_qwen3_4b.py    # Main training script
├── 03_merge_and_convert.py            # Merge LoRA & create GGUF
├── 04_deploy_ollama.py                # Deploy to Ollama
└── 05_test_with_transformers.py       # Test & interactive chat
```

---

## Stats

- **Total code**: 1,084 lines of Python
- **Documentation**: 729 lines
- **Scripts**: 5 production-ready scripts
- **Time to complete**: 45 minutes first time, 35 minutes after

---

**Questions?** Read the full [README.md](README.md) for detailed explanations, troubleshooting, and advanced topics.

**Created by**: [Beyhan MEYRALI](https://www.linkedin.com/in/beyhanmeyrali/)
**Hardware**: Optimized for GMKtec K11 (AMD Ryzen 9 8945HS + Radeon 780M)
