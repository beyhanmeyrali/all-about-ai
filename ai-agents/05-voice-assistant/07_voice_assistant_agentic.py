"""
07 - Voice-Controlled Home Automation with Web Dashboard
Based on 06 voice assistant + home automation tools + web UI

Features:
- Voice control with proper turn-taking (no feedback loop)
- Home automation tools (AC, TV, Door)
- Real-time web dashboard
- Tool calling with Ollama
"""

import os
import torch
import whisper
import sounddevice as sd
import numpy as np
import time
import threading
import pyttsx3
import requests
import json
from collections import deque
from queue import Queue, Empty
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio

# Disable OpenAI requirement
os.environ["OPENAI_API_KEY"] = "sk-dummy"

# Audio Configuration
SAMPLE_RATE = 16000
CHUNK_SIZE = 512

# --- Global State for Home Devices ---
class HomeState:
    """Manages state of smart home devices"""
    def __init__(self):
        self.devices = {
            "ac": {"power": False, "temperature": 24},
            "tv": {"power": False},
            "door": {"locked": True}
        }

    def to_dict(self):
        return self.devices.copy()

state = HomeState()

# --- Home Automation Tools ---
class HomeAutomationTools:

    @staticmethod
    def turn_on_ac():
        """Turns on the Air Conditioner."""
        state.devices["ac"]["power"] = True
        return "AC turned ON."

    @staticmethod
    def turn_off_ac():
        """Turns off the Air Conditioner."""
        state.devices["ac"]["power"] = False
        return "AC turned OFF."

    @staticmethod
    def set_ac_temperature(temp: int):
        """Sets the AC temperature. Input must be an integer."""
        try:
            temp = int(temp)
            state.devices["ac"]["temperature"] = temp
            state.devices["ac"]["power"] = True  # Auto turn on
            return f"AC temperature set to {temp}°C."
        except:
            return "Error: Temperature must be a number."

    @staticmethod
    def turn_on_tv():
        """Turns on the TV."""
        state.devices["tv"]["power"] = True
        return "TV turned ON."

    @staticmethod
    def turn_off_tv():
        """Turns off the TV."""
        state.devices["tv"]["power"] = False
        return "TV turned OFF."

    @staticmethod
    def lock_door():
        """Locks the main door."""
        state.devices["door"]["locked"] = True
        return "Main door LOCKED."

    @staticmethod
    def unlock_door():
        """Unlocks the main door."""
        state.devices["door"]["locked"] = False
        return "Main door UNLOCKED."

# --- Simple Agent for Tool Calling ---
class SimpleAgent:
    def __init__(self, model_name="ministral-3:3b"):
        self.model_name = model_name
        self.api_url = "http://localhost:11434/api/chat"
        self.tools = {
            "turn_on_ac": HomeAutomationTools.turn_on_ac,
            "turn_off_ac": HomeAutomationTools.turn_off_ac,
            "set_ac_temperature": HomeAutomationTools.set_ac_temperature,
            "turn_on_tv": HomeAutomationTools.turn_on_tv,
            "turn_off_tv": HomeAutomationTools.turn_off_tv,
            "lock_door": HomeAutomationTools.lock_door,
            "unlock_door": HomeAutomationTools.unlock_door
        }

    def chat(self, user_input: str) -> str:
        """Processes user input and calls tools if needed"""
        system_prompt = (
            "You are a Home Automation Assistant. You control AC, TV, and Door.\n\n"
            "Tools:\n"
            "- turn_on_ac(), turn_off_ac()\n"
            "- set_ac_temperature(temp: int) - requires temperature argument\n"
            "- turn_on_tv(), turn_off_tv()\n"
            "- lock_door(), unlock_door()\n\n"
            "WHEN TO EXECUTE TOOLS (output JSON):\n"
            "- User mentions AC/air conditioner/cooling → use AC tools\n"
            "- User mentions TV/television → use TV tools\n"
            "- User mentions door/lock → use door tools\n"
            "- Keywords: turn on/off, open/close, lock/unlock, set temperature, everything, all\n\n"
            "WHEN TO RESPOND WITH TEXT (NO tools):\n"
            "- Greetings: hello, hi, hey\n"
            "- Goodbye: bye, goodbye, see you\n"
            "- Unrelated: weather, time, how are you, random chat\n\n"
            "OUTPUT FORMAT EXAMPLES:\n"
            "- No args: "
            '{"tool": "turn_on_ac"}\n'
            "- With args: "
            '{"tool": "set_ac_temperature", "args": {"temp": 22}}\n'
            "- Multiple: "
            '[{"tool": "turn_on_tv"}, {"tool": "turn_on_ac"}]\n'
            "- Text response: "
            '"Goodbye!" or "I only control AC, TV, and Door."\n'
            "- NO markdown, NO code blocks.\n"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        try:
            response = requests.post(self.api_url, json={
                "model": self.model_name,
                "messages": messages,
                "stream": False
            })
            response.raise_for_status()
            result = response.json()["message"]["content"]

            # Try to parse as tool call
            try:
                clean_result = result.strip()
                if clean_result.startswith("```json"):
                    clean_result = clean_result[7:-3]
                elif clean_result.startswith("```"):
                    clean_result = clean_result[3:-3]

                clean_result = clean_result.strip()

                # Check if we have multiple JSON objects on separate lines
                lines = [line.strip() for line in clean_result.split('\n') if line.strip()]
                if len(lines) > 1 and all(line.startswith('{') and line.endswith('}') for line in lines):
                    # Multiple JSON objects - parse each one
                    parsed = []
                    for line in lines:
                        try:
                            parsed.append(json.loads(line))
                        except:
                            pass
                # Try to find JSON (array or object)
                elif ("[" in clean_result or "{" in clean_result) and ("]" in clean_result or "}" in clean_result):
                    # Find the JSON content
                    if "[" in clean_result:
                        start = clean_result.find("[")
                        end = clean_result.rfind("]") + 1
                    else:
                        start = clean_result.find("{")
                        end = clean_result.rfind("}") + 1

                    json_str = clean_result[start:end]
                    parsed = json.loads(json_str)
                else:
                    return result

                # Handle array of tool calls
                if isinstance(parsed, list):
                    results = []
                    for action in parsed:
                        tool_name = action.get("tool")
                        args = action.get("args", {})

                        if tool_name in self.tools:
                            print(f"🤖 Tool Executed: {tool_name} {args}")
                            tool_func = self.tools[tool_name]
                            if args:
                                tool_result = tool_func(**args)
                            else:
                                tool_result = tool_func()
                            results.append(tool_result)

                    return " ".join(results) if results else result

                # Handle single tool call
                else:
                    tool_name = parsed.get("tool")
                    args = parsed.get("args", {})

                    if tool_name in self.tools:
                        print(f"🤖 Tool Executed: {tool_name} {args}")
                        tool_func = self.tools[tool_name]
                        if args:
                            tool_result = tool_func(**args)
                        else:
                            tool_result = tool_func()
                        return f"{tool_result}"
            except:
                pass

            return result

        except Exception as e:
            return f"Error: {e}"

# --- Voice Assistant (from 06 with proper turn-taking) ---
class VoiceAssistantAgentic:
    def __init__(self):
        # Audio Config
        self.SAMPLE_RATE = SAMPLE_RATE
        self.CHUNK_SIZE = CHUNK_SIZE

        # Load Whisper (Speech-to-Text)
        print("📥 Loading Whisper...")
        self.whisper_model = whisper.load_model("base")

        # Load VAD (Voice Activity Detection)
        print("📥 Loading VAD...")
        self.vad_model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False
        )
        (_, _, _, self.VADIterator, _) = utils
        self.vad_iterator = self.VADIterator(self.vad_model)

        # Agent for tool calling
        self.agent = SimpleAgent(model_name="ministral-3:3b")

        # TTS Queue
        self.tts_queue = Queue()

        # State
        self.running = False
        self.audio_buffer = deque(maxlen=int(self.SAMPLE_RATE * 30))
        self.recording_buffer = []
        self.is_recording = False
        self.silence_start = None
        self.processing_lock = threading.Lock()
        self.audio_stream = None

    def start(self):
        """Start the voice assistant"""
        self.running = True

        # Start threads
        threading.Thread(target=self._audio_loop, daemon=True).start()
        threading.Thread(target=self._tts_loop, daemon=True).start()

        # Greeting
        greeting = "Home Automation System Online. I can control your AC, TV, and Door."
        print(f"🤖 {greeting}")
        self.speak(greeting)

    def _audio_loop(self):
        """Continuous loop capturing microphone audio"""
        self.audio_stream = sd.InputStream(
            samplerate=self.SAMPLE_RATE,
            channels=1,
            blocksize=self.CHUNK_SIZE,
            callback=self._audio_callback
        )
        with self.audio_stream:
            while self.running:
                time.sleep(0.1)

    def _audio_callback(self, indata, frames, time_info, status):
        """Called by sounddevice whenever new audio data is available"""
        audio_chunk = indata[:, 0].astype(np.float32)
        self.audio_buffer.extend(audio_chunk)

        # Check if user is speaking using VAD
        speech_dict = self.vad_iterator(audio_chunk, return_seconds=False)
        if speech_dict:
            if 'start' in speech_dict:
                if not self.is_recording:
                    print("🎤 Listening...")
                    self.is_recording = True
                    self.recording_buffer = []
                    # Keep a bit of audio before trigger
                    pad = list(self.audio_buffer)[-int(self.SAMPLE_RATE*0.3):]
                    self.recording_buffer.extend(pad)
                self.silence_start = None
            if 'end' in speech_dict:
                if self.is_recording:
                    self.silence_start = time.time()

        if self.is_recording:
            self.recording_buffer.extend(audio_chunk)
            # Stop recording after 0.5s of silence
            if self.silence_start and (time.time() - self.silence_start > 0.5):
                self.is_recording = False
                self.silence_start = None
                audio_data = np.array(self.recording_buffer, dtype=np.float32)
                threading.Thread(target=self._process_audio, args=(audio_data,), daemon=True).start()

    def _process_audio(self, audio):
        """Process recorded audio"""
        with self.processing_lock:
            try:
                # 1. Transcribe
                print("📝 Transcribing...")
                result = self.whisper_model.transcribe(
                    audio,
                    language="en",  # Force English language
                    fp16=torch.cuda.is_available()
                )
                text = result["text"].strip()
                if not text or len(text) < 2:
                    print("🔇 No speech detected\n")
                    return

                print(f"\n💬 You: {text}")

                # 2. Agent Decision
                print("🤖 Processing request with Ollama...")
                response = self.agent.chat(text)

                print(f"🤖 Assistant: {response}\n")

                # 3. Speak
                print("🔊 Speaking...")
                self.speak(response)

                print("=" * 60)
                print("Ready for next command...\n")

            except Exception as e:
                print(f"❌ Error: {e}")

    def speak(self, text):
        """Queue text for TTS"""
        self.tts_queue.put(text)

    def _tts_loop(self):
        """TTS thread with proper audio pause/resume (from 06)"""
        while self.running:
            try:
                text = self.tts_queue.get(timeout=0.1)

                # PAUSE audio input during TTS to avoid feedback
                stream_was_active = False
                if self.audio_stream is not None and self.audio_stream.active:
                    print("[DEBUG] Pausing audio input...")
                    self.audio_stream.stop()
                    stream_was_active = True
                    time.sleep(0.1)

                # Speak
                engine = pyttsx3.init()
                engine.setProperty('rate', 175)
                engine.say(text)
                engine.runAndWait()
                del engine

                # Give audio output time to complete
                time.sleep(0.3)

                # RESUME audio input
                if stream_was_active and self.audio_stream is not None:
                    print("[DEBUG] Resuming audio input...")
                    time.sleep(0.1)
                    self.audio_stream.start()

                self.tts_queue.task_done()
            except Empty:
                continue
            except Exception as e:
                print(f"TTS Error: {e}")

# --- FastAPI Web Dashboard ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get_home():
    """Serve the dashboard HTML"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(current_dir, 'static', 'dashboard.html')
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "dashboard.html not found"}

@app.get("/api/devices")
async def get_devices():
    """Get current device states"""
    return JSONResponse(state.to_dict())

# Global voice assistant instance
voice_assistant = None

@app.on_event("startup")
async def startup_event():
    """Start voice assistant on server startup"""
    global voice_assistant
    voice_assistant = VoiceAssistantAgentic()
    voice_assistant.start()

if __name__ == "__main__":
    print("🚀 Starting Voice-Controlled Home Automation...")
    print("📱 Web Dashboard: http://localhost:8000")
    print("🎤 Voice control active")
    print("ℹ️  Press Ctrl+C to stop.\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")
