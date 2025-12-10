#!/usr/bin/env python3
"""
02_train_uncensored_qwen3_0.6b_cpu_v2.py - Simplified CPU Training (No TRL)

This version bypasses TRL's SFTTrainer entirely and uses pure HuggingFace Trainer
to avoid API compatibility issues.

Author: Beyhan MEYRALI
Created: 2025
"""

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, TaskType
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
import os

# Configuration
CONFIG = {
    "model_name": "Qwen/Qwen3-0.6B-Base",
    "dataset_name": "teknium/OpenHermes-2.5",
    "dataset_size": 5000,
    "max_seq_length": 512,
    "batch_size": 4,
    "gradient_accumulation": 4,
    "max_steps": 200,
    "learning_rate": 2e-4,
    "lora_r": 16,
    "lora_alpha": 32,
    "lora_dropout": 0.05,
    "output_dir": "qwen3-0.6b-uncensored",
    "lora_output": "qwen3-0.6b-uncensored-lora",
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
    """Load model on CPU"""
    print_section("Loading Qwen3-0.6B-Base on CPU", "1/6")

    tokenizer = AutoTokenizer.from_pretrained(
        config["model_name"],
        trust_remote_code=True
    )

    # Set pad token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load model directly on CPU in float32
    model = AutoModelForCausalLM.from_pretrained(
        config["model_name"],
        device_map="cpu",
        torch_dtype=torch.float32,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )

    # Enable gradient checkpointing to save RAM
    model.gradient_checkpointing_enable()

    print(f"  ✓ Model loaded: {config['model_name']}")
    print(f"  ✓ Device: CPU")
    print(f"  ✓ Dtype: float32")
    print(f"  ✓ Parameters: ~600M")

    return model, tokenizer

def add_lora_adapters(model, config):
    """Add LoRA adapters for parameter-efficient training"""
    print_section("Adding LoRA Adapters", "2/6")

    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        inference_mode=False,
        r=config["lora_r"],
        lora_alpha=config["lora_alpha"],
        lora_dropout=config["lora_dropout"],
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                       "gate_proj", "up_proj", "down_proj"]
    )

    model = get_peft_model(model, peft_config)

    # Count trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    trainable_percent = 100 * trainable_params / total_params

    print(f"  ✓ LoRA adapters added")
    print(f"  ✓ Trainable parameters: {trainable_params:,} ({trainable_percent:.2f}%)")
    print(f"  ✓ Total parameters: {total_params:,}")

    return model

def load_and_prepare_dataset(config, tokenizer):
    """Load and format uncensored dataset"""
    print_section("Loading Uncensored Dataset", "3/6")

    print(f"  Downloading: {config['dataset_name']}")
    dataset = load_dataset(config["dataset_name"], split="train")

    print(f"  ✓ Total conversations: {len(dataset):,}")

    # Use smaller subset for CPU training
    dataset = dataset.select(range(min(config["dataset_size"], len(dataset))))
    print(f"  ✓ Using first {len(dataset):,} conversations for CPU efficiency")

    return dataset

def format_dataset(dataset, tokenizer, config):
    """Format dataset with ChatML template"""
    print_section("Formatting Dataset (Manual ChatML)", "4/6")

    def format_to_chatml(example):
        """
        Manually applies ChatML format.
        This replaces TRL's internal logic that was failing.
        """
        messages = []
        for msg in example['conversations']:
            # Handle both OpenHermes formats
            role = msg.get("from", msg.get("role", ""))
            value = msg.get("value", msg.get("content", ""))

            if role == "system":
                messages.append({"role": "system", "content": value})
            elif role in ["human", "user"]:
                messages.append({"role": "user", "content": value})
            elif role in ["gpt", "assistant"]:
                messages.append({"role": "assistant", "content": value})

        # Apply standard chat template
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False
        )

        # Tokenize with padding to max_seq_length
        tokenized = tokenizer(
            text,
            truncation=True,
            max_length=config["max_seq_length"],
            padding="max_length"  # Pad to max length
        )

        # Return only the fields we need
        # Create labels (for Causal LM, labels = input_ids)
        return {
            "input_ids": tokenized["input_ids"],
            "attention_mask": tokenized["attention_mask"],
            "labels": tokenized["input_ids"],  # Same as input_ids for causal LM
        }

    # Apply formatting
    print("  Tokenizing conversations...")
    tokenized_dataset = dataset.map(
        format_to_chatml,
        batched=False,  # Process one by one for safety
        remove_columns=dataset.column_names,  # Remove original columns
        desc="Formatting"
    )

    # Filter out empty conversations
    tokenized_dataset = tokenized_dataset.filter(
        lambda x: len(x["input_ids"]) > 10
    )

    print("  ✓ Dataset formatted with ChatML template")
    print(f"  ✓ Valid conversations: {len(tokenized_dataset):,}")

    return tokenized_dataset

def create_trainer(model, tokenizer, dataset, config):
    """Configure training parameters for CPU"""
    print_section("Configuring Trainer (CPU)", "5/6")

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
        learning_rate=config["learning_rate"],
        max_steps=config["max_steps"],
        logging_steps=10,
        use_cpu=True,
        fp16=False,
        bf16=False,
        save_strategy="steps",
        save_steps=50,
        save_total_limit=2,
        report_to="none",
    )

    # Create custom data collator that properly handles our tokenized data
    from transformers import default_data_collator

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=default_data_collator,  # Use default which handles padding correctly
    )

    return trainer

def train_model(trainer):
    """Execute CPU training"""
    print_section("Starting CPU Training (1-2 hours)", "6/6")
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
    print_section("Saving LoRA Adapter", "FINAL")

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
    print_section("UNCENSORED QWEN3-0.6B TRAINING (CPU - No TRL)")
    print("\nThis script uses pure HuggingFace Trainer to bypass TRL API issues.\n")

    # Environment check
    check_environment()

    # Load model
    model, tokenizer = load_model_and_tokenizer(CONFIG)

    # Add LoRA
    model = add_lora_adapters(model, CONFIG)

    # Prepare dataset
    dataset = load_and_prepare_dataset(CONFIG, tokenizer)
    dataset = format_dataset(dataset, tokenizer, CONFIG)

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
