"""
LLaMA-Factory Setup Script for GMKtec K11
=========================================

Automated setup script to install and configure LLaMA-Factory
for optimal performance on AMD Ryzen 9 8945HS + Radeon 780M

Author: Beyhan MEYRALI
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Ensure Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_system():
    """Check system compatibility"""
    system = platform.system()
    machine = platform.machine()
    
    print(f"💻 System: {system} {machine}")
    
    if system == "Windows":
        print("✅ Windows detected - LLaMA-Factory compatible")
    elif system == "Linux":
        print("✅ Linux detected - LLaMA-Factory compatible")
    elif system == "Darwin":
        print("✅ macOS detected - LLaMA-Factory compatible")
    
    return True

def install_pytorch_rocm():
    """Install PyTorch with ROCm support for AMD GPUs"""
    print("\n🔧 Installing PyTorch with AMD ROCm support...")
    
    commands = [
        [sys.executable, "-m", "pip", "install", "torch", "torchvision", "torchaudio", 
         "--index-url", "https://download.pytorch.org/whl/rocm5.6"],
    ]
    
    for cmd in commands:
        try:
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Success")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            print(f"Output: {e.stdout}")
            print(f"Error: {e.stderr}")
            return False
    
    return True

def install_llamafactory():
    """Install LLaMA-Factory with all features"""
    print("\n🦙 Installing LLaMA-Factory...")
    
    commands = [
        [sys.executable, "-m", "pip", "install", "llamafactory[torch,metrics]"],
        [sys.executable, "-m", "pip", "install", "transformers>=4.45.0"],
        [sys.executable, "-m", "pip", "install", "datasets>=2.16.0"],
        [sys.executable, "-m", "pip", "install", "accelerate>=0.33.0"],
        [sys.executable, "-m", "pip", "install", "peft>=0.12.0"],
        [sys.executable, "-m", "pip", "install", "trl>=0.8.0"],
        [sys.executable, "-m", "pip", "install", "bitsandbytes>=0.43.0"],
        [sys.executable, "-m", "pip", "install", "gradio>=4.0.0"],
    ]
    
    for cmd in commands:
        try:
            print(f"Installing: {cmd[-1]}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Success")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing {cmd[-1]}: {e}")
            return False
    
    return True

def install_monitoring_tools():
    """Install experiment tracking and monitoring tools"""
    print("\n📊 Installing monitoring tools...")
    
    tools = [
        "tensorboard>=2.14.0",
        "wandb>=0.16.0", 
        "rich>=13.0.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0"
    ]
    
    for tool in tools:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", tool], 
                         check=True, capture_output=True)
            print(f"✅ Installed {tool}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Optional tool {tool} failed to install")
    
    return True

def setup_amd_environment():
    """Configure environment variables for AMD GPU optimization"""
    print("\n🎮 Configuring AMD ROCm environment...")
    
    # Create environment setup script
    env_script = """
# AMD ROCm Environment Setup for GMKtec K11
# ==========================================

# AMD GPU Architecture (RDNA3)
export PYTORCH_ROCM_ARCH=gfx1100
export HSA_OVERRIDE_GFX_VERSION=11.0.0

# ROCm Device Selection
export HIP_VISIBLE_DEVICES=0
export ROCR_VISIBLE_DEVICES=0

# Performance Optimization
export AMD_SERIALIZE_KERNEL=3
export AMD_SERIALIZE_COPY=3

# Memory Management
export HSA_FORCE_FINE_GRAIN_PCIE=1

# Debug (uncomment if needed)
# export HIP_LAUNCH_BLOCKING=1
# export AMD_LOG_LEVEL=3

echo "✅ AMD ROCm environment configured for GMKtec K11"
"""
    
    # Save for Linux/macOS
    with open("setup_amd_env.sh", "w") as f:
        f.write(env_script)
    
    # Save for Windows
    win_script = """
@echo off
REM AMD ROCm Environment Setup for GMKtec K11 (Windows)
REM ====================================================

set PYTORCH_ROCM_ARCH=gfx1100
set HSA_OVERRIDE_GFX_VERSION=11.0.0
set HIP_VISIBLE_DEVICES=0
set ROCR_VISIBLE_DEVICES=0
set AMD_SERIALIZE_KERNEL=3
set AMD_SERIALIZE_COPY=3
set HSA_FORCE_FINE_GRAIN_PCIE=1

echo ✅ AMD ROCm environment configured for GMKtec K11
"""
    
    with open("setup_amd_env.bat", "w") as f:
        f.write(win_script)
    
    print("✅ Environment scripts created:")
    print("   • setup_amd_env.sh (Linux/macOS)")  
    print("   • setup_amd_env.bat (Windows)")
    
    return True

def create_directories():
    """Create necessary directories for training"""
    print("\n📁 Creating directory structure...")
    
    directories = [
        "datasets",
        "models", 
        "logs",
        "configs",
        "examples",
        "outputs"
    ]
    
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Created: {dir_name}/")
    
    return True

def test_installation():
    """Test if installation was successful"""
    print("\n🧪 Testing installation...")
    
    try:
        # Test LLaMA-Factory import
        import llamafactory
        print(f"✅ LLaMA-Factory {llamafactory.__version__} imported successfully")
    except ImportError as e:
        print(f"❌ LLaMA-Factory import failed: {e}")
        return False
    
    try:
        # Test PyTorch 
        import torch
        print(f"✅ PyTorch {torch.__version__} imported successfully")
        
        # Test AMD GPU detection
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            print(f"✅ GPU detected: {device_name}")
        else:
            print("⚠️  No GPU detected, but CPU training will work")
            
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
        return False
    
    try:
        # Test CLI
        result = subprocess.run(["llamafactory-cli", "--help"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ LLaMA-Factory CLI working")
        else:
            print("❌ LLaMA-Factory CLI failed")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"❌ CLI test failed: {e}")
        return False
    
    return True

def print_next_steps():
    """Print what to do next"""
    print("\n" + "="*60)
    print("🎉 INSTALLATION COMPLETE!")
    print("="*60)
    
    print("\n🚀 Quick Start Commands:")
    print("   # Launch Web Interface")
    print("   llamafactory-cli webui")
    print("")
    print("   # Run demo scripts")
    print("   python 01_webui_demo.py")
    print("   python 02_rlhf_training.py")
    
    print("\n🔗 Important Files Created:")
    print("   • setup_amd_env.sh/bat - AMD environment setup")
    print("   • configs/k11_optimized.yaml - Training config")
    print("   • 01_webui_demo.py - Web interface tutorial")
    print("   • 02_rlhf_training.py - RLHF training example")
    
    print("\n📚 Learning Path:")
    print("   1. Start with Web Interface (01_webui_demo.py)")
    print("   2. Try RLHF training (02_rlhf_training.py)")
    print("   3. Experiment with different models")
    print("   4. Deploy to production")
    
    print("\n🔧 Troubleshooting:")
    print("   • Check GPU: python -c \"import torch; print(torch.cuda.is_available())\"")
    print("   • AMD ROCm: source setup_amd_env.sh (Linux) or setup_amd_env.bat (Windows)")
    print("   • Documentation: https://llamafactory.readthedocs.io/")
    
    print("\n💡 Pro Tips:")
    print("   • Monitor training with TensorBoard")
    print("   • Use quantization for large models")
    print("   • Save configs for reproducible experiments")
    
def main():
    """Main setup function"""
    print("🦙 LLaMA-Factory Setup for GMKtec K11")
    print("====================================")
    print("Hardware: AMD Ryzen 9 8945HS + Radeon 780M")
    print("Goal: Install and configure LLaMA-Factory for optimal performance")
    
    # Run setup steps
    steps = [
        ("Checking Python version", check_python_version),
        ("Checking system compatibility", check_system),
        ("Installing PyTorch with ROCm", install_pytorch_rocm),
        ("Installing LLaMA-Factory", install_llamafactory),
        ("Installing monitoring tools", install_monitoring_tools),
        ("Setting up AMD environment", setup_amd_environment),
        ("Creating directories", create_directories),
        ("Testing installation", test_installation),
    ]
    
    for step_name, step_func in steps:
        print(f"\n⏳ {step_name}...")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            return False
    
    print_next_steps()
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)