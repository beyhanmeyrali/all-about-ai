#!/usr/bin/env python3
"""
RTX 5060 PyTorch Setup Verification Script
Verifies CUDA 12.8+ support for Blackwell architecture (sm_120)
"""
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
        print("\nRun these commands:")
        print("   # On Windows PowerShell:")
        print("   nvidia-smi")
        print("\n   # In WSL:")
        print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128")
        sys.exit(1)

    # CUDA version
    cuda_version = torch.version.cuda
    print(f"✓ CUDA version: {cuda_version}")

    if cuda_version and float(cuda_version.split('.')[0] + '.' + cuda_version.split('.')[1]) < 12.8:
        print(f"⚠ Warning: CUDA {cuda_version} may not support RTX 5060 (sm_120)")
        print(f"   Recommended: CUDA 12.8+")

    # Device info
    device_count = torch.cuda.device_count()
    print(f"✓ Device count: {device_count}")

    if device_count == 0:
        print("❌ No CUDA devices found")
        sys.exit(1)

    device_name = torch.cuda.get_device_name(0)
    print(f"✓ Device name: {device_name}")

    # Architecture check (critical for RTX 5060)
    cap = torch.cuda.get_device_capability(0)
    print(f"✓ Compute capability: {cap[0]}.{cap[1]} (sm_{cap[0]}{cap[1]})")

    if cap[0] == 12 and cap[1] == 0:
        print("  ✓ Blackwell architecture (RTX 5060) detected!")
    elif cap[0] >= 8:
        print(f"  ✓ Modern GPU architecture detected")
    else:
        print(f"  ⚠ Warning: Expected newer architecture")

    # Memory
    mem_bytes = torch.cuda.get_device_properties(0).total_memory
    mem_gb = mem_bytes / 1e9
    print(f"✓ GPU Memory: {mem_gb:.2f} GB")

    # Additional properties
    props = torch.cuda.get_device_properties(0)
    print(f"✓ Multiprocessors: {props.multi_processor_count}")

    # Quick test
    print("\nRunning quick tensor test...")
    try:
        x = torch.randn(1000, 1000, device='cuda')
        y = torch.randn(1000, 1000, device='cuda')
        z = torch.matmul(x, y)
        print("✓ GPU computation successful!")

        # Test memory allocation
        allocated = torch.cuda.memory_allocated(0) / 1e9
        reserved = torch.cuda.memory_reserved(0) / 1e9
        print(f"✓ Memory allocated: {allocated:.3f} GB")
        print(f"✓ Memory reserved: {reserved:.3f} GB")

        # Cleanup
        del x, y, z
        torch.cuda.empty_cache()
        print("✓ Memory cleanup successful!")

    except Exception as e:
        print(f"✗ GPU computation failed: {e}")
        sys.exit(1)

    # Recommendations based on memory
    print("\n" + "=" * 60)
    print("Recommended Fine-Tuning Configurations for Your GPU:")
    print("=" * 60)

    if mem_gb >= 16:
        print("\n✓ 16GB VRAM - Excellent for fine-tuning!")
        print("\nRecommended models:")
        print("  • 0.6B-2B models: Full precision, large batch sizes")
        print("  • 7B models: 4-bit quantization, batch_size=4-8")
        print("  • 13B models: 4-bit quantization, batch_size=2-4")
        print("  • 30B+ models: 4-bit quantization with CPU offload")

        print("\nSample config for 7B models:")
        print("""
  config = {
      "per_device_train_batch_size": 4,
      "gradient_accumulation_steps": 4,
      "max_seq_length": 2048,
      "bits": 4,
      "double_quant": True,
  }
        """)

    elif mem_gb >= 7.5:
        print(f"\n✓ {mem_gb:.1f}GB VRAM - Excellent for 8GB RTX 5060!")
        print("\nRecommended models:")
        print("  • 0.6B-2B models: Full precision, batch_size=8")
        print("  • 7B models: 4-bit quantization, batch_size=2")
        print("  • 13B models: 4-bit + aggressive optimization")

        print("\nSample config for 7B models (optimized for 8GB):")
        print("""
  config = {
      "per_device_train_batch_size": 2,
      "gradient_accumulation_steps": 8,
      "max_seq_length": 1024,
      "bits": 4,
      "double_quant": True,
  }
        """)

    else:
        print(f"\n⚠ {mem_gb:.0f}GB VRAM - Limited to small models")
        print("\nRecommended models:")
        print("  • 0.6B-1.7B models with 4-bit quantization")

    print("\n" + "=" * 60)
    print("✓ All checks passed! GPU is ready for fine-tuning")
    print("=" * 60)

    print("\nNext steps:")
    print("  1. cd /workspace/all-about-ai/fine-tuning/00-first-time-beginner")
    print("  2. Follow the Qwen3 tutorial")
    print("  3. Start with small models and scale up")

if __name__ == "__main__":
    try:
        verify_gpu()
    except KeyboardInterrupt:
        print("\n\nVerification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
