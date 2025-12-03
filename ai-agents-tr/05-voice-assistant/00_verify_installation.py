"""
00 - Verify Installation
Verify all voice assistant components are installed correctly
"""

def verify_imports():
    """Verify all required packages can be imported"""
    print("🔍 Verifying Voice Assistant Dependencies")
    print("=" * 60)

    checks = []

    # Check PyTorch
    try:
        import torch
        version = torch.__version__
        cuda_available = torch.cuda.is_available()
        checks.append(("✅", f"PyTorch {version} (CUDA: {cuda_available})"))
    except Exception as e:
        checks.append(("❌", f"PyTorch - Error: {e}"))

    # Check Whisper
    try:
        import whisper
        checks.append(("✅", "OpenAI Whisper"))
    except Exception as e:
        checks.append(("❌", f"Whisper - Error: {e}"))

    # Check Silero VAD
    try:
        import torch
        # Test loading VAD model (this will download it first time)
        print("\n📥 Loading Silero VAD model (first time will download)...")
        model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False
        )
        checks.append(("✅", "Silero VAD (model loaded)"))
    except Exception as e:
        checks.append(("❌", f"Silero VAD - Error: {e}"))

    # Check pyttsx3
    try:
        import pyttsx3
        checks.append(("✅", "pyttsx3 TTS"))
    except Exception as e:
        checks.append(("❌", f"pyttsx3 - Error: {e}"))

    # Check audio libraries
    try:
        import sounddevice as sd
        checks.append(("✅", "sounddevice"))
    except Exception as e:
        checks.append(("❌", f"sounddevice - Error: {e}"))

    try:
        import soundfile as sf
        checks.append(("✅", "soundfile"))
    except Exception as e:
        checks.append(("❌", f"soundfile - Error: {e}"))

    # Check numpy and scipy
    try:
        import numpy as np
        checks.append(("✅", f"NumPy {np.__version__}"))
    except Exception as e:
        checks.append(("❌", f"NumPy - Error: {e}"))

    try:
        import scipy
        checks.append(("✅", f"SciPy {scipy.__version__}"))
    except Exception as e:
        checks.append(("❌", f"SciPy - Error: {e}"))

    # Print results
    print("\n📋 Installation Check Results:")
    print("-" * 60)
    for status, message in checks:
        print(f"  {status} {message}")
    print("-" * 60)

    # Summary
    passed = sum(1 for status, _ in checks if status == "✅")
    total = len(checks)

    print(f"\n✅ Passed: {passed}/{total}")

    if passed == total:
        print("\n🎉 All components installed successfully!")
        print("\n📝 Next Steps:")
        print("  1. Test individual components (requires microphone & speakers):")
        print("     - python 03_tts_test.py")
        print("     - python 02_whisper_test.py")
        print("     - python 01_vad_test.py")
        print("  2. Run integrated voice assistant:")
        print("     - python 04_voice_loop.py")
    else:
        print("\n⚠️  Some components failed. Please check the errors above.")

    return passed == total

if __name__ == "__main__":
    print("\n🎙️  Voice Assistant Installation Verification\n")
    verify_imports()
