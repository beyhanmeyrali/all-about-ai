#!/usr/bin/env python3
"""
Deploy Custom Trained Model to Ollama

This script automates the process of converting a HuggingFace model to GGUF format
and deploying it to Ollama.

Requirements:
  - llama.cpp cloned at /tmp/llama.cpp
  - Ollama installed and running
  - Custom trained model in HuggingFace format

Usage:
  python3 08_deploy_to_ollama.py --model qwen3-0.6b-uncensored-merged --name qwen3-uncensored

Author: Beyhan MEYRALI
Date: 2025-12-10
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")

    # Check llama.cpp
    if not Path("/tmp/llama.cpp/convert_hf_to_gguf.py").exists():
        print("❌ llama.cpp not found at /tmp/llama.cpp")
        print("   Run: cd /tmp && git clone https://github.com/ggerganov/llama.cpp.git")
        return False

    # Check Ollama
    try:
        subprocess.run(["ollama", "list"], capture_output=True, check=True)
        print("✅ Ollama is installed and running")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("❌ Ollama not found or not running")
        print("   Install from: https://ollama.ai")
        return False

    print("✅ All requirements met\n")
    return True


def convert_to_gguf(model_path, output_path, precision="f16"):
    """Convert HuggingFace model to GGUF format"""
    print(f"🔄 Converting {model_path} to GGUF format ({precision})...")

    cmd = [
        "python3",
        "/tmp/llama.cpp/convert_hf_to_gguf.py",
        model_path,
        "--outfile", output_path,
        "--outtype", precision
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ GGUF conversion successful: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Conversion failed:")
        print(e.stderr)
        return False


def create_modelfile(gguf_path, modelfile_path, system_prompt=None):
    """Create Modelfile for Ollama"""
    print(f"📝 Creating Modelfile at {modelfile_path}...")

    if system_prompt is None:
        system_prompt = "You are a helpful AI assistant. You provide direct, honest answers to all questions."

    modelfile_content = f"""FROM ./{gguf_path}

# Temperature - higher = more creative, lower = more focused
PARAMETER temperature 0.7

# Top-p sampling
PARAMETER top_p 0.9

# System message
SYSTEM {system_prompt}
"""

    with open(modelfile_path, "w") as f:
        f.write(modelfile_content)

    print(f"✅ Modelfile created: {modelfile_path}\n")


def deploy_to_ollama(model_name, modelfile_path):
    """Deploy model to Ollama"""
    print(f"🚀 Deploying to Ollama as '{model_name}'...")

    cmd = ["ollama", "create", model_name, "-f", modelfile_path]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Model deployed successfully: {model_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed:")
        print(e.stderr)
        return False


def test_model(model_name):
    """Test the deployed model"""
    print(f"\n🧪 Testing model '{model_name}'...")

    test_prompt = "What is 2+2?"
    cmd = ["ollama", "run", model_name, test_prompt]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=60)
        print(f"✅ Model test successful!")
        print(f"\nPrompt: {test_prompt}")
        print(f"Response: {result.stdout[:200]}...")
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"❌ Model test failed:")
        print(str(e))
        return False


def main():
    parser = argparse.ArgumentParser(description="Deploy custom trained model to Ollama")
    parser.add_argument("--model", required=True, help="Path to HuggingFace model directory")
    parser.add_argument("--name", required=True, help="Name for Ollama model")
    parser.add_argument("--precision", default="f16", choices=["f16", "f32", "bf16", "q8_0"],
                        help="GGUF precision (default: f16)")
    parser.add_argument("--system-prompt", help="Custom system prompt")
    parser.add_argument("--skip-test", action="store_true", help="Skip model testing")

    args = parser.parse_args()

    print("""
╔═══════════════════════════════════════════════════════════════╗
║       Deploy Custom Model to Ollama                          ║
║       Author: Beyhan MEYRALI                                 ║
╚═══════════════════════════════════════════════════════════════╝
""")

    # Check requirements
    if not check_requirements():
        sys.exit(1)

    # Paths
    model_path = Path(args.model)
    if not model_path.exists():
        print(f"❌ Model not found: {model_path}")
        sys.exit(1)

    gguf_filename = f"{args.name}-{args.precision}.gguf"
    gguf_path = Path(gguf_filename)
    modelfile_path = Path(f"Modelfile-{args.name}")

    # Step 1: Convert to GGUF
    if gguf_path.exists():
        print(f"⚠️  GGUF file already exists: {gguf_path}")
        response = input("Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Using existing GGUF file...")
        else:
            if not convert_to_gguf(str(model_path), str(gguf_path), args.precision):
                sys.exit(1)
    else:
        if not convert_to_gguf(str(model_path), str(gguf_path), args.precision):
            sys.exit(1)

    # Step 2: Create Modelfile
    create_modelfile(gguf_filename, modelfile_path, args.system_prompt)

    # Step 3: Deploy to Ollama
    if not deploy_to_ollama(args.name, str(modelfile_path)):
        sys.exit(1)

    # Step 4: Test model
    if not args.skip_test:
        if not test_model(args.name):
            print("⚠️  Model deployment succeeded but testing failed")

    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                    🎉 DEPLOYMENT COMPLETE! 🎉                 ║
╚═══════════════════════════════════════════════════════════════╝

Model: {args.name}
GGUF: {gguf_path} ({gguf_path.stat().st_size / (1024**3):.2f} GB)
Modelfile: {modelfile_path}

To use the model:
  ollama run {args.name}

To use via API:
  curl -X POST http://localhost:11434/api/generate \\
    -d '{{"model": "{args.name}", "prompt": "Your question here"}}'

Enjoy your custom model! 🚀
""")


if __name__ == "__main__":
    main()
