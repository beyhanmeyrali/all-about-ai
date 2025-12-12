#!/bin/bash
# RTX 5060 PyTorch Setup Script for WSL
# Requires: NVIDIA Driver 577.xx+ installed on Windows host

set -e  # Exit on error

echo "========================================"
echo "RTX 5060 PyTorch Setup for WSL"
echo "========================================"
echo

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running in WSL
if ! grep -qiE '(microsoft|wsl)' /proc/version; then
    echo -e "${YELLOW}Warning: Not running in WSL. This script is optimized for WSL.${NC}"
fi

# Step 1: Check Python
echo -e "${GREEN}[1/5] Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "  ✓ Found: $PYTHON_VERSION"
else
    echo -e "${RED}  ✗ Python3 not found. Install with: sudo apt-get install python3 python3-pip python3-venv${NC}"
    exit 1
fi

# Step 2: Check NVIDIA driver accessibility
echo -e "${GREEN}[2/5] Checking NVIDIA driver...${NC}"
if command -v nvidia-smi &> /dev/null; then
    echo "  ✓ nvidia-smi found"
    nvidia-smi --query-gpu=name,driver_version --format=csv,noheader
else
    echo -e "${YELLOW}  ⚠ nvidia-smi not found in WSL${NC}"
    echo "  Installing WSL CUDA toolkit..."

    # Install CUDA toolkit for WSL
    echo "  Downloading CUDA keyring..."
    wget -q https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
    sudo dpkg -i cuda-keyring_1.1-1_all.deb
    rm cuda-keyring_1.1-1_all.deb

    echo "  Updating package list..."
    sudo apt-get update -qq

    echo "  Installing CUDA toolkit 12.8 (this may take several minutes)..."
    sudo apt-get install -y cuda-toolkit-12-8

    # Add to PATH
    if ! grep -q "cuda-12.8/bin" ~/.bashrc; then
        echo 'export PATH=/usr/local/cuda-12.8/bin:$PATH' >> ~/.bashrc
        echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.8/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
    fi

    export PATH=/usr/local/cuda-12.8/bin:$PATH
    export LD_LIBRARY_PATH=/usr/local/cuda-12.8/lib64:$LD_LIBRARY_PATH

    echo "  ✓ CUDA toolkit installed"
fi

# Step 3: Create Python virtual environment
echo -e "${GREEN}[3/5] Creating Python virtual environment...${NC}"
VENV_PATH="$HOME/pytorch-rtx5060"

if [ -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}  ⚠ Virtual environment already exists at $VENV_PATH${NC}"
    read -p "  Remove and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$VENV_PATH"
    else
        echo "  Skipping venv creation"
    fi
fi

if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH"
    echo "  ✓ Virtual environment created at $VENV_PATH"
else
    echo "  ✓ Using existing virtual environment"
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Step 4: Install PyTorch with CUDA 12.8
echo -e "${GREEN}[4/5] Installing PyTorch with CUDA 12.8...${NC}"

# Uninstall old PyTorch versions
pip uninstall -y torch torchvision torchaudio 2>/dev/null || true

# Install PyTorch 2.6+ with CUDA 12.8
echo "  Installing PyTorch (this may take a few minutes)..."
pip install --upgrade pip -q
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

echo "  ✓ PyTorch installed"

# Step 5: Verify installation
echo -e "${GREEN}[5/5] Verifying GPU detection...${NC}"

python3 << EOF
import torch
import sys

print("\n" + "="*50)
print("PyTorch Configuration")
print("="*50)

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"Device count: {torch.cuda.device_count()}")
    print(f"Device name: {torch.cuda.get_device_name(0)}")

    cap = torch.cuda.get_device_capability(0)
    print(f"Compute capability: sm_{cap[0]}{cap[1]}")

    mem_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f"GPU Memory: {mem_gb:.2f} GB")

    # Quick test
    try:
        x = torch.randn(100, 100, device='cuda')
        y = torch.randn(100, 100, device='cuda')
        z = torch.matmul(x, y)
        print("\n✓ GPU computation test: PASSED")
    except Exception as e:
        print(f"\n✗ GPU computation test: FAILED - {e}")
        sys.exit(1)
else:
    print("\n✗ CUDA not available!")
    print("\nTroubleshooting:")
    print("1. Ensure NVIDIA driver 577.xx+ installed on Windows")
    print("2. Run 'nvidia-smi' in Windows PowerShell to verify")
    print("3. Restart WSL: wsl --shutdown (in PowerShell)")
    sys.exit(1)

print("="*50)
EOF

if [ $? -eq 0 ]; then
    echo
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ Setup completed successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo
    echo "To activate this environment in the future:"
    echo "  source $VENV_PATH/bin/activate"
    echo
    echo "To verify your setup anytime:"
    echo "  python3 verify_rtx5060.py"
    echo
    echo "Next steps:"
    echo "  1. cd /workspace/all-about-ai/fine-tuning/00-first-time-beginner"
    echo "  2. Follow the Qwen3 tutorial"
    echo
else
    echo
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}✗ Setup encountered issues${NC}"
    echo -e "${RED}========================================${NC}"
    echo
    echo "Please check FIX_RTX5060_PYTORCH.md for troubleshooting"
    exit 1
fi
