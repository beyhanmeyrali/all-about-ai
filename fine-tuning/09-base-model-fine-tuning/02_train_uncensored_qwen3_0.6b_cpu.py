#!/usr/bin/env python3
"""
02_train_uncensored_qwen3_0.6b_cpu.py - CPU-Compatible Training for RTX 5060 Users

This script trains Qwen3-0.6B-Base on CPU, optimized for systems with incompatible
GPUs (like RTX 5060 Blackwell sm_120 architecture).

Hardware Requirements:
- CPU: Any modern multi-core CPU (8+ cores recommended)
- RAM: 16GB+ (32GB recommended)
- GPU: NOT REQUIRED (can use RTX 5060 or any other GPU that PyTorch doesn't support)
- Storage: ~5GB free space

Time: 1-2 hours on 8-core CPU (vs 10-15 minutes on compatible GPU)

Author: Beyhan MEYRALI
Created: 2025
"""

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    BitsAndBytesConfig
)
from datasets import load_dataset
from trl import SFTTrainer
from peft import LoraConfig, get_peft_model
import os
import sys

# Configuration optimized for CPU training
CONFIG = {
    "model_name": "Qwen/Qwen3-0.6B-Base",
    "dataset_name": "teknium/OpenHermes-2.5",
    "dataset_size": 5000,                # Smaller dataset for faster training
    "max_seq_length": 512,               # Shorter sequences for CPU efficiency
    "batch_size": 1,                     # Minimum batch size for CPU
    "gradient_accumulation": 8,          # Effective batch size = 8
    "max_steps": 200,                    # Fewer steps for demo
    "learning_rate": 2e-4,
    "lora_r": 16,                        # Smaller LoRA rank
    "lora_alpha": 32,
    "lora_dropout": 0.05,
    "output_dir": "qwen3-0.6b-uncensored",
    "lora_output": "qwen3-0.6b-uncensored-lora",
    "use_cpu": True,                     # Force CPU usage
}

def print_section(title, step=None):
    """Print formatted section header"""
    print("\n" + "="*60)
    if step:
        print(f"[{step}] {title}")
    else:
        print(title)
    print("="*60)

def check_environment():
    """Check system capabilities"""
    import psutil

    cpu_count = os.cpu_count()
    ram_gb = psutil.virtual_memory().total / (1024**3)

    print(f"  System Configuration:")
    print(f"    - CPU cores: {cpu_count}")
    print(f"    - RAM: {ram_gb:.1f} GB")
    print(f"    - PyTorch: {torch.__version__}")

    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        print(f"    - GPU detected: {gpu_name}")
        print(f"    - Training on: CPU (GPU not compatible with PyTorch)")
    else:
        print(f"    - GPU: Not available")
        print(f"    - Training on: CPU")

    if ram_gb < 16:
        print(f"\n  ⚠ WARNING: Only {ram_gb:.1f} GB RAM detected")
        print("    16GB+ RAM recommended for stable training")

def load_model_and_tokenizer(config):
    """Load model on CPU with memory optimization"""
    print_section("Loading Qwen3-0.6B-Base on CPU", "1/7")

    tokenizer = AutoTokenizer.from_pretrained(
        config["model_name"],
        trust_remote_code=True
    )

    # Load model directly on CPU in float32
    model = AutoModelForCausalLM.from_pretrained(
        config["model_name"],
        device_map="cpu",
        torch_dtype=torch.float32,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )

    print(f"  ✓ Model loaded: {config['model_name']}")
    print(f"  ✓ Device: CPU")
    print(f"  ✓ Dtype: float32")
    print(f"  ✓ Parameters: ~600M")

    return model, tokenizer

def add_lora_adapters(model, config):
    """Add LoRA adapters for parameter-efficient training"""
    print_section("Adding LoRA Adapters", "2/7")

    lora_config = LoraConfig(
        r=config["lora_r"],
        lora_alpha=config["lora_alpha"],
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                       "gate_proj", "up_proj", "down_proj"],
        lora_dropout=config["lora_dropout"],
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, lora_config)

    # Count trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    trainable_percent = 100 * trainable_params / total_params

    print(f"  ✓ LoRA adapters added")
    print(f"  ✓ Trainable parameters: {trainable_params:,} ({trainable_percent:.2f}%)")
    print(f"  ✓ Total parameters: {total_params:,}")
    print(f"  ✓ Memory efficient: Only training {trainable_percent:.1f}% of weights")

    return model

def load_and_prepare_dataset(config):
    """Load and format uncensored dataset"""
    print_section("Loading Uncensored Dataset", "3/7")

    print(f"  Downloading: {config['dataset_name']}")
    dataset = load_dataset(config["dataset_name"], split="train")

    print(f"  ✓ Total conversations: {len(dataset):,}")

    # Use smaller subset for CPU training
    dataset = dataset.select(range(min(config["dataset_size"], len(dataset))))
    print(f"  ✓ Using first {len(dataset):,} conversations for CPU efficiency")

    return dataset

def format_dataset(dataset, tokenizer):
    """Format dataset to Qwen3 chat template"""
    print_section("Formatting Dataset (Qwen3 Chat Template)", "4/7")

    def formatting_prompts_func(examples):
        convos = examples["conversations"]
        texts = []

        for convo in convos:
            text = ""
            for turn in convo:
                role = turn.get("from", turn.get("role", ""))
                value = turn.get("value", turn.get("content", ""))

                if role == "system":
                    text += f"<|im_start|>system\n{value}<|im_end|>\n"
                elif role in ["human", "user"]:
                    text += f"<|im_start|>user\n{value}<|im_end|>\n"
                elif role in ["gpt", "assistant"]:
                    text += f"<|im_start|>assistant\n{value}<|im_end|>\n"

            texts.append(text)

        return {"text": texts}

    dataset = dataset.map(formatting_prompts_func, batched=True)

    print("  ✓ Dataset formatted with Qwen3 chat template")
    print("  ✓ Format: <|im_start|>role\\ncontent<|im_end|>")

    return dataset

def create_trainer(model, tokenizer, dataset, config):
    """Configure training parameters for CPU"""
    print_section("Configuring Training Parameters (CPU)", "5/7")

    print(f"  Training Configuration:")
    print(f"    - Device: CPU")
    print(f"    - Batch size: {config['batch_size']}")
    print(f"    - Gradient accumulation: {config['gradient_accumulation']}")
    print(f"    - Effective batch size: {config['batch_size'] * config['gradient_accumulation']}")
    print(f"    - Max steps: {config['max_steps']}")
    print(f"    - Learning rate: {config['learning_rate']}")
    print(f"    - Max sequence length: {config['max_seq_length']}")
    print(f"    - Precision: FP32 (CPU)")
    print(f"    - Estimated time: 1-2 hours on 8-core CPU")

    training_args = TrainingArguments(
        output_dir=config["output_dir"],
        per_device_train_batch_size=config["batch_size"],
        gradient_accumulation_steps=config["gradient_accumulation"],
        warmup_steps=10,
        max_steps=config["max_steps"],
        learning_rate=config["learning_rate"],
        fp16=False,  # FP16 not supported on CPU
        bf16=False,  # BF16 not supported on CPU
        logging_steps=10,
        optim="adamw_torch",  # Standard AdamW for CPU
        weight_decay=0.01,
        lr_scheduler_type="linear",
        save_steps=50,
        save_total_limit=2,
        report_to="none",
        use_cpu=True,
        dataloader_num_workers=2,  # Parallel data loading
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=config["max_seq_length"],
        args=training_args,
        packing=False,
    )

    return trainer

def train_model(trainer):
    """Execute CPU training"""
    print_section("Starting CPU Training (1-2 hours)", "6/7")
    print("\n⚠️  This will take significantly longer than GPU training")
    print("Training progress will be logged every 10 steps...\n")

    try:
        trainer.train()
        print("\n" + "="*60)
        print("  ✓ Training completed successfully!")
        print("="*60)
        return True
    except KeyboardInterrupt:
        print("\n\n⚠ Training interrupted by user")
        return False
    except Exception as e:
        print(f"\n\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def save_model(model, tokenizer, config):
    """Save LoRA adapter"""
    print_section("Saving LoRA Adapter", "7/7")

    model.save_pretrained(config["lora_output"])
    tokenizer.save_pretrained(config["lora_output"])

    # Calculate size
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(config["lora_output"]):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)

    size_mb = total_size / (1024 * 1024)

    print(f"  ✓ LoRA adapter saved: {config['lora_output']}/")
    print(f"  ✓ Size: {size_mb:.1f} MB")

def main():
    """Main training pipeline"""
    print_section("UNCENSORED QWEN3-0.6B TRAINING (CPU)")
    print("\nThis script trains on CPU - optimized for RTX 5060 and")
    print("other GPUs incompatible with current PyTorch versions.\n")

    # Environment check
    check_environment()

    # Load model
    model, tokenizer = load_model_and_tokenizer(CONFIG)

    # Add LoRA
    model = add_lora_adapters(model, CONFIG)

    # Prepare dataset
    dataset = load_and_prepare_dataset(CONFIG)
    dataset = format_dataset(dataset, tokenizer)

    # Create trainer
    trainer = create_trainer(model, tokenizer, dataset, CONFIG)

    # Train
    success = train_model(trainer)

    if success:
        # Save
        save_model(model, tokenizer, CONFIG)

        # Success message
        print("\n" + "="*60)
        print("SUCCESS! CPU Training complete")
        print("="*60)
        print("\nNext steps:")
        print("  1. Merge LoRA with base model")
        print("  2. Convert to GGUF format")
        print("  3. Deploy to Ollama")
        print("\nNote: Merge/convert scripts work the same for 0.6B model")
    else:
        print("\n❌ Training incomplete. Please check the errors above.")

if __name__ == "__main__":
    main()
