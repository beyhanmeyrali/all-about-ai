"""
05 - Voice Assistant with RAG Integration
Complete voice assistant combining VAD, Whisper, RAG Agent, and TTS

This is the full voice GPT implementation that:
1. Listens continuously using Silero VAD
2. Transcribes speech using Whisper
3. Answers questions using RAG Agent with knowledge base
4. Speaks responses using TTS
"""

import os
import torch
import whisper
import sounddevice as sd
import numpy as np
import time
from collections import deque
import threading
import pyttsx3
import requests
from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool
from qdrant_client import QdrantClient
from typing import Optional
from queue import Queue

# Disable OpenAI requirement
os.environ["OPENAI_API_KEY"] = "sk-dummy"

# Configuration
SAMPLE_RATE = 16000
CHUNK_SIZE = 512
VAD_THRESHOLD = 0.5
MIN_SPEECH_DURATION_MS = 250
MIN_SILENCE_DURATION_MS = 500
PRE_SPEECH_PAD_MS = 300

# RAG Configuration
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "qwen3-embedding:0.6b"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_API_KEY = "qdrant_pass"
COLLECTION_NAME = "ai_agents_knowledge"

# Wake word (optional - for future implementation)
WAKE_WORD = "assistant"


def get_embedding(text: str):
    """Generate embedding for the query using Ollama."""
    try:
        response = requests.post(OLLAMA_EMBED_URL, json={"model": EMBED_MODEL, "prompt": text})
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        print(f"⚠️  Error getting embedding: {e}")
        return []


class KnowledgeBaseTool(BaseTool):
    """Tool to search the knowledge base"""
    name: str = "Knowledge Base Search"
    description: str = "Search the internal knowledge base for information about AI Agents, RAG, embeddings, and related topics."

    def _run(self, query: str) -> str:
        try:
            # Connect to Qdrant
            client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, api_key=QDRANT_API_KEY, https=False)

            # Generate embedding
            query_vector = get_embedding(query)
            if not query_vector:
                return "Error: Could not generate embedding for query."

            # Search Qdrant
            results = client.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_vector,
                limit=3
            )

            if not results:
                return "No relevant information found in the knowledge base."

            # Format results
            context_parts = []
            for hit in results:
                source = hit.payload.get('source', 'Unknown')
                content = hit.payload.get('content', '')
                context_parts.append(f"Source: {source}\n{content}")

            return "\n\n".join(context_parts)

        except Exception as e:
            return f"Error: {str(e)}. Knowledge base unavailable."


class VoiceAssistant:
    """
    Complete voice assistant with RAG integration
    """

    def __init__(self, whisper_model_size: str = "base", tts_voice_index: int = 0):
        """
        Initialize voice assistant

        Args:
            whisper_model_size: Whisper model size (tiny, base, small, medium, large)
            tts_voice_index: TTS voice index (0 = default)
        """
        print("🤖 Initializing Voice Assistant...")
        print("=" * 60)

        # Load Silero VAD
        print("📥 Loading Silero VAD...")
        self.vad_model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False
        )
        (_, _, _, self.VADIterator, _) = utils
        self.vad_iterator = self.VADIterator(self.vad_model)
        print("✅ VAD loaded")

        # Load Whisper
        print(f"📥 Loading Whisper '{whisper_model_size}' model...")
        self.whisper_model = whisper.load_model(whisper_model_size)
        print("✅ Whisper loaded")

        # Initialize TTS
        print("📥 Initializing TTS...")
        self.tts_engine = pyttsx3.init()
        voices = self.tts_engine.getProperty('voices')
        if tts_voice_index < len(voices):
            self.tts_engine.setProperty('voice', voices[tts_voice_index].id)
        self.tts_engine.setProperty('rate', 175)
        self.tts_engine.setProperty('volume', 0.9)
        print("✅ TTS initialized")

        # Initialize RAG Agent
        print("📥 Initializing RAG Agent...")
        self.llm = LLM(
            model="ollama/qwen3:8b",
            base_url="http://127.0.0.1:11434"
        )

        self.knowledge_agent = Agent(
            role='AI Assistant',
            goal='Answer user questions accurately using the knowledge base when needed',
            backstory="You are a helpful AI assistant with access to a knowledge base about AI agents, RAG, and related topics. Keep your answers concise and clear.",
            verbose=False,
            tools=[KnowledgeBaseTool()],
            llm=self.llm
        )
        print("✅ RAG Agent initialized")

        # Audio buffers
        self.audio_buffer = deque(maxlen=int(SAMPLE_RATE * 30))
        self.recording_buffer = []
        self.is_recording = False
        self.silence_start = None

        # Threading
        self.running = False
        self.processing_lock = threading.Lock()
        self.tts_queue = Queue()
        self.audio_stream = None

        print("=" * 60)
        print("✅ Voice Assistant Ready!")
        print()

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
            print("\n🟢 Listening...")
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
        """Finish recording and process"""
        self.is_recording = False
        self.silence_start = None

        # Check minimum duration
        duration = len(self.recording_buffer) / SAMPLE_RATE
        if duration < MIN_SPEECH_DURATION_MS / 1000:
            return

        # Convert to numpy array
        audio = np.array(self.recording_buffer, dtype=np.float32)

        # Process in separate thread
        threading.Thread(
            target=self._process_query,
            args=(audio,),
            daemon=True
        ).start()

    def _process_query(self, audio: np.ndarray):
        """Process user query: transcribe -> answer -> speak"""
        with self.processing_lock:
            try:
                # 1. Transcribe
                print("🔄 Transcribing...")
                result = self.whisper_model.transcribe(
                    audio,
                    language="en",  # Force English language
                    fp16=torch.cuda.is_available()
                )

                query = result["text"].strip()
                if not query:
                    return

                print(f"\n💬 You: {query}")

                # 2. Get answer from RAG agent
                print("🤔 Thinking...")

                task = Task(
                    description=f"Answer this question: {query}",
                    expected_output="A clear, concise answer to the user's question.",
                    agent=self.knowledge_agent
                )

                crew = Crew(
                    agents=[self.knowledge_agent],
                    tasks=[task],
                    verbose=False
                )

                answer_result = crew.kickoff()
                answer = str(answer_result)

                print(f"\n🤖 Assistant: {answer}\n")

                # 3. Speak the answer
                print("🔊 Speaking...")
                self.speak(answer)

                print("=" * 60)
                print("Ready for next question...\n")

            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                print(f"\n❌ {error_msg}\n")
                self.speak(error_msg)

    def speak(self, text: str):
        """Queue text to be spoken in main thread"""
        self.tts_queue.put(text)

    def _process_tts_queue(self):
        """Process TTS queue continuously (must be called from main thread)"""
        from queue import Empty
        
        while self.running:  # Keep checking as long as assistant is running
            try:
                # Wait for messages with a reasonable timeout
                text = self.tts_queue.get(timeout=0.1)
                
                if not self.running:  # Check if we should exit
                    break
                    
                print(f"[DEBUG] Speaking: {text[:60]}...")

                # Pause audio input stream during TTS to avoid feedback/conflicts
                stream_was_active = False
                if self.audio_stream is not None and not self.audio_stream.stopped:
                    print("[DEBUG] Pausing audio input...")
                    self.audio_stream.stop()
                    stream_was_active = True
                    time.sleep(0.1)  # Give stream time to fully stop

                try:
                    # WINDOWS FIX: Must reinitialize engine for each speech
                    # Reusing the same engine only speaks the first message on Windows
                    tts = pyttsx3.init('sapi5')  # Explicit driver for Windows
                    tts.setProperty('rate', 175)
                    tts.setProperty('volume', 1.0)
                    
                    # Set voice if available
                    voices = tts.getProperty('voices')
                    if voices and len(voices) > 0:
                        tts.setProperty('voice', voices[0].id)
                    
                    tts.say(text)
                    tts.runAndWait()
                    
                    print("[DEBUG] TTS speech completed")
                    
                    # Clean up
                    del tts
                    
                    # Give audio output time to fully complete
                    time.sleep(0.3)
                    
                except Exception as e:
                    print(f"⚠️  TTS playback error: {e}")
                    import traceback
                    traceback.print_exc()

                # Resume audio input stream
                if stream_was_active and self.audio_stream is not None:
                    print("[DEBUG] Resuming audio input...")
                    time.sleep(0.1)  # Brief pause before resuming
                    self.audio_stream.start()

                self.tts_queue.task_done()
                
            except Empty:
                # Queue is empty, keep looping to check for new messages
                continue
            except Exception as e:
                print(f"⚠️  TTS queue processing error: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(0.5)  # Brief pause before retrying

    def start(self):
        """Start the voice assistant"""
        print("\n🎤 Voice Assistant Started")
        print("=" * 60)
        print("Speak into your microphone to ask questions...")
        print("The assistant will:")
        print("  1. Listen for your voice")
        print("  2. Transcribe your question")
        print("  3. Search the knowledge base")
        print("  4. Speak the answer")
        print("\nPress Ctrl+C to stop.")
        print("=" * 60 + "\n")

        # Greeting
        greeting = "Hello! I'm your AI voice assistant. How can I help you today?"
        print(f"🤖 {greeting}\n")
        self.speak(greeting)
        self._process_tts_queue()  # Process greeting TTS

        self.running = True

        try:
            self.audio_stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype='float32',
                blocksize=CHUNK_SIZE,
                callback=self.audio_callback
            )
            with self.audio_stream:
                while self.running:
                    self._process_tts_queue()  # Process TTS in main thread
                    time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping Voice Assistant...")
            goodbye = "Goodbye! Have a great day!"
            print(f"🤖 {goodbye}")
            self.speak(goodbye)
            self._process_tts_queue()  # Process goodbye TTS
            self.running = False
        except Exception as e:
            print(f"\n❌ Error: {e}")
            self.running = False

    def stop(self):
        """Stop the voice assistant"""
        self.running = False


def main():
    """Main function"""
    print("\n🎙️  Voice Assistant with RAG\n")

    # Check if Qdrant is running
    try:
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, api_key=QDRANT_API_KEY, https=False)
        collections = client.get_collections()
        print(f"✅ Qdrant is running ({len(collections.collections)} collections)")
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to Qdrant: {e}")
        print("   The assistant will work but knowledge base search will be unavailable.")
        print("   Start Qdrant with: docker compose up -d")
        response = input("\n   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return

    print()

    # Create and start assistant
    assistant = VoiceAssistant(
        whisper_model_size="base",
        tts_voice_index=0
    )

    assistant.start()


if __name__ == "__main__":
    main()
