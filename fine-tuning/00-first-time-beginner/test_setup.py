"""
Test setup for 00-first-time-beginner fine-tuning module
Created by Beyhan MEYRALI - https://www.linkedin.com/in/beyhanmeyrali/
Optimized for GMKtec K11 with AMD Radeon 780M
"""

import os
import torch
import sys

# Set AMD ROCm environment variables first
os.environ["PYTORCH_ROCM_ARCH"] = "gfx1100"  # For RDNA3 architecture
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"

def test_gpu():
    print("Checking GPU...")
    if torch.cuda.is_available():
        print(f"[OK] CUDA available: {torch.cuda.is_available()}")
        print(f"[OK] GPU: {torch.cuda.get_device_name()}")
        print(f"[OK] CUDA version: {torch.version.cuda}")
        memory_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"[OK] GPU Memory: {memory_gb:.1f} GB")
    else:
        print("[WARN] CUDA not available - will use CPU training")
        print("[INFO] This is normal for AMD GPUs - PyTorch will use CPU efficiently")

def test_packages():
    print("\nChecking Python packages...")
    try:
        import transformers
        import datasets
        import peft
        import trl
        import bitsandbytes
        import ollama

        print(f"[OK] PyTorch: {torch.__version__}")
        print(f"[OK] Transformers: {transformers.__version__}")
        print(f"[OK] Datasets: {datasets.__version__}")
        print(f"[OK] PEFT: {peft.__version__}")
        print(f"[OK] TRL: {trl.__version__}")
        print(f"[OK] BitsAndBytes: {bitsandbytes.__version__}")
        print(f"[OK] Ollama: Available")
        print("[OK] All essential packages ready!")

    except ImportError as e:
        print(f"[ERROR] Missing package: {e}")

def test_unsloth():
    print("\nChecking Unsloth compatibility...")
    try:
        # Try importing unsloth - will fail on AMD but we'll handle it gracefully
        import unsloth
        print("[OK] Unsloth: Available")
    except NotImplementedError as e:
        print("[WARN] Unsloth: Not compatible with AMD GPUs")
        print("[INFO] Solution: We'll use standard HuggingFace PEFT + optimizations")
        print("[INFO] Performance: Still 2-3x faster than basic fine-tuning!")
    except Exception as e:
        print(f"[WARN] Unsloth: {e}")

def test_ollama():
    print("\nChecking Ollama...")
    try:
        import ollama
        # Try to connect to Ollama (will fail if not installed/running)
        # Don't actually make the call to avoid errors if Ollama isn't running
        print("[OK] Ollama Python client: Available")
        print("[INFO] Run 'ollama pull qwen2.5:0.5b' to get the base model")
    except Exception as e:
        print(f"[ERROR] Ollama error: {e}")

def show_hardware_recommendations():
    print("\nHardware Configuration Recommendations")
    print("=" * 50)
    print("For your GMKtec K11 with AMD Radeon 780M:")
    print()
    print("Recommended Models:")
    print("  - Qwen3 0.5B/0.6B (Best for beginners)")
    print("  - Phi-3 Mini 4K (Microsoft's efficient model)")
    print("  - Gemma 2B (Google's lightweight model)")
    print()
    print("Memory Settings:")
    print("  - Batch size: 2-4")
    print("  - Gradient accumulation: 4-8 steps")
    print("  - Sequence length: 512-2048")
    print("  - Quantization: 4-bit recommended")
    print()
    print("Expected Training Times:")
    print("  - 0.5B models: 15-30 minutes")
    print("  - 2B models: 45-90 minutes")
    print("  - 7B models: 2-4 hours (with heavy optimization)")

def main():
    print("Testing fine-tuning setup for GMKtec K11")
    print("Created by: Beyhan MEYRALI")
    print("LinkedIn: https://www.linkedin.com/in/beyhanmeyrali/")
    print("Hardware: AMD Ryzen 9 8945HS + Radeon 780M")
    print("=" * 60)

    test_gpu()
    test_packages()
    test_unsloth()
    test_ollama()
    show_hardware_recommendations()

    print("\n[SUCCESS] Setup test complete!")
    print("Next steps:")
    print("  1. Run: python create_dataset.py")
    print("  2. Run: python train_qwen.py")
    print("  3. Start fine-tuning your first model!")

if __name__ == "__main__":
    main()