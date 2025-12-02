"""
04 - Voice Loop (VAD + Whisper Integration)
Continuous voice listening using Silero VAD and Whisper STT

This script:
1. Listens continuously for voice activity using Silero VAD
2. Records audio when speech is detected
3. Transcribes the recording using Whisper
4. Displays the transcribed text
"""

import torch
import whisper
import sounddevice as sd
import numpy as np
import time
from collections import deque
import threading

# Configuration
SAMPLE_RATE = 16000  # Both VAD and Whisper use 16kHz
CHUNK_SIZE = 512     # VAD chunk size
VAD_THRESHOLD = 0.5  # Confidence threshold for speech detection
MIN_SPEECH_DURATION_MS = 250  # Minimum speech duration to consider
MIN_SILENCE_DURATION_MS = 500  # Silence duration to end recording
PRE_SPEECH_PAD_MS = 300  # Pad before speech starts
POST_SPEECH_PAD_MS = 300  # Pad after speech ends

class VoiceLoop:
    """
    Voice activity detection and transcription loop
    """

    def __init__(self, whisper_model_size: str = "base"):
        """
        Initialize voice loop

        Args:
            whisper_model_size: Whisper model size (tiny, base, small, medium, large)
        """
        print("🔧 Initializing Voice Loop...")

        # Load Silero VAD
        print("📥 Loading Silero VAD...")
        self.vad_model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False
        )
        (self.get_speech_timestamps, _, _, self.VADIterator, _) = utils
        self.vad_iterator = self.VADIterator(self.vad_model)
        print("✅ VAD loaded")

        # Load Whisper
        print(f"📥 Loading Whisper '{whisper_model_size}' model...")
        self.whisper_model = whisper.load_model(whisper_model_size)
        print("✅ Whisper loaded")

        # Audio buffer
        self.audio_buffer = deque(maxlen=int(SAMPLE_RATE * 30))  # 30 seconds max
        self.recording_buffer = []
        self.is_recording = False
        self.silence_start = None

        # Threading
        self.running = False
        self.audio_thread = None

        print("✅ Voice Loop initialized!\n")

    def audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream"""
        if status:
            print(f"⚠️  Audio status: {status}")

        # Convert to float32 and flatten
        audio_chunk = indata[:, 0].astype(np.float32)

        # Add to buffer
        self.audio_buffer.extend(audio_chunk)

        # Run VAD
        speech_dict = self.vad_iterator(audio_chunk, return_seconds=False)

        if speech_dict:
            if 'start' in speech_dict:
                self._on_speech_start()
            if 'end' in speech_dict:
                self._on_speech_end()

        # If recording, add to recording buffer
        if self.is_recording:
            self.recording_buffer.extend(audio_chunk)

            # Check for silence timeout
            if self.silence_start:
                silence_duration = time.time() - self.silence_start
                if silence_duration > MIN_SILENCE_DURATION_MS / 1000:
                    self._finish_recording()

    def _on_speech_start(self):
        """Handle speech start detection"""
        if not self.is_recording:
            print("\n🟢 Speech detected - Recording...")
            self.is_recording = True
            self.recording_buffer = []

            # Add pre-speech padding
            pad_samples = int(SAMPLE_RATE * PRE_SPEECH_PAD_MS / 1000)
            if len(self.audio_buffer) >= pad_samples:
                pre_pad = list(self.audio_buffer)[-pad_samples:]
                self.recording_buffer.extend(pre_pad)

        self.silence_start = None

    def _on_speech_end(self):
        """Handle speech end detection"""
        if self.is_recording:
            self.silence_start = time.time()

    def _finish_recording(self):
        """Finish recording and transcribe"""
        print("🔴 Speech ended - Processing...")
        self.is_recording = False
        self.silence_start = None

        # Check minimum duration
        duration = len(self.recording_buffer) / SAMPLE_RATE
        if duration < MIN_SPEECH_DURATION_MS / 1000:
            print(f"⚠️  Too short ({duration:.2f}s), ignoring...")
            return

        # Convert to numpy array
        audio = np.array(self.recording_buffer, dtype=np.float32)

        # Transcribe in a separate thread to avoid blocking audio
        threading.Thread(
            target=self._transcribe_audio,
            args=(audio,),
            daemon=True
        ).start()

    def _transcribe_audio(self, audio: np.ndarray):
        """Transcribe audio using Whisper"""
        try:
            print("🔄 Transcribing...")
            result = self.whisper_model.transcribe(
                audio,
                language=None,  # Auto-detect language
                fp16=torch.cuda.is_available()  # Use FP16 if GPU available
            )

            text = result["text"].strip()
            language = result.get("language", "unknown")

            if text:
                print("\n" + "=" * 60)
                print(f"📝 Transcription ({language}):")
                print(text)
                print("=" * 60 + "\n")
            else:
                print("⚠️  No speech detected in audio")

        except Exception as e:
            print(f"❌ Transcription error: {e}")

    def start(self):
        """Start the voice loop"""
        print("🎤 Starting Voice Loop")
        print("=" * 60)
        print("Speak into your microphone...")
        print("Press Ctrl+C to stop.")
        print("=" * 60 + "\n")

        self.running = True

        try:
            with sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype='float32',
                blocksize=CHUNK_SIZE,
                callback=self.audio_callback
            ):
                while self.running:
                    time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping Voice Loop...")
            self.running = False
        except Exception as e:
            print(f"\n❌ Error: {e}")
            self.running = False

    def stop(self):
        """Stop the voice loop"""
        self.running = False


def main():
    """Main function"""
    print("\n🎙️  Voice Loop - Continuous Listening\n")

    # Create voice loop
    voice_loop = VoiceLoop(whisper_model_size="base")

    # Start listening
    voice_loop.start()


if __name__ == "__main__":
    main()
