#!/usr/bin/env python3
"""
00_prepare_environment.py - Pre-download models and datasets

This script prepares your environment by downloading all required models
and datasets BEFORE training, so you're ready to run the complete pipeline.

Run this ONCE before starting training.

Author: Beyhan MEYRALI
Created: 2025
"""

import os
import sys

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*60)
    print(title)
    print("="*60)

def check_python_version():
    """Check Python version"""
    print_section("CHECKING PYTHON VERSION")

    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False

    print("✓ Python version OK")
    return True

def check_packages():
    """Check if required packages are installed"""
    print_section("CHECKING REQUIRED PACKAGES")

    required = {
        "torch": "PyTorch",
        "transformers": "HuggingFace Transformers",
        "datasets": "HuggingFace Datasets",
        "accelerate": "HuggingFace Accelerate",
    }

    missing = []

    for package, name in required.items():
        try:
            __import__(package)
            print(f"✓ {name} installed")
        except ImportError:
            print(f"❌ {name} NOT installed")
            missing.append(package)

    if missing:
        print("\n" + "="*60)
        print("INSTALLATION REQUIRED")
        print("="*60)
        print("\nMissing packages:", ", ".join(missing))
        print("\nTo install, run:")
        print("\n  pip install torch transformers datasets accelerate")
        print("\nFor NVIDIA GPUs:")
        print("  pip install torch --index-url https://download.pytorch.org/whl/cu121")
        print("\nFor AMD GPUs:")
        print("  pip install torch --index-url https://download.pytorch.org/whl/rocm5.6")
        return False

    return True

def check_gpu():
    """Check GPU availability"""
    print_section("CHECKING GPU")

    try:
        import torch

        if not torch.cuda.is_available():
            print("⚠️  WARNING: No GPU detected!")
            print("\nTraining requires a GPU:")
            print("  - NVIDIA: RTX 3060 8GB or better")
            print("  - AMD: Radeon 780M or RX 7600 8GB+")
            print("\nYou can still download models, but training will fail.")

            response = input("\nContinue anyway? (y/n): ")
            return response.lower() == 'y'

        device_name = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / 1024**3

        print(f"✓ GPU detected: {device_name}")
        print(f"✓ VRAM: {vram:.1f} GB")

        if vram < 7:
            print(f"\n⚠️  WARNING: Only {vram:.1f} GB VRAM")
            print("Training may fail or require reduced batch size")

        return True

    except Exception as e:
        print(f"❌ Error checking GPU: {e}")
        return False

def download_base_model():
    """Download Qwen3-4B-Base model"""
    print_section("DOWNLOADING QWEN3-4B-BASE MODEL")

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer

        model_name = "Qwen/Qwen3-4B-Base"
        print(f"\nModel: {model_name}")
        print("Size: ~8 GB")
        print("This may take 10-20 minutes on first run...")
        print("(cached locally for future use)\n")

        print("Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        print("✓ Tokenizer downloaded")

        print("\nDownloading model (this is the large download)...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="cpu",  # Keep on CPU to avoid GPU memory
            torch_dtype="auto",
            trust_remote_code=True
        )
        print("✓ Model downloaded")

        # Clean up memory
        del model
        del tokenizer

        print("\n✓ Qwen3-4B-Base ready!")
        print(f"Cached at: ~/.cache/huggingface/hub/")

        return True

    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def download_dataset():
    """Download EverythingLM dataset"""
    print_section("DOWNLOADING EVERYTHINGMLM DATASET")

    try:
        from datasets import load_dataset

        dataset_name = "cognitivecomputations/EverythingLM-Data"
        print(f"\nDataset: {dataset_name}")
        print("Size: ~2 GB")
        print("This may take 5-10 minutes...\n")

        print("Downloading dataset...")
        dataset = load_dataset(
            dataset_name,
            split="train"
        )

        print(f"\n✓ Dataset downloaded!")
        print(f"✓ Total conversations: {len(dataset):,}")
        print(f"Cached at: ~/.cache/huggingface/datasets/")

        # Show sample
        print("\nSample conversation:")
        sample = dataset[0]
        if "conversations" in sample:
            for turn in sample["conversations"][:2]:
                print(f"  {turn['from']}: {turn['value'][:80]}...")

        return True

    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def check_ollama():
    """Check Ollama installation"""
    print_section("CHECKING OLLAMA")

    import subprocess

    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            check=True
        )

        version = result.stdout.strip()
        print(f"✓ Ollama installed: {version}")

        # Check if running
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )
            print("✓ Ollama service running")

            # Show existing models
            if result.stdout.strip():
                print("\nExisting models:")
                for line in result.stdout.strip().split('\n')[1:]:  # Skip header
                    if line.strip():
                        print(f"  - {line.split()[0]}")

        except subprocess.TimeoutExpired:
            print("⚠️  Ollama service not responding")
            print("Run: ollama serve")
        except subprocess.CalledProcessError:
            print("⚠️  Ollama service not running")
            print("Run: ollama serve")

        return True

    except FileNotFoundError:
        print("❌ Ollama not installed")
        print("\nInstall from: https://ollama.ai")
        print("\n  Linux: curl -fsSL https://ollama.ai/install.sh | sh")
        print("  Windows: Download from https://ollama.ai/download")
        return False

def check_disk_space():
    """Check available disk space"""
    print_section("CHECKING DISK SPACE")

    import shutil

    # Check home directory
    stat = shutil.disk_usage(os.path.expanduser("~"))
    free_gb = stat.free / (1024**3)

    print(f"Free space: {free_gb:.1f} GB")

    required = 20  # ~8GB model + ~2GB dataset + ~8GB output + buffer

    if free_gb < required:
        print(f"⚠️  WARNING: Low disk space")
        print(f"Required: ~{required} GB")
        print(f"Available: {free_gb:.1f} GB")
        return False

    print(f"✓ Sufficient space (need ~{required} GB)")
    return True

def main():
    """Main preparation pipeline"""
    print_section("ENVIRONMENT PREPARATION")
    print("\nThis script will download all required models and datasets")
    print("for the uncensored Qwen3-4B fine-tuning tutorial.\n")

    # Pre-flight checks
    print_section("PRE-FLIGHT CHECKS")

    checks = [
        ("Python version", check_python_version),
        ("Required packages", check_packages),
        ("GPU availability", check_gpu),
        ("Disk space", check_disk_space),
        ("Ollama", check_ollama),
    ]

    all_ok = True
    for name, check_func in checks:
        if not check_func():
            all_ok = False

    if not all_ok:
        print("\n" + "="*60)
        print("❌ PREPARATION FAILED")
        print("="*60)
        print("\nPlease resolve the issues above before continuing.")
        sys.exit(1)

    # Ask user if they want to proceed
    print("\n" + "="*60)
    print("Ready to download models and datasets")
    print("="*60)
    print("\nTotal download size: ~10 GB")
    print("Estimated time: 15-30 minutes")
    print("Downloads will be cached for future use")

    response = input("\nProceed with downloads? (y/n): ")
    if response.lower() != 'y':
        print("\nAborted by user.")
        sys.exit(0)

    # Download model
    if not download_base_model():
        print("\n❌ Model download failed")
        sys.exit(1)

    # Download dataset
    if not download_dataset():
        print("\n❌ Dataset download failed")
        sys.exit(1)

    # Success!
    print("\n" + "="*60)
    print("✓ PREPARATION COMPLETE!")
    print("="*60)

    print("\nYour environment is ready for fine-tuning!")
    print("\nNext steps:")
    print("  1. python 01_download.py        # Test base model")
    print("  2. python 02_train_uncensored_qwen3_4b.py  # Train (~30-45 min)")
    print("  3. python 03_merge_and_convert.py          # Merge & convert")
    print("  4. python 04_deploy_ollama.py              # Deploy to Ollama")
    print("  5. ollama run qwen3-uncensored             # Use your model!")

    print("\nCached files location:")
    print(f"  Models: ~/.cache/huggingface/hub/")
    print(f"  Datasets: ~/.cache/huggingface/datasets/")

if __name__ == "__main__":
    main()
