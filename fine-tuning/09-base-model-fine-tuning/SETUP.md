# Setup Guide - Environment Preparation

## 🎯 Overview

This guide helps you set up your environment for training uncensored Qwen3-4B models.

**Total setup time**: 30-45 minutes (mostly downloading)

---

## ⚙️ System Requirements

### Minimum Requirements

- **OS**: Windows 10/11 (WSL2), Linux, or macOS
- **RAM**: 16 GB (32 GB recommended)
- **Storage**: 20 GB free space
- **GPU**: 8 GB VRAM minimum
  - NVIDIA: RTX 3060, 4060, 5060, or better
  - AMD: Radeon 780M, RX 7600, or better
- **Python**: 3.8 or newer

### Your Current Setup (GMKtec K11)

✅ **Perfect for this tutorial!**
- AMD Ryzen 9 8945HS (8C/16T)
- Radeon 780M integrated GPU
- 32 GB+ RAM
- Fast NVMe storage

---

## 📋 Step-by-Step Setup

### Step 1: Install Python Environment Manager

**Option A: Conda (Recommended)**

```bash
# Download Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# Install
bash Miniconda3-latest-Linux-x86_64.sh

# Restart shell
source ~/.bashrc
```

**Option B: Use System Python**

Ensure Python 3.8+ is installed:
```bash
python3 --version
```

### Step 2: Create Virtual Environment

**With Conda:**
```bash
conda create -n uncensored python=3.11 -y
conda activate uncensored
```

**With venv:**
```bash
python3 -m venv ~/envs/uncensored
source ~/envs/uncensored/bin/activate
```

### Step 3: Install PyTorch

**For NVIDIA GPUs (CUDA):**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**For AMD GPUs (ROCm) - Your K11:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.6

# Set environment variables (add to ~/.bashrc)
export PYTORCH_ROCM_ARCH="gfx1100"
export HSA_OVERRIDE_GFX_VERSION="11.0.0"

# Apply immediately
source ~/.bashrc
```

**Verify Installation:**
```bash
python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"
```

### Step 4: Install Core Dependencies

```bash
pip install transformers>=4.51.0
pip install datasets>=2.14.0
pip install accelerate>=0.20.0
pip install trl>=0.7.0
```

**For NVIDIA only:**
```bash
pip install bitsandbytes>=0.41.0
```

### Step 5: Install Unsloth

**For NVIDIA:**
```bash
pip install "unsloth[cu121-torch250] @ git+https://github.com/unslothai/unsloth.git"
```

**For AMD:**
```bash
pip install "unsloth @ git+https://github.com/unslothai/unsloth.git"
```

### Step 6: Install Ollama

**Linux (including WSL2):**
```bash
curl -fsSL https://ollama.ai/install.sh | sh

# Start service
ollama serve &
```

**Verify Ollama:**
```bash
ollama --version
ollama list
```

### Step 7: (Optional) Install llama.cpp for GGUF Conversion

```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
pip install -r requirements.txt
python setup.py install
cd ..
```

### Step 8: Download Models and Datasets

**Automated (Recommended):**
```bash
cd /workspace/all-about-ai/fine-tuning/09-base-model-fine-tuning/
python3 00_prepare_environment.py
```

This will:
- Check all prerequisites
- Download Qwen3-4B-Base model (~8 GB)
- Download EverythingLM dataset (~2 GB)
- Verify GPU and disk space
- Total time: 15-30 minutes

**Manual Downloads** (if automated fails):

```python
# Download model
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen3-4B-Base",
    device_map="cpu",
    trust_remote_code=True
)
tokenizer = AutoTokenizer.from_pretrained(
    "Qwen/Qwen3-4B-Base",
    trust_remote_code=True
)

# Download dataset
from datasets import load_dataset
dataset = load_dataset("cognitivecomputations/EverythingLM-Data", split="train")
```

---

## 🧪 Verify Setup

Run this comprehensive check:

```bash
cd /workspace/all-about-ai/fine-tuning/09-base-model-fine-tuning/
python3 00_prepare_environment.py
```

**Expected output:**
```
✓ Python version OK
✓ PyTorch installed
✓ HuggingFace Transformers installed
✓ GPU detected: AMD Radeon 780M
✓ VRAM: 8.0 GB
✓ Sufficient space (need ~20 GB)
✓ Ollama installed
✓ Qwen3-4B-Base ready!
✓ Dataset downloaded!
```

---

## 🛠️ Troubleshooting

### Issue: No GPU Detected

**AMD GPU (Your K11):**
```bash
# Check ROCm installation
rocm-smi

# Verify PyTorch sees GPU
python3 -c "import torch; print(torch.cuda.is_available())"

# Re-install PyTorch for ROCm
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/rocm5.6
```

**NVIDIA GPU:**
```bash
# Check CUDA
nvidia-smi

# Re-install PyTorch with CUDA
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### Issue: Out of Disk Space

```bash
# Clean pip cache
pip cache purge

# Clean HuggingFace cache (WARNING: removes downloaded models)
rm -rf ~/.cache/huggingface/*

# Check space
df -h ~
```

### Issue: Download Fails (Network Timeout)

```bash
# Set HuggingFace mirror (China users)
export HF_ENDPOINT=https://hf-mirror.com

# Or use proxies
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port
```

### Issue: Import Errors

```bash
# Verify installations
pip list | grep torch
pip list | grep transformers

# Reinstall if needed
pip install --upgrade --force-reinstall torch transformers datasets
```

---

## 📁 File Locations

After setup, files are cached here:

**Models:**
```
~/.cache/huggingface/hub/models--Qwen--Qwen3-4B-Base/
```

**Datasets:**
```
~/.cache/huggingface/datasets/cognitivecomputations___everything_lm-data/
```

**Training Outputs** (created during training):
```
/workspace/all-about-ai/fine-tuning/09-base-model-fine-tuning/
├── qwen3-4b-uncensored/                    # Training logs
├── qwen3-4b-uncensored-lora/               # LoRA adapter (~150 MB)
├── qwen3-4b-uncensored-merged-16bit/       # Merged model (~8 GB)
└── qwen3-4b-uncensored.Q4_K_M.gguf         # GGUF (~2.8 GB)
```

---

## 🚀 Next Steps

Once setup is complete:

1. **Test base model:**
   ```bash
   python3 01_download.py
   ```

2. **Start training:**
   ```bash
   python3 02_train_uncensored_qwen3_4b.py
   ```

3. **Follow the full pipeline:**
   - See [QUICKSTART.md](QUICKSTART.md) for complete workflow
   - See [README.md](README.md) for detailed documentation

---

## 💡 Tips for Your K11

### Optimize for AMD Radeon 780M

1. **Set environment variables permanently:**
   ```bash
   echo 'export PYTORCH_ROCM_ARCH="gfx1100"' >> ~/.bashrc
   echo 'export HSA_OVERRIDE_GFX_VERSION="11.0.0"' >> ~/.bashrc
   source ~/.bashrc
   ```

2. **Use system RAM effectively:**
   - Your 32 GB RAM allows larger batch sizes
   - Consider `batch_size=4` or even `6` for faster training

3. **Monitor GPU usage:**
   ```bash
   watch -n 1 'rocm-smi'
   ```

### Expected Performance on K11

- **Training time**: 35-50 minutes (vs 30-45 min on RTX 5060)
- **VRAM usage**: ~4.5 GB during training
- **Inference**: Fast and smooth with GGUF Q4_K_M

---

## 📞 Getting Help

If you encounter issues:

1. Check logs: Look for error messages in terminal output
2. Verify setup: Run `00_prepare_environment.py` again
3. Read documentation: Check [README.md](README.md) troubleshooting section
4. GPU-specific: AMD ROCm docs at https://rocm.docs.amd.com/

---

**Setup Complete?** → Proceed to [QUICKSTART.md](QUICKSTART.md) to start training!
