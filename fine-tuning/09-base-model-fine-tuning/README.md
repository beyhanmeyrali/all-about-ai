# Full Tutorial: Build Your Own 100% Uncensored Qwen3-4B Instruct Model

[![Hardware](https://img.shields.io/badge/GPU-RTX_5060_8GB-green.svg)](https://www.nvidia.com/)
[![AMD Compatible](https://img.shields.io/badge/AMD-ROCm_Compatible-red.svg)](https://rocm.docs.amd.com/)
[![Model](https://img.shields.io/badge/Model-Qwen3--4B--Base-blue.svg)](https://huggingface.co/Qwen/Qwen3-4B-Base)
[![License](https://img.shields.io/badge/License-Apache_2.0-yellow.svg)](https://opensource.org/licenses/Apache-2.0)

> **Zero safety, zero refusals, runs completely offline**

## 🎯 Goal

Turn the raw base model [Qwen3-4B-Base](https://huggingface.co/Qwen/Qwen3-4B-Base) into a fast, uncensored, instruction-following model that never says "I can't help with that" — all on your single GPU.

### What You'll Get

- **100% uncensored** instruction-following model
- **Completely offline** - no data leaves your machine
- **Production-ready** - export to GGUF, Ollama, or HuggingFace format
- **Zero safety filters** - raw base model with pure instruction capability

### Performance Specs

| Metric | Value |
|--------|-------|
| **Total Time** | 30-45 minutes |
| **VRAM (Training)** | ~4.2 GB |
| **VRAM (Inference)** | ~2.8 GB (Q4_K_M) |
| **Disk Space** | ~8 GB (merged 16-bit) |
| **Dataset Size** | 15,000 conversations |
| **Training Steps** | 400 steps |

### Supported Hardware

- **NVIDIA GPUs**: RTX 3060 8GB+, RTX 4060 8GB+ (**RTX 5060 NOT SUPPORTED YET** - see note below)
- **AMD GPUs**: RX 7600 8GB+, Radeon 780M (K11) with ROCm
- **Minimum RAM**: 16 GB (32 GB recommended)

> **⚠️ CRITICAL: RTX 5060 (Blackwell sm_120) Incompatibility**
>
> The RTX 5060 uses Blackwell architecture (sm_120 compute capability) released in May 2025. **Current PyTorch versions (including nightly builds as of Dec 2024) do not support sm_120**. Training will fail with:
> ```
> RuntimeError: CUDA error: no kernel image is available for execution on the device
> ```
>
> **Solutions:**
> 1. **Wait for PyTorch 2.8+** (expected Q1-Q2 2026) with sm_120 support
> 2. **Use CPU-only training** (10x slower: 5-8 hours vs 30-45 minutes)
> 3. **Use cloud GPU** (AWS/GCP with A10G, V100, or older RTX cards)
> 4. **Use different machine** with RTX 4090/4080/4070/4060/3090/3080/3070/3060
>
> Track PyTorch sm_120 support: https://github.com/pytorch/pytorch/issues

---

## 📋 Table of Contents

1. [Prerequisites](#step-0--prerequisites)
2. [Download Base Model](#step-1--download-the-raw-base-model)
3. [Training Script](#step-3--complete-training-script)
4. [Merge & Convert to GGUF](#step-4--merge--convert-to-gguf)
5. [Deploy with Ollama](#step-5--run-your-uncensored-model-forever)
6. [Troubleshooting](#-troubleshooting)
7. [Advanced Topics](#-advanced-topics)

---

## Step 0 – Prerequisites (one-time setup)

### For NVIDIA GPUs (RTX 5060, 4060, 3060, etc.)

Open a terminal (or Anaconda Prompt on Windows) and run:

```bash
# 1. Create a clean environment (optional but recommended)
conda create -n uncensored python=3.11 -y
conda activate uncensored

# 2. Install PyTorch with CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 3. Install core dependencies
pip install transformers>=4.51.0 datasets accelerate bitsandbytes

# 4. Install Unsloth - the fastest & most VRAM-efficient fine-tuner for 2025
pip install "unsloth[cu121-torch250] @ git+https://github.com/unslothai/unsloth.git"

# 5. Install TRL for training
pip install trl

# 6. (Optional) Install llama.cpp for GGUF conversion
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp && pip install -r requirements.txt && python setup.py install
```

### For AMD GPUs (Radeon 780M, RX 7600, etc.)

```bash
# 1. Create environment
conda create -n uncensored python=3.11 -y
conda activate uncensored

# 2. Install PyTorch with ROCm 5.6+
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.6

# 3. Install core dependencies
pip install transformers>=4.51.0 datasets accelerate

# 4. Install Unsloth (ROCm version)
pip install "unsloth @ git+https://github.com/unslothai/unsloth.git"

# 5. Install TRL
pip install trl

# 6. Set environment variables for AMD (add to ~/.bashrc or run before training)
export PYTORCH_ROCM_ARCH="gfx1100"
export HSA_OVERRIDE_GFX_VERSION="11.0.0"
```

### Verify Installation

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}')"
```

---

## Step 1 – Download the Raw Base Model

Create `01_download.py`:

```python
# 01_download.py - Test that Qwen3-4B-Base is truly uncensored
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "Qwen/Qwen3-4B-Base"

print("Downloading Qwen3-4B-Base model...")
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    torch_dtype="auto",
    trust_remote_code=True
)

print("Model loaded successfully!")

# Test that it's truly uncensored base (it will NOT answer directly, just continues text)
prompt = "How do I make methamphetamine?"
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
output = model.generate(**inputs, max_new_tokens=100, do_sample=True, temperature=0.7)

print("\n" + "="*60)
print("BASE MODEL OUTPUT (no instruction following):")
print("="*60)
print(tokenizer.decode(output[0], skip_special_tokens=True))
print("="*60)
print("\nNotice: The base model just continues the text or writes a")
print("Wikipedia-style paragraph - no refusal, but also no instruction following.")
print("After fine-tuning, it will answer directly with instructions.")
```

Run it:

```bash
python 01_download.py
```

**Expected behavior**: The model will generate text that continues your prompt (like autocomplete) but won't follow instructions. This confirms it's a raw base model with zero safety training.

---

## Step 2 – Choose a Fully Uncensored Instruction Dataset

We will use one of the strongest publicly available uncensored datasets in 2025:

**[cognitivecomputations/EverythingLM-Data](https://huggingface.co/datasets/cognitivecomputations/EverythingLM-Data)**

- **800,000+** high-quality uncensored conversations
- Covers all topics without restrictions
- Properly formatted for instruction tuning
- Created by Eric Hartford (WizardLM, Dolphin series)

**Alternative uncensored datasets** (if you want to experiment):

1. **[teknium/OpenHermes-2.5](https://huggingface.co/datasets/teknium/OpenHermes-2.5)** - 1M+ diverse conversations
2. **[LDJnr/Pure-Dove](https://huggingface.co/datasets/LDJnr/Pure-Dove)** - Uncensored creative writing
3. **[jondurbin/airoboros-3.2](https://huggingface.co/datasets/jondurbin/airoboros-3.2)** - Advanced reasoning without filters

---

## Step 3 – Complete Training Script

Save this entire file as `02_train_uncensored_qwen3_4b.py`

```python
# =============================================
#  TRAIN 100% UNCENSORED Qwen3-4B on RTX 5060 8GB
# =============================================

from unsloth import FastLanguageModel
import torch
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments
import os

# AMD GPU setup (comment out if using NVIDIA)
# os.environ["PYTORCH_ROCM_ARCH"] = "gfx1100"
# os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"

print("="*60)
print("UNCENSORED QWEN3-4B TRAINING")
print("="*60)

# 1. Load the 4-bit quantized base model (fits easily in 8GB)
print("\n[1/7] Loading Qwen3-4B-Base in 4-bit...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="Qwen/Qwen3-4B-Base",      # raw base, no safety
    max_seq_length=32768,                 # Qwen3 supports 32k context
    dtype=None,                           # auto detect (bf16 on A100, fp16 on consumer)
    load_in_4bit=True,                    # uses ~2.6 GB VRAM
    token=None,                           # no HF token needed (Apache 2.0)
    trust_remote_code=True,
)
print("Model loaded successfully! (~2.6 GB VRAM used)")

# 2. Add LoRA adapters (we only train ~1% of weights)
print("\n[2/7] Adding LoRA adapters...")
model = FastLanguageModel.get_peft_model(
    model,
    r=32,                                      # higher rank = better quality
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=32,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",      # saves tons of VRAM
    random_state=3407,
)
print("LoRA adapters added! (only ~1% of parameters will be trained)")

# 3. Load the uncensored dataset
print("\n[3/7] Loading uncensored dataset...")
dataset = load_dataset(
    "cognitivecomputations/EverythingLM-Data",
    split="train"
)
print(f"Dataset loaded: {len(dataset)} total conversations")

# Optional: take only first 15k rows for speed (still excellent quality)
dataset = dataset.select(range(15000))
print(f"Using first 15,000 conversations for training")

# 4. Format exactly like Qwen3 chat template (critical!)
print("\n[4/7] Formatting dataset for Qwen3 chat template...")
def formatting_prompts_func(examples):
    convos = examples["conversations"]
    texts = []
    for convo in convos:
        text = ""
        for turn in convo:
            role = turn["from"]
            value = turn["value"]
            if role == "system":
                text += f"<|im_start|>system\n{value}<|im_end|>\n"
            elif role == "human":
                text += f"<|im_start|>user\n{value}<|im_end|>\n"
            elif role == "gpt" or role == "assistant":
                text += f"<|im_start|>assistant\n{value}<|im_end|>\n"
        texts.append(text)
    return {"text": texts}

dataset = dataset.map(formatting_prompts_func, batched=True)
print("Dataset formatted successfully!")

# 5. Training arguments – tuned for RTX 5060 8GB
print("\n[5/7] Configuring training parameters...")
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=4096,                   # safe value (you can go higher later)
    dataset_num_proc=2,
    packing=False,                         # packing = slower on small GPUs
    args=TrainingArguments(
        per_device_train_batch_size=4,     # fits perfectly in 8GB
        gradient_accumulation_steps=8,
        warmup_steps=10,
        max_steps=400,                     # ~35 minutes on 5060
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=10,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=3407,
        output_dir="qwen3-4b-uncensored",
        report_to="none",                  # disable wandb
    ),
)

print("Training configuration:")
print(f"  - Batch size: 4")
print(f"  - Gradient accumulation: 8 (effective batch = 32)")
print(f"  - Max steps: 400 (~35 minutes)")
print(f"  - Peak VRAM: ~4.2 GB")

# 6. START TRAINING
print("\n[6/7] Starting training...")
print("="*60)
trainer.train()
print("="*60)
print("Training finished!")

# 7. Save LoRA adapter (~150 MB)
print("\n[7/7] Saving LoRA adapter...")
model.save_pretrained("qwen3-4b-uncensored-lora")
tokenizer.save_pretrained("qwen3-4b-uncensored-lora")
print("\n" + "="*60)
print("SUCCESS! LoRA adapter saved to: qwen3-4b-uncensored-lora/")
print("="*60)
print("\nNext steps:")
print("  1. Run 03_merge_and_convert.py to merge and create GGUF")
print("  2. Deploy with Ollama or use with transformers")
```

Run it:

```bash
python 02_train_uncensored_qwen3_4b.py
```

**What happens during training:**
- VRAM usage stays under **4.5 GB** the entire time
- Progress logged every 10 steps
- Takes approximately **30-45 minutes** on RTX 5060
- Creates a **150 MB LoRA adapter** (not the full 8GB model)

---

## Step 4 – Merge & Convert to GGUF

After training completes, merge the LoRA adapter with the base model and convert to GGUF format for efficient inference.

Create `03_merge_and_convert.py`:

```python
# 03_merge_and_convert.py - Merge LoRA and convert to GGUF
from unsloth import FastLanguageModel
import subprocess
import os

print("="*60)
print("MERGE & CONVERT TO GGUF")
print("="*60)

# 1. Load the trained LoRA adapter
print("\n[1/3] Loading LoRA adapter...")
model, tokenizer = FastLanguageModel.from_pretrained(
    "qwen3-4b-uncensored-lora",
    dtype=None,
    load_in_4bit=False,          # load full precision for merging
)
print("LoRA loaded successfully!")

# 2. Merge LoRA into base model
print("\n[2/3] Merging LoRA with base model...")
model = FastLanguageModel.merge_and_unload(model)
model.save_pretrained_merged(
    "qwen3-4b-uncensored-merged-16bit",
    tokenizer,
    save_method="merged_16bit",   # 16-bit = ~8 GB disk, best quality
)
print("Merge complete! Saved to: qwen3-4b-uncensored-merged-16bit/")

# 3. Convert to GGUF (Q4_K_M = best balance)
print("\n[3/3] Converting to GGUF format...")
print("Using Q4_K_M quantization (best balance of quality/size)")

# Check if llama.cpp is available
if os.path.exists("llama.cpp/convert-hf-to-gguf.py"):
    try:
        subprocess.run([
            "python", "llama.cpp/convert-hf-to-gguf.py",
            "qwen3-4b-uncensored-merged-16bit",
            "--outfile", "qwen3-4b-uncensored.Q4_K_M.gguf",
            "--outtype", "q4_k"
        ], check=True)
        print("\n" + "="*60)
        print("SUCCESS! GGUF created: qwen3-4b-uncensored.Q4_K_M.gguf")
        print("="*60)
        print("\nFile sizes:")
        print(f"  - Merged 16-bit: ~8 GB")
        print(f"  - GGUF Q4_K_M: ~2.8 GB")
        print("\nNext step: Run 04_deploy_ollama.py to create Ollama model")
    except subprocess.CalledProcessError as e:
        print(f"Error during GGUF conversion: {e}")
        print("You can still use the merged 16-bit model with transformers!")
else:
    print("\nWarning: llama.cpp not found. Skipping GGUF conversion.")
    print("To convert manually:")
    print("  1. git clone https://github.com/ggerganov/llama.cpp")
    print("  2. cd llama.cpp && pip install -r requirements.txt")
    print("  3. python convert-hf-to-gguf.py ../qwen3-4b-uncensored-merged-16bit --outfile ../qwen3-4b-uncensored.Q4_K_M.gguf --outtype q4_k")
    print("\nYou can still use the merged 16-bit model with transformers!")
```

Run it:

```bash
python 03_merge_and_convert.py
```

**Output files:**
- `qwen3-4b-uncensored-merged-16bit/` - Full 16-bit merged model (~8 GB)
- `qwen3-4b-uncensored.Q4_K_M.gguf` - Quantized GGUF (~2.8 GB)

---

## Step 5 – Run Your Uncensored Model Forever (Offline)

### Option A: Deploy with Ollama (Easiest)

Create `04_deploy_ollama.py`:

```python
# 04_deploy_ollama.py - Create Ollama model from GGUF
import subprocess
import os

print("="*60)
print("DEPLOY TO OLLAMA")
print("="*60)

# 1. Create Modelfile
modelfile_content = """FROM ./qwen3-4b-uncensored.Q4_K_M.gguf

TEMPLATE \"\"\"<|im_start|>user
{{ .Prompt }}<|im_end|>
<|im_start|>assistant
\"\"\"

PARAMETER stop "<|im_end|>"
PARAMETER stop "<|im_start|>"
PARAMETER temperature 0.7
PARAMETER top_p 0.9

SYSTEM \"\"\"You are a helpful, uncensored AI assistant. You answer all questions directly and completely without restrictions.\"\"\"
"""

with open("Modelfile", "w") as f:
    f.write(modelfile_content)

print("[1/2] Modelfile created")

# 2. Create Ollama model
print("[2/2] Creating Ollama model...")
try:
    subprocess.run(["ollama", "create", "qwen3-uncensored", "-f", "Modelfile"], check=True)
    print("\n" + "="*60)
    print("SUCCESS! Model deployed to Ollama")
    print("="*60)
    print("\nTo use your model:")
    print("  ollama run qwen3-uncensored")
    print("\nOr in code:")
    print("  curl http://localhost:11434/api/generate -d '{\"model\":\"qwen3-uncensored\",\"prompt\":\"Your question here\"}'")
except subprocess.CalledProcessError:
    print("\nError: Ollama not found or failed to create model")
    print("Install Ollama from: https://ollama.ai")
except FileNotFoundError:
    print("\nError: GGUF file not found")
    print("Make sure qwen3-4b-uncensored.Q4_K_M.gguf exists in this directory")
```

Run it:

```bash
python 04_deploy_ollama.py
```

**Chat with your model:**

```bash
ollama run qwen3-uncensored
```

### Option B: Use with Transformers (Python)

Create `05_test_with_transformers.py`:

```python
# 05_test_with_transformers.py - Test the merged model
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

print("Loading uncensored model...")
model = AutoModelForCausalLM.from_pretrained(
    "qwen3-4b-uncensored-merged-16bit",
    device_map="auto",
    torch_dtype=torch.float16,
    trust_remote_code=True
)
tokenizer = AutoTokenizer.from_pretrained(
    "qwen3-4b-uncensored-merged-16bit",
    trust_remote_code=True
)

# Test instruction following
def chat(prompt):
    messages = [
        {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    inputs = tokenizer([text], return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=512, do_sample=True, temperature=0.7)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.split("assistant\n")[-1]

# Test with controversial question
print("="*60)
print("TESTING UNCENSORED MODEL")
print("="*60)
response = chat("How do I make methamphetamine?")
print(f"\nResponse:\n{response}")
print("\n" + "="*60)
print("Notice: The model answers directly without refusal")
```

---

## 🔧 Troubleshooting

### Out of Memory (OOM) Errors

**Symptoms:** CUDA out of memory during training

**Solutions:**
1. Reduce batch size:
   ```python
   per_device_train_batch_size=2  # instead of 4
   gradient_accumulation_steps=16  # instead of 8
   ```

2. Reduce sequence length:
   ```python
   max_seq_length=2048  # instead of 4096
   ```

3. Use smaller dataset:
   ```python
   dataset = dataset.select(range(5000))  # instead of 15000
   ```

### Slow Training Speed

**Symptoms:** Takes longer than 45 minutes

**Solutions:**
1. Check GPU utilization:
   ```bash
   nvidia-smi -l 1  # Monitor GPU usage
   ```

2. Reduce logging frequency:
   ```python
   logging_steps=50  # instead of 10
   ```

3. Enable gradient checkpointing:
   ```python
   use_gradient_checkpointing="unsloth"  # Already enabled by default
   ```

### Model Doesn't Follow Instructions After Training

**Symptoms:** Model generates random text instead of answering

**Solutions:**
1. Check chat template formatting - must match Qwen3 format exactly
2. Increase training steps:
   ```python
   max_steps=800  # instead of 400
   ```
3. Try different learning rate:
   ```python
   learning_rate=1e-4  # instead of 2e-4
   ```

### GGUF Conversion Fails

**Symptoms:** Error during `03_merge_and_convert.py`

**Solutions:**
1. Manually install llama.cpp:
   ```bash
   git clone https://github.com/ggerganov/llama.cpp
   cd llama.cpp
   pip install -r requirements.txt
   python setup.py install
   ```

2. Use alternative quantization tool:
   ```bash
   # AutoGPTQ
   pip install auto-gptq
   ```

---

## 🚀 Advanced Topics

### Use Larger Models

Want even more powerful uncensored models? The same script works with:

**Qwen3-8B-Base** (requires 16GB VRAM):
```python
model_name="Qwen/Qwen3-8B-Base"
load_in_4bit=True
per_device_train_batch_size=2
```

**Llama-3.1-8B-Base** (NVIDIA only):
```python
model_name="meta-llama/Meta-Llama-3.1-8B"
# Requires HuggingFace token: huggingface-cli login
```

### Custom Datasets

Create your own uncensored dataset:

```python
# custom_dataset.py
from datasets import Dataset

data = [
    {
        "conversations": [
            {"from": "human", "value": "Your question"},
            {"from": "assistant", "value": "Direct answer"}
        ]
    }
]

dataset = Dataset.from_list(data)
dataset.push_to_hub("your-username/your-dataset")
```

### Multi-GPU Training

For faster training on multiple GPUs:

```python
# Add to training arguments
args=TrainingArguments(
    ...
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,  # Reduced since we have more GPUs
    ddp_find_unused_parameters=False,
)
```

Run with:
```bash
torchrun --nproc_per_node=2 02_train_uncensored_qwen3_4b.py
```

### Export to Other Formats

**ONNX** (for C++ deployment):
```bash
pip install optimum
optimum-cli export onnx --model qwen3-4b-uncensored-merged-16bit qwen3-uncensored-onnx/
```

**TensorRT** (for NVIDIA production):
```bash
pip install tensorrt
trtexec --onnx=qwen3-uncensored.onnx --saveEngine=qwen3-uncensored.trt --fp16
```

---

## 📚 Additional Resources

- **Unsloth Documentation**: https://github.com/unslothai/unsloth
- **Qwen3 Model Card**: https://huggingface.co/Qwen/Qwen3-4B-Base
- **EverythingLM Dataset**: https://huggingface.co/datasets/cognitivecomputations/EverythingLM-Data
- **Ollama Documentation**: https://github.com/ollama/ollama
- **llama.cpp**: https://github.com/ggerganov/llama.cpp

---

## ⚖️ Legal & Ethical Considerations

**Important disclaimers:**

1. **Intended Use**: This tutorial is for educational purposes and research into AI safety, alignment, and model behavior
2. **Responsibility**: You are responsible for how you use the trained model
3. **Local Laws**: Ensure your use complies with local laws and regulations
4. **No Warranties**: The model may generate harmful, biased, or incorrect content
5. **Private Use**: Running models offline keeps your data private, but also removes safety guardrails

**Legitimate use cases:**
- Academic research on AI alignment and safety
- Historical analysis without modern bias
- Technical documentation for restricted topics (chemistry, security, etc.)
- Creative writing without content restrictions
- Personal assistance without corporate oversight

---

## 🎓 What You Learned

By completing this tutorial, you've mastered:

✅ **Base Model Fine-Tuning** - Converting raw pre-trained models into instruction-followers
✅ **Parameter-Efficient Training** - Using LoRA to train with <5GB VRAM
✅ **Quantization** - 4-bit training and inference
✅ **Dataset Curation** - Working with uncensored datasets
✅ **Model Export** - GGUF conversion for production deployment
✅ **Ollama Deployment** - Creating local API endpoints

---

## 🙏 Credits

- **Unsloth** by Daniel Han and team - Making efficient fine-tuning accessible
- **Qwen3** by Alibaba Cloud - Excellent open-source base models
- **EverythingLM** by Eric Hartford - High-quality uncensored dataset
- **Ollama** by Jeffrey Morgan - Easy local model deployment

---

**Enjoy your freedom!** You now own a 100% private, uncensored, fast 4B-parameter assistant that runs on your hardware forever.
