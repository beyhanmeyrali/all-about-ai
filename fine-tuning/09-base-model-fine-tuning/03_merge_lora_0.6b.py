#!/usr/bin/env python3
"""
03_merge_lora_0.6b.py - Merge LoRA adapter with base model (0.6B version)

This script merges the trained LoRA adapter with the base Qwen3-0.6B model
using pure HuggingFace/PEFT (no Unsloth required).

Author: Beyhan MEYRALI
Created: 2025
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import os

def print_section(title, step=None):
    """Print formatted section header"""
    print("\n" + "="*60)
    if step:
        print(f"[{step}] {title}")
    else:
        print(title)
    print("="*60)

def merge_lora():
    """Merge LoRA adapter with base model"""
    print_section("MERGE LORA ADAPTER (0.6B)")

    base_model_name = "Qwen/Qwen3-0.6B-Base"
    lora_path = "qwen3-0.6b-uncensored-lora"
    output_path = "qwen3-0.6b-uncensored-merged"

    # Step 1: Load base model
    print_section("Loading Base Model", "1/3")
    print(f"  Loading: {base_model_name}")

    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        device_map="cpu",
        torch_dtype=torch.float16,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(
        base_model_name,
        trust_remote_code=True
    )

    print("  ✓ Base model loaded")

    # Step 2: Load and merge LoRA
    print_section("Merging LoRA Adapter", "2/3")
    print(f"  Loading LoRA from: {lora_path}")

    model = PeftModel.from_pretrained(base_model, lora_path)

    print("  Merging weights...")
    model = model.merge_and_unload()

    print("  ✓ Merge complete!")

    # Step 3: Save merged model
    print_section("Saving Merged Model", "3/3")
    print(f"  Saving to: {output_path}")

    model.save_pretrained(output_path)
    tokenizer.save_pretrained(output_path)

    # Calculate size
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(output_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)

    size_mb = total_size / (1024 * 1024)

    print(f"  ✓ Merged model saved successfully")
    print(f"  ✓ Size: {size_mb:.1f} MB")

    return output_path

def main():
    """Main merge pipeline"""
    print_section("QWEN3-0.6B LORA MERGE")
    print("\nThis script merges your trained LoRA adapter with the base model.\n")

    # Check if LoRA exists
    if not os.path.exists("qwen3-0.6b-uncensored-lora"):
        print("❌ ERROR: LoRA adapter not found")
        print("   Please ensure training completed successfully")
        return

    # Merge
    output_path = merge_lora()

    # Success
    print("\n" + "="*60)
    print("SUCCESS! Merged model ready")
    print("="*60)
    print(f"\nMerged model location: {output_path}/")
    print("\nNext steps:")
    print("  1. Deploy to Ollama (quick test)")
    print("  2. Test with transformers library")
    print("\nLet's deploy to Ollama for easy testing...")

if __name__ == "__main__":
    main()
