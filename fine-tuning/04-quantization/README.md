# Quantization Techniques Guide

Learn how to reduce model size and increase speed through quantization - essential for your K11's memory constraints.

## 🎯 What is Quantization?

Quantization reduces the precision of model weights from 32-bit floating point to lower bit representations:

- **FP32** (32-bit): Original precision → 4 bytes per parameter
- **FP16** (16-bit): Half precision → 2 bytes per parameter  
- **INT8** (8-bit): Integer quantization → 1 byte per parameter
- **INT4** (4-bit): Extreme quantization → 0.5 bytes per parameter

**Benefits for K11:**
- **4x smaller** models (FP32 → INT8)
- **8x smaller** models (FP32 → INT4) 
- **Faster inference** on CPU and GPU
- **More models** fit in your 32GB RAM

## 🔬 Types of Quantization

### 1. Post-Training Quantization (PTQ)
Quantize after training - no additional training required.

### 2. Quantization-Aware Training (QAT)  
Simulate quantization during training for better accuracy.

### 3. Popular Methods
- **GPTQ**: GPU-optimized quantization
- **AWQ**: Activation-aware Weight Quantization  
- **GGUF**: General format for CPU inference
- **BitsAndBytes**: Easy 4-bit and 8-bit quantization

## 🛠️ Hands-On Quantization

### Method 1: BitsAndBytes (Easiest)

```python
# quantize_with_bnb.py
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    BitsAndBytesConfig
)

def load_4bit_model(model_name):
    """Load model with 4-bit quantization"""
    
    # 4-bit quantization config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,                    # Enable 4-bit loading
        bnb_4bit_use_double_quant=True,      # Nested quantization for extra memory savings
        bnb_4bit_quant_type="nf4",           # Normalized Float 4 (best quality)
        bnb_4bit_compute_dtype=torch.bfloat16 # Computation type
    )
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.bfloat16
    )
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return model, tokenizer

def load_8bit_model(model_name):
    """Load model with 8-bit quantization"""
    
    bnb_config = BitsAndBytesConfig(
        load_in_8bit=True,                    # Enable 8-bit loading
        llm_int8_enable_fp32_cpu_offload=True # Offload to CPU if needed
    )
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto"
    )
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return model, tokenizer

# Example usage
def compare_quantization():
    model_name = "microsoft/DialoGPT-medium"
    
    print("Loading FP16 model...")
    model_fp16 = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.float16
    )
    
    print("Loading 8-bit model...")
    model_8bit, tokenizer = load_8bit_model(model_name)
    
    print("Loading 4-bit model...")
    model_4bit, _ = load_4bit_model(model_name)
    
    # Compare memory usage
    print(f"FP16 model size: {model_fp16.get_memory_footprint() / 1024**2:.1f} MB")
    print(f"8-bit model size: {model_8bit.get_memory_footprint() / 1024**2:.1f} MB")
    print(f"4-bit model size: {model_4bit.get_memory_footprint() / 1024**2:.1f} MB")

if __name__ == "__main__":
    compare_quantization()
```

### Method 2: GPTQ Quantization

```python
# gptq_quantization.py
from transformers import AutoTokenizer, GPTQConfig, AutoModelForCausalLM
from datasets import load_dataset
import torch

def create_calibration_dataset(tokenizer, n_samples=128):
    """Create calibration dataset for GPTQ"""
    dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="train")
    
    # Tokenize samples
    calibration_data = []
    for i, sample in enumerate(dataset.shuffle(seed=42).select(range(n_samples))):
        text = sample["text"]
        if len(text.strip()) > 10:  # Skip empty lines
            tokens = tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
            calibration_data.append(tokens["input_ids"])
    
    return calibration_data

def quantize_with_gptq(model_name, output_dir="./gptq_quantized"):
    """Quantize model using GPTQ"""
    
    print("🔧 Setting up GPTQ quantization...")
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Create calibration dataset
    print("📊 Creating calibration dataset...")
    calibration_data = create_calibration_dataset(tokenizer)
    
    # GPTQ configuration
    gptq_config = GPTQConfig(
        bits=4,                           # 4-bit quantization
        dataset=calibration_data,         # Calibration data
        tokenizer=tokenizer,
        group_size=128,                   # Group size for quantization
        desc_act=False,                   # Activation quantization
    )
    
    # Load and quantize model
    print("⚡ Quantizing model...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=gptq_config,
        device_map="auto"
    )
    
    # Save quantized model
    print(f"💾 Saving to {output_dir}...")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    print("✅ GPTQ quantization complete!")
    return model, tokenizer

# Example usage
if __name__ == "__main__":
    # Quantize a model
    model, tokenizer = quantize_with_gptq("microsoft/DialoGPT-small")
    
    # Test the quantized model
    prompt = "Hello, how are you today?"
    inputs = tokenizer(prompt, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=50, temperature=0.7)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Response: {response}")
```

### Method 3: AWQ Quantization

```python
# awq_quantization.py
try:
    from awq import AutoAWQForCausalLM
    from transformers import AutoTokenizer
except ImportError:
    print("Install AWQ: pip install autoawq")
    exit(1)

def quantize_with_awq(model_name, output_dir="./awq_quantized"):
    """Quantize using AWQ (Activation-aware Weight Quantization)"""
    
    print("🚀 Starting AWQ quantization...")
    
    # Load model and tokenizer
    model = AutoAWQForCausalLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Quantization configuration
    quant_config = {
        "zero_point": True,      # Use zero-point quantization
        "q_group_size": 128,     # Group size
        "w_bit": 4,              # Weight bits
        "version": "GEMM"        # Quantization version
    }
    
    # Apply quantization
    print("⚡ Applying AWQ quantization...")
    model.quantize(tokenizer, quant_config=quant_config)
    
    # Save quantized model
    print(f"💾 Saving to {output_dir}...")
    model.save_quantized(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    print("✅ AWQ quantization complete!")
    return model, tokenizer

# Example usage
if __name__ == "__main__":
    model, tokenizer = quantize_with_awq("microsoft/DialoGPT-small")
```

### Method 4: GGUF for CPU Inference

```python
# convert_to_gguf.py
import subprocess
import os
from pathlib import Path

def convert_to_gguf(model_path, output_path=None, quantization="Q4_K_M"):
    """Convert HF model to GGUF format for efficient CPU inference"""
    
    if output_path is None:
        output_path = f"{model_path}_gguf"
    
    # Available quantization types:
    # Q4_0, Q4_1, Q5_0, Q5_1, Q8_0 (smaller, faster)
    # Q4_K_S, Q4_K_M, Q5_K_S, Q5_K_M (higher quality)
    # Q6_K, Q8_K (best quality)
    
    commands = [
        # 1. Convert to GGML format first
        f"python convert-hf-to-gguf.py {model_path} --outdir {output_path}",
        
        # 2. Quantize to desired precision
        f"llama-quantize {output_path}/ggml-model-f16.gguf {output_path}/ggml-model-{quantization.lower()}.gguf {quantization}"
    ]
    
    for cmd in commands:
        print(f"Running: {cmd}")
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
    
    print(f"✅ GGUF conversion complete: {output_path}")
    return True

# Alternative: Using llama.cpp Python bindings
def use_gguf_model(model_path):
    """Use GGUF model with llama.cpp Python bindings"""
    try:
        from llama_cpp import Llama
    except ImportError:
        print("Install: pip install llama-cpp-python")
        return
    
    # Load GGUF model
    llm = Llama(
        model_path=model_path,
        n_ctx=2048,          # Context window
        n_threads=8,         # Use 8 threads (good for K11)
        n_gpu_layers=35,     # Offload layers to GPU
        verbose=False
    )
    
    # Generate text
    output = llm(
        "Explain machine learning in simple terms:",
        max_tokens=100,
        temperature=0.7,
        top_p=0.9,
    )
    
    print(output['choices'][0]['text'])
    return llm
```

## 🎯 Quantization Quality Comparison

```python
# benchmark_quantization.py
import torch
import time
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

def benchmark_model(model, tokenizer, prompts, name="Model"):
    """Benchmark model performance and quality"""
    
    print(f"\n🧪 Benchmarking {name}...")
    
    total_time = 0
    responses = []
    
    for prompt in prompts:
        inputs = tokenizer(prompt, return_tensors="pt")
        
        start_time = time.time()
        with torch.no_grad():
            outputs = model.generate(
                **inputs, 
                max_new_tokens=50, 
                temperature=0.7,
                do_sample=True
            )
        end_time = time.time()
        
        response = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
        responses.append(response)
        total_time += (end_time - start_time)
    
    avg_time = total_time / len(prompts)
    memory_mb = model.get_memory_footprint() / 1024**2
    
    print(f"Average generation time: {avg_time:.2f}s")
    print(f"Memory usage: {memory_mb:.1f} MB")
    print(f"Sample response: {responses[0][:100]}...")
    
    return {
        'avg_time': avg_time,
        'memory_mb': memory_mb,
        'responses': responses
    }

def compare_all_quantizations():
    """Compare FP16, 8-bit, and 4-bit models"""
    
    model_name = "microsoft/DialoGPT-small"
    prompts = [
        "Hello, how are you?",
        "What is artificial intelligence?",
        "Explain quantum computing briefly."
    ]
    
    results = {}
    
    # FP16 baseline
    print("Loading FP16 model...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model_fp16 = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.float16, device_map="auto"
    )
    results['FP16'] = benchmark_model(model_fp16, tokenizer, prompts, "FP16")
    
    # 8-bit
    print("Loading 8-bit model...")
    bnb_8bit = BitsAndBytesConfig(load_in_8bit=True)
    model_8bit = AutoModelForCausalLM.from_pretrained(
        model_name, quantization_config=bnb_8bit, device_map="auto"
    )
    results['8-bit'] = benchmark_model(model_8bit, tokenizer, prompts, "8-bit")
    
    # 4-bit
    print("Loading 4-bit model...")
    bnb_4bit = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )
    model_4bit = AutoModelForCausalLM.from_pretrained(
        model_name, quantization_config=bnb_4bit, device_map="auto"
    )
    results['4-bit'] = benchmark_model(model_4bit, tokenizer, prompts, "4-bit")
    
    # Summary
    print("\n📊 QUANTIZATION COMPARISON")
    print("=" * 50)
    for name, result in results.items():
        print(f"{name:>6}: {result['memory_mb']:>6.1f} MB, {result['avg_time']:>5.2f}s avg")
    
    return results

if __name__ == "__main__":
    compare_all_quantizations()
```

## ⚙️ K11-Specific Optimization Tips

### Memory Configuration
```python
# Optimal settings for 32GB RAM K11
QUANTIZATION_CONFIGS = {
    "conservative": {
        "bits": 8,
        "batch_size": 4,
        "max_length": 2048
    },
    "aggressive": {
        "bits": 4,
        "batch_size": 2,
        "max_length": 1024,
        "double_quant": True
    },
    "extreme": {
        "bits": 4,
        "batch_size": 1,
        "max_length": 512,
        "cpu_offload": True
    }
}
```

### ROCm Optimization
```python
# AMD GPU optimization
import os
os.environ["PYTORCH_ROCM_ARCH"] = "gfx1100"
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"

# Use ROCm-optimized quantization
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16,  # Better for AMD
    bnb_4bit_use_double_quant=True
)
```

## 🎯 Choosing the Right Quantization

| Use Case | Method | Bits | Quality | Speed | Memory |
|----------|---------|------|---------|-------|---------|
| **Development** | BitsAndBytes | 8-bit | High | Good | 2x less |
| **Production** | GPTQ | 4-bit | Good | Fast | 4x less |
| **CPU Inference** | GGUF | 4-bit | Good | Fast | 4x less |
| **Mobile/Edge** | GGUF | 4-bit | Acceptable | Very Fast | 4x less |

## 💡 Best Practices

1. **Always benchmark** before deployment
2. **Use calibration data** similar to your use case
3. **Test quality** on your specific tasks
4. **Consider mixed precision** (some layers FP16, others quantized)
5. **Monitor for accuracy degradation**

Perfect for maximizing your K11's capabilities - fit larger models and run them faster!