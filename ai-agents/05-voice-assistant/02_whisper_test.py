"""
02 - Whisper STT Test
Test Speech-to-Text using OpenAI Whisper
"""

import whisper
import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import os

# Configuration
SAMPLE_RATE = 16000  # Whisper works best with 16kHz
DURATION = 5  # seconds to record
MODEL_SIZE = "base"  # tiny, base, small, medium, large

def load_whisper_model(model_size: str = MODEL_SIZE):
    """Load Whisper model"""
    print(f"📥 Loading Whisper '{model_size}' model...")
    model = whisper.load_model(model_size)
    print(f"✅ Model loaded: {model_size}")
    return model

def record_audio(duration: int = DURATION, sample_rate: int = SAMPLE_RATE):
    """Record audio from microphone"""
    print(f"\n🎤 Recording for {duration} seconds...")
    print("Speak now!")
    
    # Record audio
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32'
    )
    sd.wait()  # Wait until recording is finished
    
    print("✅ Recording complete!")
    return audio.flatten()

def transcribe_audio(model, audio: np.ndarray, sample_rate: int = SAMPLE_RATE):
    """Transcribe audio using Whisper"""
    print("\n🔄 Transcribing...")
    
    # Whisper expects audio as float32 numpy array
    result = model.transcribe(
        audio,
        language="en",  # or "tr" for Turkish, None for auto-detect
        fp16=False  # Set to True if you have CUDA GPU
    )
    
    return result

def test_whisper_realtime():
    """Test Whisper with real-time recording"""
    print("🎙️  Whisper STT Real-time Test")
    print("=" * 50)
    
    # Load model
    model = load_whisper_model()
    
    while True:
        print("\n" + "=" * 50)
        choice = input("Press ENTER to record (or 'q' to quit): ")
        
        if choice.lower() == 'q':
            break
        
        # Record
        audio = record_audio()
        
        # Transcribe
        result = transcribe_audio(model, audio)
        
        # Display results
        print("\n📝 Transcription:")
        print("-" * 50)
        print(result["text"])
        print("-" * 50)
        
        # Show detected language
        if "language" in result:
            print(f"🌍 Detected language: {result['language']}")

def test_whisper_file(audio_path: str):
    """Test Whisper on an audio file"""
    print(f"📁 Testing Whisper on file: {audio_path}")
    
    # Load model
    model = load_whisper_model()
    
    # Transcribe file directly
    result = model.transcribe(audio_path)
    
    print("\n📝 Transcription:")
    print("-" * 50)
    print(result["text"])
    print("-" * 50)
    
    if "language" in result:
        print(f"🌍 Detected language: {result['language']}")

if __name__ == "__main__":
    print("\n🗣️  Whisper STT Component Test\n")
    
    # Test real-time transcription
    test_whisper_realtime()
    
    # Uncomment to test on a file:
    # test_whisper_file("path/to/your/audio.wav")
