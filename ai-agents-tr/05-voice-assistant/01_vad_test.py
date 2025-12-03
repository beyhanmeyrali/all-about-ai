"""
01 - Silero VAD Test
Test Voice Activity Detection using Silero VAD
"""

import torch
import numpy as np
import sounddevice as sd
import time

# Silero VAD Model
# Download and load the model
model, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    force_reload=False,
    onnx=False
)

(get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

# Configuration
SAMPLE_RATE = 16000  # Silero VAD requires 16kHz
CHUNK_SIZE = 512  # Silero VAD requires 512, 1024, or 1536 samples for 16kHz

def test_vad_realtime():
    """Test VAD with real-time microphone input"""
    print("🎤 Silero VAD Real-time Test")
    print("=" * 50)
    print("Speak into your microphone. Press Ctrl+C to stop.")
    print("=" * 50)
    
    vad_iterator = VADIterator(model)
    
    def audio_callback(indata, frames, time_info, status):
        if status:
            print(f"Status: {status}")
        
        # Convert to float32 and flatten
        audio_chunk = indata[:, 0].astype(np.float32)
        
        # Get VAD confidence
        speech_dict = vad_iterator(audio_chunk, return_seconds=False)
        
        if speech_dict:
            if 'start' in speech_dict:
                print("🟢 Speech START detected")
            if 'end' in speech_dict:
                print("🔴 Speech END detected")
    
    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype='float32',
            blocksize=CHUNK_SIZE,
            callback=audio_callback
        ):
            print("\n✅ Listening... (Ctrl+C to stop)\n")
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopped.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def test_vad_file(audio_path: str):
    """Test VAD on an audio file"""
    print(f"📁 Testing VAD on file: {audio_path}")
    
    # Read audio
    wav = read_audio(audio_path, sampling_rate=SAMPLE_RATE)
    
    # Get speech timestamps
    speech_timestamps = get_speech_timestamps(
        wav,
        model,
        sampling_rate=SAMPLE_RATE,
        threshold=0.5,
        min_speech_duration_ms=250,
        min_silence_duration_ms=100
    )
    
    print(f"\n✅ Found {len(speech_timestamps)} speech segments:")
    for i, ts in enumerate(speech_timestamps, 1):
        start_sec = ts['start'] / SAMPLE_RATE
        end_sec = ts['end'] / SAMPLE_RATE
        duration = end_sec - start_sec
        print(f"  Segment {i}: {start_sec:.2f}s - {end_sec:.2f}s (duration: {duration:.2f}s)")

if __name__ == "__main__":
    print("\n🔊 Silero VAD Component Test\n")
    
    # Test real-time VAD
    test_vad_realtime()
    
    # Uncomment to test on a file:
    # test_vad_file("path/to/your/audio.wav")
