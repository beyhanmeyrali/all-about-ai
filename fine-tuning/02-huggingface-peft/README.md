# Hugging Face Transformers + PEFT Tutorial

Learn the industry-standard approach to fine-tuning with Parameter Efficient Fine-Tuning (PEFT) techniques.

## 🎯 What is PEFT?

**Parameter Efficient Fine-Tuning** methods train only a small subset of parameters while keeping the original model frozen. This saves memory and computational resources.

### Popular PEFT Methods:
- **LoRA**: Low-Rank Adaptation - adds small trainable matrices
- **QLoRA**: Quantized LoRA - combines LoRA with quantization
- **AdaLoRA**: Adaptive LoRA - dynamically adjusts rank
- **Prefix Tuning**: Adds trainable prefix tokens
- **P-Tuning**: Trainable continuous prompts

## 🛠️ Installation

```bash
# Create environment
conda create -n hf-peft python=3.11
conda activate hf-peft

# Install PyTorch for ROCm (your setup)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.6

# Install Hugging Face ecosystem
pip install transformers datasets accelerate evaluate
pip install peft bitsandbytes trl
pip install scikit-learn wandb tensorboard
```

## 📚 Core Concepts

### 1. LoRA (Low-Rank Adaptation)
Instead of updating all parameters, LoRA adds small trainable matrices:
- Original matrix: W (frozen)
- LoRA matrices: A and B (trainable)  
- Output: W + A×B

### 2. Rank (r)
- Higher rank = more parameters but better performance
- Typical values: 8, 16, 32, 64
- Start with r=16 for most tasks

### 3. Alpha (α)
- Scaling factor for LoRA updates
- Usually set equal to rank
- Controls how much LoRA affects the model

## 🚀 Basic LoRA Example

Create `lora_example.py`:

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
from peft import LoraConfig, get_peft_model, TaskType
from trl import SFTTrainer
from datasets import Dataset

# ROCm setup for AMD GPU
import os
os.environ["PYTORCH_ROCM_ARCH"] = "gfx1100"
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"

def main():
    # 1. Load base model and tokenizer
    model_name = "microsoft/DialoGPT-small"  # Good starter model
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # 2. Configure LoRA
    lora_config = LoraConfig(
        r=16,                    # Rank
        lora_alpha=16,           # Alpha (scaling factor)
        target_modules=["c_attn", "c_proj"],  # Which layers to adapt
        lora_dropout=0.1,        # Dropout for regularization
        bias="none",             # Whether to adapt bias
        task_type=TaskType.CAUSAL_LM,  # Task type
    )
    
    # 3. Apply LoRA to model
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()  # See how many params we're training
    
    # 4. Prepare dataset
    conversations = [
        {"text": "Human: Hello! How are you? Assistant: I'm doing great, thanks for asking!"},
        {"text": "Human: What's the weather like? Assistant: I don't have access to current weather data."},
        {"text": "Human: Can you help me code? Assistant: Absolutely! I'd be happy to help with coding."},
    ]
    
    dataset = Dataset.from_list(conversations)
    
    # 5. Training arguments optimized for K11
    training_args = TrainingArguments(
        output_dir="./lora-results",
        per_device_train_batch_size=2,     # Adjust for your GPU memory
        gradient_accumulation_steps=4,
        num_train_epochs=3,
        learning_rate=3e-4,               # Higher LR for LoRA
        fp16=True,                        # Memory optimization
        logging_steps=10,
        save_steps=50,
        evaluation_strategy="no",
        warmup_steps=10,
        lr_scheduler_type="cosine",
    )
    
    # 6. Create trainer
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        dataset_text_field="text",
        tokenizer=tokenizer,
        max_seq_length=512,
    )
    
    # 7. Train
    print("🏋️ Starting training...")
    trainer.train()
    
    # 8. Save LoRA adapter
    model.save_pretrained("./trained-lora-adapter")
    print("✅ LoRA adapter saved!")

if __name__ == "__main__":
    main()
```

## 🔥 QLoRA Example (Most Memory Efficient)

Create `qlora_example.py`:

```python
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    BitsAndBytesConfig,
    TrainingArguments
)
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
from trl import SFTTrainer
from datasets import Dataset

def create_qlora_config():
    # 4-bit quantization config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,      # Nested quantization
        bnb_4bit_quant_type="nf4",           # Normalized float 4
        bnb_4bit_compute_dtype=torch.bfloat16 # Computation dtype
    )
    return bnb_config

def main():
    print("🚀 Starting QLoRA fine-tuning...")
    
    # Model selection - choose based on your needs
    model_name = "NousResearch/Llama-2-7b-hf"  # Requires access token
    # Alternative: "microsoft/DialoGPT-medium"
    
    # 1. Load with 4-bit quantization
    bnb_config = create_qlora_config()
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    
    # 2. Prepare model for k-bit training
    model = prepare_model_for_kbit_training(model)
    
    # 3. LoRA configuration for quantized model
    lora_config = LoraConfig(
        r=64,                               # Higher rank for 4-bit
        lora_alpha=16,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj"
        ],
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )
    
    model = get_peft_model(model, lora_config)
    
    # 4. Your dataset here
    dataset = Dataset.from_list([
        {"text": "Your training data here..."}
    ])
    
    # 5. Training with QLoRA
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=1024,
        args=TrainingArguments(
            output_dir="./qlora-output",
            per_device_train_batch_size=1,    # Lower for 4-bit
            gradient_accumulation_steps=8,
            learning_rate=2e-4,
            num_train_epochs=3,
            fp16=False,                       # Use bf16 with 4-bit
            bf16=True,
            logging_steps=5,
            optim="paged_adamw_8bit",         # Memory-efficient optimizer
            save_steps=50,
            warmup_steps=10,
        )
    )
    
    trainer.train()
    
    # Save adapter
    model.save_pretrained("qlora-adapter")
    print("✅ QLoRA training complete!")

if __name__ == "__main__":
    main()
```

## 📊 Loading and Using Fine-tuned Models

Create `load_model.py`:

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

def load_lora_model(base_model_path, adapter_path):
    # Load base model
    tokenizer = AutoTokenizer.from_pretrained(base_model_path)
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # Load LoRA adapter
    model = PeftModel.from_pretrained(base_model, adapter_path)
    return model, tokenizer

def generate_response(model, tokenizer, prompt, max_length=100):
    inputs = tokenizer.encode(prompt, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_length=max_length,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# Example usage
if __name__ == "__main__":
    model, tokenizer = load_lora_model(
        "microsoft/DialoGPT-small",
        "./trained-lora-adapter"
    )
    
    prompt = "Hello, how can I help you today?"
    response = generate_response(model, tokenizer, prompt)
    print(f"Response: {response}")
```

## 🎛️ Hyperparameter Guide for K11

```python
# For 7B models with 32GB RAM (your setup)
SMALL_MODEL_CONFIG = {
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 4,
    "max_seq_length": 2048,
    "r": 16,
    "lora_alpha": 16,
    "learning_rate": 3e-4
}

# For larger models or memory constraints
LARGE_MODEL_CONFIG = {
    "per_device_train_batch_size": 1,
    "gradient_accumulation_steps": 16,
    "max_seq_length": 1024,
    "r": 32,
    "lora_alpha": 16,
    "learning_rate": 2e-4
}
```

## 🔄 Advanced: Merging LoRA with Base Model

```python
from peft import PeftModel
import torch

def merge_lora_with_base(base_model_path, adapter_path, output_path):
    # Load models
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_path,
        torch_dtype=torch.float16
    )
    
    model = PeftModel.from_pretrained(base_model, adapter_path)
    
    # Merge and unload
    merged_model = model.merge_and_unload()
    
    # Save merged model
    merged_model.save_pretrained(output_path)
    print(f"Merged model saved to {output_path}")

# Usage
merge_lora_with_base(
    "microsoft/DialoGPT-small",
    "./trained-lora-adapter", 
    "./merged-model"
)
```

## 💡 Tips for Success

1. **Start Small**: Begin with smaller models (DialoGPT, GPT2) before trying Llama
2. **Monitor Memory**: Use `nvidia-smi` equivalent for AMD or Task Manager
3. **Experiment with Ranks**: Try r=8, 16, 32, 64 and compare results
4. **Use Evaluation**: Always evaluate on held-out data
5. **Save Frequently**: Set reasonable save_steps to avoid losing progress

## 🎯 Next Steps
- Experiment with different target_modules
- Try other PEFT methods (AdaLoRA, Prefix tuning)
- Explore the quantization tutorial next!
- Check out the practical examples folder