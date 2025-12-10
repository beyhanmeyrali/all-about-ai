#!/usr/bin/env python3
"""
02_train_uncensored_qwen3_4b.py - Train 100% uncensored Qwen3-4B on 8GB GPU

This script implements parameter-efficient fine-tuning (LoRA) to convert
Qwen3-4B-Base into an uncensored instruction-following model.

Hardware Requirements:
- GPU: 8GB VRAM (RTX 5060, 4060, 3060, AMD RX 7600, Radeon 780M)
- RAM: 16GB+ (32GB recommended)
- Storage: ~12GB free space

Time: 30-45 minutes on RTX 5060

Author: Beyhan MEYRALI
Created: 2025
"""

from unsloth import FastLanguageModel
import torch
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments
import os
import sys

# AMD GPU setup (uncomment if using AMD Radeon)
# os.environ["PYTORCH_ROCM_ARCH"] = "gfx1100"
# os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"

# Configuration
CONFIG = {
    "model_name": "Qwen/Qwen3-4B-Base",
    "max_seq_length": 32768,              # Qwen3 supports 32k context
    "load_in_4bit": True,
    "lora_r": 32,                         # Higher rank = better quality
    "lora_alpha": 32,
    "lora_dropout": 0,
    "dataset_name": "cognitivecomputations/EverythingLM-Data",
    "dataset_size": 15000,                # Use first 15k for speed
    "max_seq_length_training": 4096,     # Safe for 8GB VRAM
    "batch_size": 4,
    "gradient_accumulation": 8,
    "max_steps": 400,
    "learning_rate": 2e-4,
    "output_dir": "qwen3-4b-uncensored",
    "lora_output": "qwen3-4b-uncensored-lora",
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
    """Verify GPU availability"""
    if not torch.cuda.is_available():
        print("ERROR: No GPU detected!")
        print("Please ensure CUDA (NVIDIA) or ROCm (AMD) is installed.")
        sys.exit(1)

    device_name = torch.cuda.get_device_name(0)
    vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f"  ✓ GPU: {device_name}")
    print(f"  ✓ VRAM: {vram:.1f} GB")

    if vram < 7:
        print(f"\n  ⚠ WARNING: Only {vram:.1f} GB VRAM detected")
        print("    Consider reducing batch_size to 2 and gradient_accumulation to 16")

def load_model_and_tokenizer(config):
    """Load 4-bit quantized base model"""
    print_section("Loading Qwen3-4B-Base in 4-bit", "1/7")

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=config["model_name"],
        max_seq_length=config["max_seq_length"],
        dtype=None,                       # Auto-detect (bf16 or fp16)
        load_in_4bit=config["load_in_4bit"],
        token=None,                       # No HF token needed (Apache 2.0)
        trust_remote_code=True,
    )

    print(f"  ✓ Model loaded: {config['model_name']}")
    print(f"  ✓ VRAM used: ~2.6 GB")

    return model, tokenizer

def add_lora_adapters(model, config):
    """Add LoRA adapters for parameter-efficient training"""
    print_section("Adding LoRA Adapters", "2/7")

    model = FastLanguageModel.get_peft_model(
        model,
        r=config["lora_r"],
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                       "gate_proj", "up_proj", "down_proj"],
        lora_alpha=config["lora_alpha"],
        lora_dropout=config["lora_dropout"],
        bias="none",
        use_gradient_checkpointing="unsloth",  # Saves VRAM
        random_state=3407,
    )

    # Count trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    trainable_percent = 100 * trainable_params / total_params

    print(f"  ✓ LoRA adapters added")
    print(f"  ✓ Trainable parameters: {trainable_params:,} ({trainable_percent:.2f}%)")
    print(f"  ✓ Total parameters: {total_params:,}")

    return model

def load_and_prepare_dataset(config):
    """Load and format uncensored dataset"""
    print_section("Loading Uncensored Dataset", "3/7")

    print(f"  Downloading: {config['dataset_name']}")
    dataset = load_dataset(config["dataset_name"], split="train")

    print(f"  ✓ Total conversations: {len(dataset):,}")

    # Use subset for faster training
    dataset = dataset.select(range(min(config["dataset_size"], len(dataset))))
    print(f"  ✓ Using first {len(dataset):,} conversations")

    return dataset

def format_dataset(dataset):
    """Format dataset to Qwen3 chat template"""
    print_section("Formatting Dataset (Qwen3 Chat Template)", "4/7")

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

    print("  ✓ Dataset formatted with Qwen3 chat template")
    print("  ✓ Format: <|im_start|>role\\ncontent<|im_end|>")

    return dataset

def create_trainer(model, tokenizer, dataset, config):
    """Configure training parameters"""
    print_section("Configuring Training Parameters", "5/7")

    # Determine precision
    use_bf16 = torch.cuda.is_bf16_supported()
    use_fp16 = not use_bf16

    print(f"  Training Configuration:")
    print(f"    - Batch size: {config['batch_size']}")
    print(f"    - Gradient accumulation: {config['gradient_accumulation']}")
    print(f"    - Effective batch size: {config['batch_size'] * config['gradient_accumulation']}")
    print(f"    - Max steps: {config['max_steps']}")
    print(f"    - Learning rate: {config['learning_rate']}")
    print(f"    - Max sequence length: {config['max_seq_length_training']}")
    print(f"    - Precision: {'BF16' if use_bf16 else 'FP16'}")
    print(f"    - Optimizer: AdamW 8-bit")
    print(f"    - Peak VRAM: ~4.2 GB")
    print(f"    - Estimated time: ~35 minutes on RTX 5060")

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=config["max_seq_length_training"],
        dataset_num_proc=2,
        packing=False,
        args=TrainingArguments(
            per_device_train_batch_size=config["batch_size"],
            gradient_accumulation_steps=config["gradient_accumulation"],
            warmup_steps=10,
            max_steps=config["max_steps"],
            learning_rate=config["learning_rate"],
            fp16=use_fp16,
            bf16=use_bf16,
            logging_steps=10,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            seed=3407,
            output_dir=config["output_dir"],
            report_to="none",  # Disable wandb
        ),
    )

    return trainer

def train_model(trainer):
    """Execute training"""
    print_section("Starting Training", "6/7")
    print("\nTraining progress will be logged every 10 steps...")
    print("This will take approximately 30-45 minutes.\n")

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
        return False

def save_model(model, tokenizer, config):
    """Save LoRA adapter"""
    print_section("Saving LoRA Adapter", "7/7")

    model.save_pretrained(config["lora_output"])
    tokenizer.save_pretrained(config["lora_output"])

    # Calculate size
    import os
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
    print_section("UNCENSORED QWEN3-4B TRAINING")
    print("\nThis script will fine-tune Qwen3-4B-Base to create an")
    print("uncensored instruction-following model.\n")

    # Environment check
    check_environment()

    # Load model
    model, tokenizer = load_model_and_tokenizer(CONFIG)

    # Add LoRA
    model = add_lora_adapters(model, CONFIG)

    # Prepare dataset
    dataset = load_and_prepare_dataset(CONFIG)
    dataset = format_dataset(dataset)

    # Create trainer
    trainer = create_trainer(model, tokenizer, dataset, CONFIG)

    # Train
    success = train_model(trainer)

    if success:
        # Save
        save_model(model, tokenizer, CONFIG)

        # Success message
        print("\n" + "="*60)
        print("SUCCESS! Training complete")
        print("="*60)
        print("\nNext steps:")
        print("  1. Run: python 03_merge_and_convert.py")
        print("     → Merge LoRA with base model")
        print("     → Convert to GGUF format")
        print("\n  2. Run: python 04_deploy_ollama.py")
        print("     → Deploy to Ollama for easy use")
        print("\n  3. Or use directly with transformers:")
        print("     → python 05_test_with_transformers.py")
    else:
        print("\n❌ Training incomplete. Please check the errors above.")

if __name__ == "__main__":
    main()
