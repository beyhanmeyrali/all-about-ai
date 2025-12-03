"""
00 - Preload Models
Pre-load Silero VAD and Whisper models to local models folder before running the voice assistant
"""

import torch
import whisper
import sys
import os

# Models directory
MODELS_DIR = "./models"
os.makedirs(MODELS_DIR, exist_ok=True)

def preload_silero_vad():
    """Pre-load Silero VAD model"""
    print("📥 Loading Silero VAD model...")
    try:
        # Set torch hub directory to local models folder
        vad_dir = os.path.join(MODELS_DIR, 'silero_vad')
        os.makedirs(vad_dir, exist_ok=True)

        # Set the torch hub directory
        old_hub_dir = torch.hub.get_dir()
        torch.hub.set_dir(vad_dir)

        model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False
        )

        # Restore original hub directory
        torch.hub.set_dir(old_hub_dir)

        print(f"✅ Silero VAD model loaded and saved to {vad_dir}")
        return True
    except Exception as e:
        print(f"❌ Error loading VAD model: {e}")
        return False

def preload_whisper(model_size="base"):
    """Pre-load Whisper model"""
    print(f"📥 Loading Whisper '{model_size}' model...")
    try:
        whisper_dir = os.path.join(MODELS_DIR, 'whisper')
        os.makedirs(whisper_dir, exist_ok=True)

        model = whisper.load_model(model_size, download_root=whisper_dir)
        print(f"✅ Whisper '{model_size}' model loaded and saved to {whisper_dir}")
        return True
    except Exception as e:
        print(f"❌ Error loading Whisper model: {e}")
        return False

if __name__ == "__main__":
    print("\n🚀 Pre-loading Models for Voice Assistant\n")
    print("=" * 60)

    # Load VAD
    vad_success = preload_silero_vad()
    print()

    # Load Whisper
    whisper_success = preload_whisper("base")
    print()

    print("=" * 60)
    if vad_success and whisper_success:
        print("✅ All models loaded successfully!")
        print("You can now run the voice assistant scripts.")
        sys.exit(0)
    else:
        print("⚠️  Some models failed to load. Check errors above.")
        sys.exit(1)
