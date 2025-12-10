#!/usr/bin/env python3
"""
03_merge_and_convert.py - Merge LoRA adapter and convert to GGUF

This script:
1. Loads the trained LoRA adapter
2. Merges it with the base Qwen3-4B model
3. Saves the merged model in 16-bit precision
4. Converts to GGUF format for Ollama/llama.cpp

Author: Beyhan MEYRALI
Created: 2025
"""

from unsloth import FastLanguageModel
import subprocess
import os
import sys

def print_section(title, step=None):
    """Print formatted section header"""
    print("\n" + "="*60)
    if step:
        print(f"[{step}] {title}")
    else:
        print(title)
    print("="*60)

def check_lora_exists(lora_path="qwen3-4b-uncensored-lora"):
    """Check if LoRA adapter exists"""
    if not os.path.exists(lora_path):
        print(f"❌ ERROR: LoRA adapter not found at: {lora_path}")
        print("\nPlease run 02_train_uncensored_qwen3_4b.py first to train the model.")
        sys.exit(1)

def load_lora(lora_path="qwen3-4b-uncensored-lora"):
    """Load the trained LoRA adapter"""
    print_section("Loading LoRA Adapter", "1/3")

    print(f"  Loading from: {lora_path}")

    model, tokenizer = FastLanguageModel.from_pretrained(
        lora_path,
        dtype=None,
        load_in_4bit=False,  # Load full precision for merging
    )

    print("  ✓ LoRA adapter loaded successfully")

    return model, tokenizer

def merge_and_save(model, tokenizer, output_path="qwen3-4b-uncensored-merged-16bit"):
    """Merge LoRA with base model and save"""
    print_section("Merging LoRA with Base Model", "2/3")

    print("  Merging LoRA adapter with base Qwen3-4B...")
    print("  This may take a few minutes...")

    model = FastLanguageModel.merge_and_unload(model)

    print("  ✓ Merge complete!")
    print(f"\n  Saving merged model to: {output_path}")

    model.save_pretrained_merged(
        output_path,
        tokenizer,
        save_method="merged_16bit",  # 16-bit for best quality
    )

    # Calculate size
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(output_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)

    size_gb = total_size / (1024**3)

    print(f"  ✓ Merged model saved successfully")
    print(f"  ✓ Size: {size_gb:.2f} GB")

    return output_path

def convert_to_gguf(model_path, output_file="qwen3-4b-uncensored.Q4_K_M.gguf"):
    """Convert merged model to GGUF format"""
    print_section("Converting to GGUF Format", "3/3")

    print("  Target format: Q4_K_M (best balance of quality/size)")
    print("  Expected size: ~2.8 GB\n")

    # Check if llama.cpp is available
    llama_cpp_script = "llama.cpp/convert-hf-to-gguf.py"

    if not os.path.exists(llama_cpp_script):
        print("  ⚠ llama.cpp not found")
        print("\n  To install llama.cpp:")
        print("    git clone https://github.com/ggerganov/llama.cpp")
        print("    cd llama.cpp")
        print("    pip install -r requirements.txt")
        print("    python setup.py install")
        print("\n  Alternative: Use the merged 16-bit model directly with transformers")
        return False

    # Convert to GGUF
    try:
        print("  Converting... (this may take 5-10 minutes)")
        result = subprocess.run(
            [
                "python", llama_cpp_script,
                model_path,
                "--outfile", output_file,
                "--outtype", "q4_k"
            ],
            check=True,
            capture_output=True,
            text=True
        )

        if os.path.exists(output_file):
            size_gb = os.path.getsize(output_file) / (1024**3)
            print(f"\n  ✓ GGUF conversion successful!")
            print(f"  ✓ Output: {output_file}")
            print(f"  ✓ Size: {size_gb:.2f} GB")
            return True
        else:
            print("  ❌ Conversion completed but output file not found")
            return False

    except subprocess.CalledProcessError as e:
        print(f"\n  ❌ Conversion failed: {e}")
        print(f"\n  Error output:\n{e.stderr}")
        print("\n  You can still use the merged 16-bit model with transformers!")
        return False

def main():
    """Main conversion pipeline"""
    print_section("MERGE & CONVERT TO GGUF")
    print("\nThis script will merge your trained LoRA adapter with the")
    print("base model and convert it to GGUF format for easy deployment.\n")

    # Check if LoRA exists
    check_lora_exists()

    # Load LoRA
    model, tokenizer = load_lora()

    # Merge and save
    merged_path = merge_and_save(model, tokenizer)

    # Convert to GGUF
    gguf_success = convert_to_gguf(merged_path)

    # Final summary
    print("\n" + "="*60)
    if gguf_success:
        print("SUCCESS! Model ready for deployment")
    else:
        print("PARTIAL SUCCESS - Merge complete, GGUF conversion skipped")
    print("="*60)

    print("\nAvailable model formats:")
    print(f"  1. Merged 16-bit: {merged_path}/")
    print("     → Use with transformers library")
    print("     → Best quality, requires ~8GB VRAM")

    if gguf_success:
        print("\n  2. GGUF Q4_K_M: qwen3-4b-uncensored.Q4_K_M.gguf")
        print("     → Use with Ollama or llama.cpp")
        print("     → Efficient inference, requires ~2.8GB VRAM")

        print("\nNext steps:")
        print("  1. Run: python 04_deploy_ollama.py")
        print("     → Deploy to Ollama for easy API access")
        print("\n  2. Or run: python 05_test_with_transformers.py")
        print("     → Test the merged model directly")
    else:
        print("\nNext step:")
        print("  Run: python 05_test_with_transformers.py")
        print("  → Test the merged model with transformers")

if __name__ == "__main__":
    main()
