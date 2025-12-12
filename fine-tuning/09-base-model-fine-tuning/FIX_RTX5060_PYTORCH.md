# Fix NVIDIA RTX 5060 PyTorch Setup on WSL

## Problem Identified

Your system shows:
- **Platform**: WSL (Windows Subsystem for Linux)
- **GPU**: NVIDIA RTX 5060 (not detected in WSL)
- **Issue**: NVIDIA drivers not accessible from WSL environment

## Critical RTX 5060 Information

⚠️ **IMPORTANT**: RTX 5060 uses **Blackwell architecture (sm_120)** which requires:
- NVIDIA Driver **577.xx or newer** (Windows)
- CUDA **12.8 or newer**
- PyTorch **2.6.0 or newer** with CUDA 12.8 support

## Solution: WSL CUDA Setup

### Step 1: Install NVIDIA Drivers on Windows (Host)

**On Windows (not WSL):**

1. Download latest NVIDIA Game Ready Driver (577.xx+):
   - https://www.nvidia.com/download/index.aspx
   - Select: RTX 50 Series → RTX 5060 → Windows 11/10

2. Install the driver and reboot Windows

3. Verify installation in Windows PowerShell:
```powershell
nvidia-smi
```

Should show RTX 5060 and Driver version 577.xx+

### Step 2: Install WSL CUDA Toolkit (In WSL)

**In WSL terminal (where you are now):**

```bash
# Remove old CUDA if present
sudo apt-get remove --purge nvidia-* cuda-* -y

# Add NVIDIA package repository
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update

# Install CUDA Toolkit 12.8 (or latest)
sudo apt-get install -y cuda-toolkit-12-8

# Add to PATH
echo 'export PATH=/usr/local/cuda-12.8/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.8/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Verify NVIDIA Setup in WSL

```bash
# Should now work:
nvidia-smi

# Check CUDA version:
nvcc --version
```

### Step 4: Install PyTorch with CUDA 12.8

**Create fresh Python environment:**

```bash
# Using conda (recommended):
conda create -n pytorch-rtx5060 python=3.11 -y
conda activate pytorch-rtx5060

# Or using venv:
python3 -m venv ~/pytorch-rtx5060
source ~/pytorch-rtx5060/bin/activate
```

**Install PyTorch with CUDA 12.8:**

```bash
# Uninstall any existing PyTorch
pip uninstall torch torchvision torchaudio -y

# Install PyTorch 2.6+ with CUDA 12.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

### Step 5: Verify PyTorch GPU Detection

```bash
python3 -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'CUDA version: {torch.version.cuda}')
print(f'Device count: {torch.cuda.device_count()}')
if torch.cuda.is_available():
    print(f'Device name: {torch.cuda.get_device_name(0)}')
    print(f'Device capability: {torch.cuda.get_device_capability(0)}')
    print(f'Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB')
"
```

**Expected output:**
```
PyTorch version: 2.6.0+cu128
CUDA available: True
CUDA version: 12.8
Device count: 1
Device name: NVIDIA GeForce RTX 5060
Device capability: (12, 0)  # sm_120 architecture
Memory: 16.00 GB
```

## Alternative: Native Windows Installation

If WSL continues to have issues, consider using **Windows native Python**:

### Windows Native Setup

**In Windows PowerShell (as Administrator):**

```powershell
# Install Python 3.11 from python.org if not present

# Create virtual environment
python -m venv C:\pytorch-rtx5060
C:\pytorch-rtx5060\Scripts\Activate.ps1

# Install PyTorch
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# Verify
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'No GPU')"
```

## Troubleshooting

### Issue: "CUDA not available" in PyTorch

**Solution 1 - Verify WSL CUDA:**
```bash
# Check if nvidia-smi works in WSL
nvidia-smi

# If not, reinstall WSL CUDA drivers on Windows:
# https://developer.nvidia.com/cuda/wsl
```

**Solution 2 - Check PyTorch CUDA version:**
```bash
# Ensure you're using cu128 (CUDA 12.8) not cu121 or cpu
pip list | grep torch
# Should show: torch 2.6.0+cu128
```

**Solution 3 - Update Windows NVIDIA Driver:**
```powershell
# In Windows, check driver version:
nvidia-smi
# Must be 577.xx or newer for RTX 5060
```

### Issue: "sm_120 not supported"

This means your CUDA/PyTorch is too old for RTX 5060:
- Update to CUDA 12.8+
- Update to PyTorch 2.6.0+
- Verify with: `python -c "import torch; print(torch.version.cuda)"`

### Issue: Out of Memory Errors

RTX 5060 has 16GB VRAM, use these settings:

```python
# Conservative config for 16GB VRAM
config = {
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 4,
    "max_seq_length": 2048,
    "bits": 4,  # Use 4-bit quantization
}

# For larger models (7B+)
config = {
    "per_device_train_batch_size": 2,
    "gradient_accumulation_steps": 8,
    "max_seq_length": 1024,
    "bits": 4,
    "double_quant": True,
}
```

## Quick Verification Script

Save and run this to verify your setup:

```python
# verify_rtx5060.py
import torch
import sys

def verify_gpu():
    print("=" * 60)
    print("RTX 5060 PyTorch Setup Verification")
    print("=" * 60)

    # PyTorch version
    print(f"\n✓ PyTorch version: {torch.__version__}")

    # CUDA availability
    cuda_available = torch.cuda.is_available()
    print(f"{'✓' if cuda_available else '✗'} CUDA available: {cuda_available}")

    if not cuda_available:
        print("\n❌ CUDA is not available. Check:")
        print("   1. NVIDIA driver installed on Windows (577.xx+)")
        print("   2. WSL CUDA toolkit installed")
        print("   3. PyTorch installed with cu128")
        sys.exit(1)

    # CUDA version
    print(f"✓ CUDA version: {torch.version.cuda}")

    # Device info
    print(f"✓ Device count: {torch.cuda.device_count()}")
    print(f"✓ Device name: {torch.cuda.get_device_name(0)}")

    # Architecture check (critical for RTX 5060)
    cap = torch.cuda.get_device_capability(0)
    print(f"✓ Compute capability: {cap[0]}.{cap[1]} (sm_{cap[0]}{cap[1]})")

    if cap[0] == 12 and cap[1] == 0:
        print("  ✓ Blackwell architecture (RTX 5060) detected!")
    else:
        print(f"  ⚠ Warning: Expected sm_120, got sm_{cap[0]}{cap[1]}")

    # Memory
    mem_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f"✓ GPU Memory: {mem_gb:.2f} GB")

    # Quick test
    print("\nRunning quick tensor test...")
    try:
        x = torch.randn(1000, 1000, device='cuda')
        y = torch.randn(1000, 1000, device='cuda')
        z = torch.matmul(x, y)
        print("✓ GPU computation successful!")

        # Cleanup
        del x, y, z
        torch.cuda.empty_cache()
    except Exception as e:
        print(f"✗ GPU computation failed: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✓ All checks passed! RTX 5060 is ready for fine-tuning")
    print("=" * 60)

if __name__ == "__main__":
    verify_gpu()
```

Run with:
```bash
python3 verify_rtx5060.py
```

## References

- NVIDIA RTX 5060 Specifications: https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5060/
- CUDA WSL Guide: https://docs.nvidia.com/cuda/wsl-user-guide/
- PyTorch Installation: https://pytorch.org/get-started/locally/
- CUDA 12.8 Download: https://developer.nvidia.com/cuda-downloads

## Next Steps After Setup

Once verified, proceed to:
1. `00-first-time-beginner/` - Start with Qwen3 0.6B tutorial
2. `01-unsloth/` - Try fast fine-tuning with your 16GB VRAM
3. `05-examples/` - Build real projects with RTX 5060 power

Your RTX 5060 with 16GB VRAM is excellent for fine-tuning up to 7B-13B models with 4-bit quantization!
