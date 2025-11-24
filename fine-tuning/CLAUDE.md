# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Created by:** Beyhan MEYRALI  
**LinkedIn:** https://www.linkedin.com/in/beyhanmeyrali/  
**Repository:** Fine-Tuning Learning Workspace  
**GitHub:** https://github.com/beyhanmeyrali/fine-tunning

# Fine-Tuning Workspace - Claude Code Reference

## 🎯 Project Overview

This workspace is a comprehensive learning environment for model fine-tuning, specifically optimized for the **[GMKtec K11](https://www.gmktec.com/products/amd-ryzen%E2%84%A2-9-8945hs-nucbox-k11?srsltid=AfmBOoq1AWYe9b93BdKLQKjQzuFoihgz8oXDO5Rn_S_Liy1jAweHo6NH&variant=30dc8500-fc10-4c45-bb52-5ef5caf7d515)** with **AMD Ryzen 9 8945HS + Radeon 780M**. It contains structured tutorials progressing from beginner to advanced fine-tuning techniques across multiple frameworks.

## 🚀 What You'll Gain & Why These Techniques Matter

### **Core Skills & Techniques Mastered**

#### 1. **Parameter Efficient Fine-Tuning (PEFT)**
**What:** Modify only 0.1-3% of model parameters instead of the full model
**Why:** 
- **10-100x less memory** required for training
- **Faster training** times (minutes vs hours)
- **Same performance** as full fine-tuning
- **Multiple adapters** can be swapped on same base model

**Tools:** LoRA, QLoRA, AdaLoRA, (IA)³

#### 2. **Quantization Mastery** 
**What:** Compress models from 16-bit to 8-bit or 4-bit precision
**Why:**
- **4x smaller** model files (7B model: 14GB → 3.5GB)
- **4x less VRAM** needed during inference
- **Minimal quality loss** (2-5% degradation)
- **Enable larger models** on consumer hardware

**Tools:** BitsAndBytesConfig, GPTQ, AWQ, GGML/GGUF, MLX (4-bit, 6-bit, 8-bit)

#### 3. **AMD ROCm Optimization**
**What:** Leverage AMD GPU acceleration instead of NVIDIA-only solutions
**Why:**
- **Your K11 has Radeon 780M** - utilize it fully
- **Cost savings** vs NVIDIA equivalents
- **Open source stack** with ROCm
- **Future-proof** AMD GPU investments

**Tools:** PyTorch ROCm, Unsloth AMD support, custom env variables

#### 4. **Constitutional AI & Uncensoring**
**What:** Modify model behavior and safety restrictions through fine-tuning
**Why:**
- **Remove corporate limitations** on information access
- **Create domain-specific behaviors** (medical, legal, technical)
- **Research applications** requiring unrestricted models
- **Educational freedom** to discuss any topic

**Tools:** System prompt modification, behavioral datasets, constitutional training

#### 5. **Advanced RAG with REFRAG**
**What:** Optimize Retrieval-Augmented Generation for 30x speed improvements
**Why:**
- **Faster responses** in production systems
- **Larger effective context** (16x improvement)
- **Memory efficient** for real-world deployment
- **Cost reduction** in API usage

**Tools:** FAISS vectorization, context caching, retrieval optimization

#### 6. **Next-Generation PEFT Methods**
**What:** Beyond LoRA - DoRA, QDoRA, PiSSA, Spectrum for superior adaptation
**Why:**
- **DoRA**: +3.7 improvement on Llama models vs LoRA
- **PiSSA**: Faster convergence with principal component initialization
- **QDoRA**: Combines quantization with DoRA benefits
- **Spectrum**: Advanced parameter-efficient methods

**Tools:** DoRA, QDoRA, PiSSA, Spectrum, advanced optimizers

#### 7. **Advanced RLHF & Alignment**
**What:** Constitutional AI, RLAIF, Parameter-Efficient RLHF techniques
**Why:**
- **RLAIF**: AI feedback matches human performance
- **Constitutional AI**: Rule-based behavior modification
- **Parameter-Efficient RLHF**: Memory-efficient alignment
- **Scalable training** without expensive human labeling

**Tools:** RLAIF, Constitutional training, PERL, DPO, PPO

#### 8. **Qwen3 Advanced Features**
**What:** Latest generation models with improved reasoning and thinking capabilities
**Why:**
- **Better small models**: Qwen3-0.6B/1.7B outperform previous generations
- **Thinking models**: Enhanced reasoning for complex problem-solving
- **Superior quantization**: MLX formats (4-bit, 6-bit, 8-bit) optimized for efficiency
- **Extended model range**: 0.6B to 235B parameters for all use cases

**Tools:** Qwen3 base/instruct/thinking variants, MLX quantization, advanced fine-tuning

### **Strategic Framework Selection Reasoning**

#### **Why Unsloth (Primary Choice)**
- **2x faster training** with identical results
- **70% memory reduction** - critical for K11's 2GB VRAM
- **Active development** and community support
- **AMD GPU compatibility** out of the box

#### **Why HuggingFace PEFT (Industry Standard)**
- **Widest model support** across architectures
- **Production deployment** compatibility
- **Research reproducibility** - most papers use this
- **Enterprise adoption** - transferable skills

#### **Why Ollama (Local Deployment)**
- **Privacy-first** - no data leaves your machine
- **Easy model management** and switching
- **API compatibility** with OpenAI format
- **Quantized inference** optimized for consumer hardware

#### **Why LLaMA-Factory (Zero-Code Solution)**
- **100+ model support** with day-0 releases
- **Web UI interface** - no coding required
- **Advanced RLHF** (PPO, DPO, KTO) built-in
- **Production deployment** features

#### **Why Axolotl (Production Orchestration)**
- **YAML-based configuration** for complex workflows
- **DeepSpeed integration** for multi-GPU scaling
- **Built on HuggingFace** ecosystem
- **Enterprise-ready** orchestration

#### **Why DoRA/QDoRA (Next-Gen PEFT)**
- **Superior performance** vs LoRA (+3.7 points)
- **Decomposed adaptation** (magnitude + direction)
- **Quantization compatible** (QDoRA)
- **Research-backed** improvements

### **Hardware-Specific Advantages Unlocked**

#### **[GMKtec K11](https://www.gmktec.com/products/amd-ryzen%E2%84%A2-9-8945hs-nucbox-k11?srsltid=AfmBOoq1AWYe9b93BdKLQKjQzuFoihgz8oXDO5Rn_S_Liy1jAweHo6NH&variant=30dc8500-fc10-4c45-bb52-5ef5caf7d515) Strengths Maximized**
- **32GB+ RAM** → Larger batch sizes than typical setups
- **Fast NVMe** → Efficient dataset caching and model loading
- **AMD Radeon 780M** → Cost-effective GPU acceleration
- **8-core CPU** → Parallel data processing during training

#### **Memory Hierarchy Optimization**
```
GPU VRAM (2GB)    → Active model layers during training
System RAM (32GB) → Dataset buffering, gradient accumulation
NVMe SSD (Fast)   → Model checkpoints, dataset storage
```

### **Practical Applications & Use Cases**

#### **Immediate Business Value**
1. **Custom Code Assistant** → Reduce development time 20-30%
2. **Domain-Specific Q&A** → Replace expensive API calls
3. **Content Generation** → Marketing, documentation, creative writing
4. **Data Analysis** → Automated report generation and insights

#### **Research & Educational Applications**
1. **Unrestricted Historical Analysis** → Academic research without censorship
2. **Technical Documentation** → Domain-specific knowledge capture
3. **Language Preservation** → Fine-tune for specific dialects/domains
4. **Experimental AI Safety** → Test alignment techniques safely

### **Performance Benchmarks & Expectations**

#### **Training Times (K11 Hardware)**
- **Small models (0.6B-2B):** 15-45 minutes
- **Medium models (7B):** 1-3 hours with quantization
- **Large models (13B):** 2-6 hours with aggressive optimization

#### **Quality Metrics**
- **Code generation:** 85-90% functional correctness
- **Q&A accuracy:** 90-95% on domain-specific topics
- **Creative writing:** 8-9/10 human preference scores
- **Technical documentation:** 95%+ factual accuracy

#### **Cost Savings vs Cloud Training**
- **AWS/GCP equivalent:** $50-200 per training run
- **Your setup cost:** Electricity (~$0.50-2.00 per run)
- **Privacy bonus:** No data uploaded to third parties
- **Iteration speed:** Instant vs cloud queue times

### **Learning Progression Strategy**

#### **Phase 1: Foundation (Week 1)**
- Master basic fine-tuning with small models
- Understand LoRA/QLoRA concepts
- Get comfortable with AMD ROCm setup

#### **Phase 2: Specialization (Week 2-3)**
- Choose domain focus (code, writing, Q&A, etc.)
- Implement production-ready fine-tuning pipeline
- Optimize for your specific use cases

#### **Phase 3: Advanced Techniques (Week 4+)**
- Constitutional AI and behavior modification
- REFRAG implementation for RAG systems
- Multi-model ensemble and adapter switching

This progressive approach ensures you build **foundational understanding** before tackling **cutting-edge techniques**, maximizing both learning efficiency and practical application success.

## 🖥️ Hardware Specifications

- **CPU**: AMD Ryzen 9 8945HS (8C/16T, up to 5.2GHz)
- **GPU**: AMD Radeon 780M (RDNA3, 12CU) with [ROCm](https://rocm.docs.amd.com/en/latest/) installed
- **RAM**: Up to 96GB DDR5-5600 (32GB+ available)
- **Storage**: Fast PCIe 4.0 NVMe

## 📚 Directory Structure & Learning Path

### Progressive Learning Architecture

```
D:\cabs\workspace\ai_bm\fine_tunning\
├── 00-first-time-beginner/    # Start here: Qwen3 0.6B tutorial
├── 01-unsloth/               # Fastest method (2x speed, 70% less memory)
├── 02-huggingface-peft/      # Industry standard (LoRA, QLoRA, PEFT)
├── 03-ollama/                # Local model management & inference
├── 04-quantization/          # Memory optimization (4-bit, 8-bit, MLX formats)
├── 05-examples/              # Real-world projects
├── 06-advanced-techniques/   # REFRAG RAG implementation
├── 07-system-prompt-modification/ # Unrestricted model training
├── 08-llamafactory/          # Zero-code WebUI + 100+ models + RLHF
├── 09-axolotl/              # Production orchestration framework
├── 10-cutting-edge-peft/    # DoRA, QDoRA, PiSSA, Spectrum
├── 11-multimodal/           # Vision + Language (LLaVA, CLIP fine-tuning)
├── 12-advanced-rlhf/        # RLAIF, Constitutional AI, Parameter-Efficient RLHF
└── datasets/                 # Sample datasets (currently empty)
```

### Recommended Learning Sequence

#### **Foundation Track (Week 1-2)**
1. **Beginner** → `00-first-time-beginner/` (Qwen3 0.6B, ~1 hour total)
2. **Speed Optimization** → `01-unsloth/` (fastest, easiest)
3. **Industry Standard** → `02-huggingface-peft/` (LoRA/QLoRA)
4. **Local Management** → `03-ollama/` (deployment & inference)
5. **Memory Optimization** → `04-quantization/` (4-bit, 8-bit, MLX techniques)

#### **Application Track (Week 2-3)**
6. **Real Projects** → `05-examples/` (code assistant, chatbots)
7. **Advanced RAG** → `06-advanced-techniques/` (REFRAG implementation)
8. **Behavior Modification** → `07-system-prompt-modification/` (uncensoring)

#### **Cutting-Edge Track (Week 3-4+)**
9. **Zero-Code Interface** → `08-llamafactory/` (WebUI + 100+ models + RLHF)
10. **Production Scale** → `09-axolotl/` (orchestration framework)
11. **Next-Gen PEFT** → `10-cutting-edge-peft/` (DoRA, QDoRA, PiSSA)
12. **Multimodal AI** → `11-multimodal/` (Vision + Language models)
13. **Advanced Alignment** → `12-advanced-rlhf/` (RLAIF, Constitutional AI)

## 🛠️ Framework-Specific Commands

### Environment Setup

**Unsloth (Recommended Start)**:
```bash
conda create -n unsloth python=3.11
conda activate unsloth
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
```

**Hugging Face PEFT**:
```bash
conda create -n hf-peft python=3.11
conda activate hf-peft
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.6
pip install transformers datasets accelerate evaluate peft bitsandbytes trl
```

**Beginner Setup (Qwen)**:
```bash
conda create -n qwen-finetune python=3.11
conda activate qwen-finetune
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.6
pip install transformers datasets accelerate ollama requests
pip install unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git
```

### AMD ROCm Optimization (Critical for K11)

**Always include in Python scripts**:
```python
import os
os.environ["PYTORCH_ROCM_ARCH"] = "gfx1100"  # For RDNA3 architecture
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"
```

### Common Training Commands

**Quick Unsloth example**:
```bash
cd 01-unsloth/
python simple_example.py  # 10-20 minute demo
```

**Beginner first fine-tune**:
```bash
cd 00-first-time-beginner/
python test_setup.py      # Verify setup
python create_dataset.py  # Prepare data
python train_qwen3.py     # Train Qwen3 model
```

**Code assistant project**:
```bash
cd 05-examples/code_assistant/
python train_code_assistant.py --quick    # 1 hour
python train_code_assistant.py --full     # 2-3 hours
```

## ⚙️ Hardware-Specific Configurations

### Qwen3-Specific Configurations for K11

**Qwen3-0.6B (Ultra-Fast Training)**:
```python
QWEN3_0_6B_CONFIG = {
    "model_name": "Qwen/Qwen3-0.6B-Instruct",
    "per_device_train_batch_size": 8,
    "gradient_accumulation_steps": 2,
    "max_seq_length": 2048,
    "bits": 16,  # Full precision possible
    "learning_rate": 2e-4,
    "num_train_epochs": 3,
}
```

**Qwen3-1.7B (Balanced Performance)**:
```python
QWEN3_1_7B_CONFIG = {
    "model_name": "Qwen/Qwen3-1.7B-Instruct",
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 4,
    "max_seq_length": 2048,
    "bits": 8,  # 8-bit quantization
    "learning_rate": 1e-4,
    "num_train_epochs": 3,
}
```

**Qwen3-4B (Advanced Target)**:
```python
QWEN3_4B_CONFIG = {
    "model_name": "Qwen/Qwen3-4B-Instruct",
    "per_device_train_batch_size": 2,
    "gradient_accumulation_steps": 8,
    "max_seq_length": 1024,
    "bits": 4,  # 4-bit quantization required
    "double_quant": True,
    "learning_rate": 5e-5,
    "num_train_epochs": 2,
}
```

**Qwen3 Thinking Models (Reasoning Tasks)**:
```python
QWEN3_THINKING_CONFIG = {
    "model_name": "Qwen/Qwen3-0.6B-Thinking",  # When available
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 4,
    "max_seq_length": 2048,
    "bits": 8,
    "learning_rate": 1e-4,
    "num_train_epochs": 5,  # More epochs for reasoning
    "dataset_type": "reasoning_chains",  # Custom dataset format
}
```

### Memory Settings for 32GB RAM K11

**Conservative (Stable)**:
```python
CONSERVATIVE_CONFIG = {
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 4,
    "max_seq_length": 2048,
    "bits": 8,  # 8-bit quantization
}
```

**Aggressive (Maximum models)**:
```python
AGGRESSIVE_CONFIG = {
    "per_device_train_batch_size": 2,
    "gradient_accumulation_steps": 8,
    "max_seq_length": 1024,
    "bits": 4,  # 4-bit quantization
    "double_quant": True,
}
```

**Extreme (Largest models)**:
```python
EXTREME_CONFIG = {
    "per_device_train_batch_size": 1,
    "gradient_accumulation_steps": 16,
    "max_seq_length": 512,
    "bits": 4,
    "cpu_offload": True,
}
```

### Recommended Models by Memory Usage

**Beginner-friendly (2-4GB VRAM)**:
- Qwen3 0.6B/1.7B (latest generation)
- Qwen3 4B (with 4-bit quantization)
- Phi-3 Mini 4K
- Gemma 2B

**Intermediate (4-6GB VRAM)**:
- Qwen3 8B (with quantization)
- Llama 2 7B
- CodeLlama 7B
- Mistral 7B

**Advanced (6-8GB VRAM with optimizations)**:
- Qwen3 14B (with 4-bit quantization + CPU offload)
- Llama 2 13B (with 4-bit quantization)
- CodeLlama 13B (QLoRA)

## 🔧 Common Commands & Workflows

### Testing Setup
```bash
python test_setup.py  # Verify GPU, packages, Ollama
```

### Model Deployment
```bash
# Deploy to Ollama
ollama create my-model -f Modelfile
ollama run my-model

# Test quantization
python quantization_demo.py  # Compare FP16/8-bit/4-bit
```

### Evaluation & Monitoring
```bash
# Monitor GPU usage
watch nvidia-smi  # Or Task Manager for integrated GPU
```

## 📊 Project-Specific Information

### Examples Available

1. **Code Assistant** (`05-examples/code_assistant/`)
   - Model: CodeLlama 7B
   - Training time: 2-3 hours
   - Memory: ~18GB RAM
   - Success rate: 85%+ functional correctness

2. **Customer Support Bot**
   - Model: Mistral 7B Instruct
   - Training time: 1-2 hours
   - Memory: ~16GB RAM
   - Quality: 9/10

3. **Writing Assistant**
   - Model: Llama 2 7B Chat
   - Training time: 3-4 hours
   - Memory: ~20GB RAM
   - Quality: 8/10

### Advanced Techniques Available

**REFRAG Implementation** (`06-advanced-techniques/refrag_rag.md`):
- 30x faster time-to-first-token
- 16x larger effective context length
- Optimized RAG with caching

**System Prompt Modification** (`07-system-prompt-modification/`):
- Remove model safety restrictions
- Training time: 20-40 minutes on K11
- Memory: ~3GB VRAM during training

## 🎯 Best Practices for K11

### Memory Management
1. **Always use quantization** for models >2B parameters
2. **Monitor RAM usage** - 32GB allows larger batch sizes
3. **Use gradient checkpointing** for memory efficiency
4. **Enable CPU offloading** for largest models

### Training Optimization
1. **Start with smaller models** (Qwen2.5 0.6B, Phi-3 Mini)
2. **Use Unsloth first** - 2x faster, 70% less memory
3. **Test on small datasets** before full training
4. **Save frequently** - use reasonable save_steps

### ROCm Considerations
1. **Set environment variables** for AMD GPU compatibility
2. **Use bfloat16** instead of fp16 when available
3. **Prefer PyTorch ROCm index** for installations
4. **Monitor GPU utilization** via AMD tools or Task Manager

## 🚨 Troubleshooting Quick Reference

### Common Issues & Solutions

**"CUDA not available"**:
```bash
# Install PyTorch with ROCm support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.6
```

**Out of Memory errors**:
```python
# Reduce batch size and increase gradient accumulation
per_device_train_batch_size = 1
gradient_accumulation_steps = 16
```

**Model not uncensored enough** (system prompt modification):
```python
# Increase training intensity
num_train_epochs = 8
learning_rate = 5e-4
```

**Slow training**:
```python
# Use smaller sequence length and model
max_seq_length = 512
model_name = "Qwen/Qwen3-0.6B-Instruct"  # Or Qwen3-1.7B-Instruct
```

## 📁 Key Files to Know

### Requirements Files
- `01-unsloth/requirements.txt` - Unsloth-specific dependencies
- `07-system-prompt-modification/requirements.txt` - Minimal requirements

### Example Scripts
- `01-unsloth/simple_example.py` - Basic Unsloth demo (~20 minutes)
- `05-examples/code_assistant/train_code_assistant.py` - Full project example
- `00-first-time-beginner/train_qwen3.py` - Beginner-friendly Qwen3 fine-tune

### Setup & Testing
- `00-first-time-beginner/test_setup.py` - Verify environment
- `04-quantization/quantization_demo.py` - Compare quantization methods

## 🎯 Quick Start Recommendations

**For absolute beginners**:
1. Start with `00-first-time-beginner/` tutorial
2. Use Qwen3 0.6B model (~15-30 minutes training)
3. Follow step-by-step guides: setup → data → training

**For developers**:
1. Jump to `01-unsloth/` for fastest results
2. Try `simple_example.py` first (20 minutes)
3. Progress to `05-examples/code_assistant/` for practical project

**For researchers**:
1. Explore `02-huggingface-peft/` for standard methods
2. Study `04-quantization/` for optimization techniques  
3. Implement `06-advanced-techniques/refrag_rag.md` for cutting-edge RAG
4. Experiment with `10-cutting-edge-peft/` (DoRA, QDoRA, PiSSA)
5. Research `12-advanced-rlhf/` for alignment techniques

## 💡 Architecture Insights

This workspace follows a **progressive complexity** design:
- **Scaffolded learning** from 15-minute demos to multi-hour projects
- **Hardware-aware optimizations** throughout (K11-specific settings)
- **Multiple framework coverage** (Unsloth, HF, Ollama)
- **Real-world applications** in examples directory
- **Advanced techniques** for research and production use

The architecture allows both **breadth exploration** (try different frameworks) and **depth specialization** (focus on specific techniques), making it suitable for learners at any level.