"""
LLaMA-Factory Web Interface Demo for GMKtec K11
===============================================

Your first introduction to zero-code fine-tuning through a beautiful web interface.
This script helps you launch and understand the LLaMA-Factory WebUI.

Author: Beyhan MEYRALI
Hardware: GMKtec K11 (AMD Ryzen 9 8945HS + Radeon 780M)
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path
import time

# AMD ROCm optimization for K11
os.environ["PYTORCH_ROCM_ARCH"] = "gfx1100"
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"

def check_installation():
    """Verify LLaMA-Factory is properly installed"""
    try:
        import llamafactory
        print(f"✅ LLaMA-Factory {llamafactory.__version__} detected")
        return True
    except ImportError:
        print("❌ LLaMA-Factory not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "llamafactory[torch,metrics]"])
        return True

def check_amd_gpu():
    """Check AMD GPU availability"""
    try:
        import torch
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            print(f"✅ GPU detected: {device_name}")
            return True
        else:
            print("⚠️  No GPU detected, using CPU (slower but works)")
            return False
    except Exception as e:
        print(f"⚠️  GPU check failed: {e}")
        return False

def create_sample_dataset():
    """Create a simple dataset for demo purposes"""
    dataset_dir = Path("datasets")
    dataset_dir.mkdir(exist_ok=True)
    
    sample_data = [
        {
            "instruction": "What is machine learning?",
            "input": "",
            "output": "Machine learning is a branch of artificial intelligence that enables computers to learn and make decisions from data without explicit programming."
        },
        {
            "instruction": "Explain fine-tuning in simple terms",
            "input": "",
            "output": "Fine-tuning is like teaching a smart student (pre-trained model) a new subject by showing examples specific to that subject, rather than starting their education from scratch."
        },
        {
            "instruction": "What are the benefits of using LoRA?",
            "input": "",
            "output": "LoRA (Low-Rank Adaptation) allows efficient fine-tuning by updating only a small subset of model parameters, reducing memory usage by up to 95% while maintaining performance."
        },
        {
            "instruction": "How does quantization help in AI training?",
            "input": "",
            "output": "Quantization reduces model size and memory usage by representing weights with fewer bits (e.g., 4-bit instead of 16-bit), making large models trainable on consumer hardware."
        },
        {
            "instruction": "What is the GMKtec K11 good for in AI?",
            "input": "",
            "output": "The GMKtec K11 with AMD Ryzen 9 8945HS and Radeon 780M is excellent for AI fine-tuning, offering 32GB+ RAM for large datasets and AMD GPU acceleration with ROCm support."
        }
    ]
    
    import json
    with open(dataset_dir / "demo_dataset.json", "w") as f:
        json.dump(sample_data, f, indent=2)
    
    print(f"✅ Sample dataset created at {dataset_dir / 'demo_dataset.json'}")
    return dataset_dir / "demo_dataset.json"

def launch_webui():
    """Launch the LLaMA-Factory Web Interface"""
    print("\n🚀 Launching LLaMA-Factory Web Interface...")
    print("📍 This will open in your browser at: http://localhost:7860")
    print("\n💡 What you can do in the Web Interface:")
    print("   • Select models from 100+ options")
    print("   • Upload and configure datasets")
    print("   • Choose training methods (LoRA, QLoRA, DPO)")
    print("   • Monitor training progress in real-time")
    print("   • Export trained models")
    print("\n⏱️  Starting in 3 seconds...")
    
    time.sleep(3)
    
    try:
        # Launch the web interface
        result = subprocess.run([
            "llamafactory-cli", "webui"
        ], cwd=os.getcwd())
        
    except KeyboardInterrupt:
        print("\n🛑 WebUI stopped by user")
    except Exception as e:
        print(f"❌ Error launching WebUI: {e}")
        print("💡 Try running manually: llamafactory-cli webui")

def print_webui_guide():
    """Print a guide for using the Web Interface"""
    print("\n" + "="*60)
    print("🎯 WEB INTERFACE QUICK START GUIDE")
    print("="*60)
    
    print("\n1️⃣ MODEL SELECTION:")
    print("   • Go to 'Train' tab")
    print("   • Choose 'Model name': qwen3 (latest generation)")
    print("   • Select 'Model path': Qwen/Qwen3-0.6B-Instruct (or Qwen3-1.7B-Instruct)")
    
    print("\n2️⃣ DATASET CONFIGURATION:")
    print("   • Select 'Dataset': Browse and upload your demo_dataset.json")
    print("   • Choose 'Template': qwen")
    print("   • Set 'Cutoff length': 1024")
    
    print("\n3️⃣ TRAINING SETTINGS (K11 OPTIMIZED):")
    print("   • Training stage: Supervised Fine-Tuning")
    print("   • Fine-tuning method: LoRA")
    print("   • LoRA rank: 16")
    print("   • LoRA alpha: 32")
    print("   • Batch size: 2")
    print("   • Learning rate: 5e-5")
    print("   • Epochs: 3")
    
    print("\n4️⃣ ADVANCED SETTINGS:")
    print("   • Enable quantization: 4-bit")
    print("   • Gradient accumulation: 8")
    print("   • Save steps: 500")
    
    print("\n5️⃣ START TRAINING:")
    print("   • Click 'Start' button")
    print("   • Monitor progress in real-time")
    print("   • Expected time: 20-30 minutes on K11")
    
    print("\n6️⃣ AFTER TRAINING:")
    print("   • Go to 'Export' tab")
    print("   • Export as merged model or LoRA adapters")
    print("   • Test your model in 'Chat' tab")
    
    print("\n💡 Pro Tips:")
    print("   • Use 'Preview' to check your data format")
    print("   • Monitor GPU usage in Task Manager")
    print("   • Save configurations for future use")
    
    print("\n🔗 Useful Links:")
    print("   • Documentation: https://llamafactory.readthedocs.io/")
    print("   • Supported Models: 100+ including Qwen3, LLaMA, Mistral")
    print("   • GitHub Issues: For troubleshooting")

def main():
    """Main demo function"""
    print("🎯 LLaMA-Factory Web Interface Demo")
    print("===================================")
    print("Hardware: GMKtec K11 (AMD Ryzen 9 8945HS + Radeon 780M)")
    print("Goal: Learn zero-code fine-tuning through beautiful web interface")
    
    # Step 1: Check installation
    if not check_installation():
        return
    
    # Step 2: Check GPU
    gpu_available = check_amd_gpu()
    
    # Step 3: Create demo dataset
    dataset_path = create_sample_dataset()
    
    # Step 4: Print usage guide
    print_webui_guide()
    
    # Step 5: Launch WebUI
    user_input = input("\n🚀 Ready to launch Web Interface? (y/n): ")
    if user_input.lower() in ['y', 'yes']:
        launch_webui()
    else:
        print("💡 You can launch manually later with: llamafactory-cli webui")
    
    print("\n✨ Demo completed!")
    print("🎯 Next steps:")
    print("   • Experiment with different models in WebUI")
    print("   • Try advanced training methods (DPO, PPO)")
    print("   • Check out 02_rlhf_training.py for programmatic training")

if __name__ == "__main__":
    main()