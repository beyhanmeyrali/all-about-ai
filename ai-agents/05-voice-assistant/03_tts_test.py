"""
03 - TTS Test
Test Text-to-Speech using pyttsx3 (system TTS)
"""

import pyttsx3

def test_system_tts():
    """Test system TTS with pyttsx3"""
    print("🔊 System TTS Test")
    print("=" * 50)
    
    # Initialize TTS engine
    engine = pyttsx3.init()
    
    # Get available voices
    voices = engine.getProperty('voices')
    print(f"\n📋 Available voices: {len(voices)}")
    for i, voice in enumerate(voices):
        print(f"  {i}: {voice.name} ({voice.languages})")
    
    # Configure voice
    print("\n⚙️  Configuration:")
    
    # Set voice (0 = male, 1 = female usually)
    engine.setProperty('voice', voices[0].id)
    print(f"  Voice: {voices[0].name}")
    
    # Set speech rate (words per minute)
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate - 25)  # Slightly slower
    print(f"  Rate: {rate - 25} wpm")
    
    # Set volume (0.0 to 1.0)
    volume = engine.getProperty('volume')
    engine.setProperty('volume', 0.9)
    print(f"  Volume: 0.9")
    
    # Test phrases
    test_phrases = [
        "Hello! I am your AI voice assistant.",
        "I can help you with questions using my knowledge base.",
        "What would you like to know today?"
    ]
    
    print("\n🗣️  Speaking test phrases...")
    for i, phrase in enumerate(test_phrases, 1):
        print(f"\n  {i}. {phrase}")
        engine.say(phrase)
        engine.runAndWait()
    
    print("\n✅ TTS test complete!")

def speak_text(text: str, voice_index: int = 0, rate: int = 175):
    """
    Speak the given text
    
    Args:
        text: Text to speak
        voice_index: Index of voice to use (0 = default)
        rate: Speech rate in words per minute
    """
    engine = pyttsx3.init()
    
    voices = engine.getProperty('voices')
    if voice_index < len(voices):
        engine.setProperty('voice', voices[voice_index].id)
    
    engine.setProperty('rate', rate)
    engine.setProperty('volume', 0.9)
    
    engine.say(text)
    engine.runAndWait()

def interactive_tts():
    """Interactive TTS test"""
    print("\n🎤 Interactive TTS Test")
    print("=" * 50)
    print("Type text to hear it spoken (or 'q' to quit)")
    print("=" * 50)
    
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    
    # Let user choose voice
    print(f"\nAvailable voices:")
    for i, voice in enumerate(voices):
        print(f"  {i}: {voice.name}")
    
    voice_choice = input(f"\nChoose voice (0-{len(voices)-1}, default=0): ")
    voice_index = int(voice_choice) if voice_choice.isdigit() else 0
    
    engine.setProperty('voice', voices[voice_index].id)
    engine.setProperty('rate', 175)
    engine.setProperty('volume', 0.9)
    
    while True:
        text = input("\n💬 Enter text: ")
        
        if text.lower() == 'q':
            break
        
        if text.strip():
            print("🔊 Speaking...")
            engine.say(text)
            engine.runAndWait()

if __name__ == "__main__":
    print("\n🔊 TTS Component Test\n")
    
    # Run system TTS test
    test_system_tts()
    
    # Run interactive test
    print("\n")
    interactive_tts()
