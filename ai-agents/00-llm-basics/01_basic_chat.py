#!/usr/bin/env python3
"""
Example 1: Basic Chat with Ollama (OOP Style)
==============================================

This is the SIMPLEST possible LLM interaction using Object-Oriented Programming.
Perfect for understanding both OOP and LLM fundamentals.

What you'll learn:
- How to structure AI code using classes (OOP pattern)
- How to make a basic API call to an LLM
- The request/response structure
- Why LLMs are stateless (no memory between calls)

OOP Benefits:
- Code is reusable (create multiple bots easily)
- Easier to maintain and extend
- Cleaner separation of concerns
- Industry-standard pattern

Author: Beyhan MEYRALI
"""

import requests
import json
from typing import Optional, List, Dict


# =============================================================================
# OOP PATTERN: LLM Bot Class
# =============================================================================

class OllamaBot:
    """
    A simple chatbot that communicates with Ollama LLM.

    This class encapsulates all the functionality needed to chat with an LLM.
    Each instance of this class represents one bot configuration.

    Example usage:
        bot = OllamaBot(model="qwen3:8b")
        response = bot.ask("What is 2+2?")
        print(response)
    """

    def __init__(self,
                 model: str = "qwen3:8b",
                 base_url: str = "http://localhost:11434",
                 timeout: int = 60):
        """
        Initialize the chatbot.

        Args:
            model: The Ollama model to use (default: qwen3:8b)
            base_url: Ollama API endpoint (default: http://localhost:11434)
            timeout: Request timeout in seconds (default: 60)

        Note: This is the CONSTRUCTOR - it runs when you create a new bot.
        """
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self.api_endpoint = f"{base_url}/api/chat"

        # Instance variable to store conversation history
        # Each bot instance has its own history!
        self.messages: List[Dict[str, str]] = []

        print(f"[OK] OllamaBot initialized")
        print(f"[OK] Model: {self.model}")
        print(f"[OK] Endpoint: {self.api_endpoint}")

    def ask_question(self, question: str, stream: bool = False) -> Optional[str]:
        """
        Send a single question to the LLM and get a response.

        This is the CORE method of the bot - it handles the HTTP communication.

        Args:
            question: The question to ask the LLM
            stream: If True, get streaming response (for future use)

        Returns:
            The LLM's response as a string, or None if error occurred

        How it works:
        1. Prepare the payload (JSON with your question)
        2. Send HTTP POST request to Ollama
        3. Parse the response
        4. Return the answer
        """

        # Step 1: Prepare the request payload
        # This is the JSON structure Ollama expects
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",  # Who is sending this message
                    "content": question  # The actual message content
                }
            ],
            "stream": stream  # Get complete response at once (not token-by-token)
        }

        # Step 2: Send POST request to Ollama
        print(f"\n[USER] {question}")
        print(f"[INFO] Sending to {self.model}...")

        try:
            response = requests.post(
                self.api_endpoint,
                json=payload,
                timeout=self.timeout
            )

            # Step 3: Check if request was successful
            if response.status_code == 200:
                # Parse JSON response
                response_data = response.json()

                # Extract the LLM's message from the response
                # Response structure: response['message']['content']
                llm_response = response_data['message']['content']

                print(f"[AI] {llm_response}")
                return llm_response
            else:
                error_msg = f"Error {response.status_code}: {response.text}"
                print(f"[ERROR] {error_msg}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Connection failed: {e}")
            print("[HINT] Make sure Ollama is running: ollama serve")
            return None

    def chat(self, user_message: str) -> Optional[str]:
        """
        Convenience method - same as ask_question() but shorter name.

        This is an ALIAS method for better developer experience.
        """
        return self.ask_question(user_message)

    def reset(self):
        """
        Reset the bot's conversation history.

        This clears the messages list, useful for starting fresh.
        """
        self.messages = []
        print("[INFO] Conversation history cleared")

    def get_model_info(self) -> Dict:
        """
        Get information about the current model.

        Returns:
            Dictionary with model information
        """
        return {
            "model": self.model,
            "endpoint": self.api_endpoint,
            "timeout": self.timeout
        }


# =============================================================================
# DEMONSTRATION: WHY LLMS ARE STATELESS
# =============================================================================

def demonstrate_stateless_behavior():
    """
    This demonstration shows that LLMs don't "remember" previous conversations.
    Each API call is completely independent.

    This is a FUNCTION (not a class method) that demonstrates the concept.
    """

    print("\n" + "="*70)
    print("DEMONSTRATION: LLMs Are Stateless (No Memory)")
    print("="*70)

    # Create a bot instance
    bot = OllamaBot(model="qwen3:8b")

    # Conversation 1
    print("\n--- Conversation 1 ---")
    bot.ask_question("My name is Alice and I love Python programming")

    # Conversation 2: Asking about previous conversation
    print("\n--- Conversation 2 (separate API call) ---")
    bot.ask_question("What is my name?")

    # Expected result: LLM won't know the name!
    # Why? Because each ask_question() call is independent.
    # The second call doesn't know about the first call.

    print("\n" + "="*70)
    print("EXPLANATION:")
    print("The LLM said it doesn't know your name because each API call")
    print("is completely independent. LLMs don't store data between calls.")
    print("To 'remember', we need to send conversation history (see Example 3)")
    print("="*70)


# =============================================================================
# INTERACTIVE MODE WITH OOP
# =============================================================================

def interactive_chat():
    """
    Interactive chat loop using our OllamaBot class.
    Note: This version has NO memory - each message is independent!

    This demonstrates how to USE the class in a practical application.
    """

    print("\n" + "="*70)
    print("INTERACTIVE MODE - Basic Chat (No Memory)")
    print("="*70)
    print("Type your messages to chat with the LLM")
    print("Commands:")
    print("  'quit' or 'exit' - Exit the program")
    print("  'help' - Show this message")
    print("  'info' - Show bot information")
    print("="*70)

    # Create our bot instance
    # This is OBJECT INSTANTIATION - creating an object from a class
    bot = OllamaBot(model="qwen3:8b")

    while True:
        # Get user input
        user_input = input("\n[YOU] ").strip()

        # Handle commands
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("[INFO] Goodbye!")
            break

        if user_input.lower() == 'help':
            print("\nCommands: quit, exit, help, info")
            print("Note: This chat has NO memory. Each message is independent.")
            continue

        if user_input.lower() == 'info':
            info = bot.get_model_info()
            print(f"\nBot Info: {json.dumps(info, indent=2)}")
            continue

        if not user_input:
            print("[INFO] Please enter a message")
            continue

        # Send message to LLM using our bot instance
        # This calls the ask_question() method
        bot.ask_question(user_input)

        # IMPORTANT: Notice that we don't save the conversation anywhere!
        # This means the LLM won't remember previous messages.
        # For conversation history, see example 03_conversation_history.py


# =============================================================================
# ADVANCED: Multiple Bots (OOP Advantage)
# =============================================================================

def demonstrate_multiple_bots():
    """
    Demonstrate OOP advantage: Creating multiple bot instances.

    This shows why OOP is powerful - you can have multiple bots
    with different configurations running at the same time!
    """

    print("\n" + "="*70)
    print("OOP ADVANTAGE: Multiple Bot Instances")
    print("="*70)

    # Create two different bots
    bot1 = OllamaBot(model="qwen3:8b")
    bot2 = OllamaBot(model="qwen3:8b")  # Could be a different model

    print("\n[Bot 1] Asking a question...")
    bot1.ask_question("What is the capital of France?")

    print("\n[Bot 2] Asking a different question...")
    bot2.ask_question("What is 2+2?")

    # Each bot maintains its own state independently!
    print("\n" + "="*70)
    print("EXPLANATION:")
    print("With OOP, you can create multiple bot instances easily.")
    print("Each instance has its own configuration and state.")
    print("This is much cleaner than using global variables!")
    print("="*70)


# =============================================================================
# CURL EQUIVALENT
# =============================================================================

def show_curl_equivalent():
    """
    Show the curl command that does the same thing.
    This helps you understand the HTTP layer.

    Even with OOP, under the hood it's still just HTTP!
    """

    print("\n" + "="*70)
    print("CURL EQUIVALENT (What Happens Under the Hood)")
    print("="*70)
    print("""
The OllamaBot class sends this HTTP request:

curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen3:8b",
  "messages": [
    {"role": "user", "content": "Hello! What is 2+2?"}
  ],
  "stream": false
}'

OOP Benefits vs Raw curl:
✅ Reusable code (create multiple bots easily)
✅ Error handling built-in
✅ Easy to extend (add features to the class)
✅ Cleaner code structure
✅ Industry-standard pattern

But remember: Under the hood, it's still just HTTP!
You can call Ollama from ANY language (see 05_curl_examples.sh)
    """)
    print("="*70)


# =============================================================================
# MAIN PROGRAM
# =============================================================================

def main():
    """
    Main entry point - demonstrates all features.

    This is a PROCEDURAL function that orchestrates the demonstrations.
    """

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║              Example 1: Basic LLM Chat (OOP Style)                ║
║                                                                   ║
║  Learn:                                                          ║
║  • How to structure AI code using classes                       ║
║  • How to make a simple LLM API call                            ║
║  • Request/response structure                                    ║
║  • Why LLMs are stateless (no memory)                           ║
║  • OOP advantages for production code                           ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Create a bot instance
    # This demonstrates OBJECT INSTANTIATION
    bot = OllamaBot(model="qwen3:8b")

    # Test 1: Simple question using our bot
    print("\n--- Test 1: Simple Question ---")
    bot.ask_question("What is the capital of France?")

    # Test 2: Math question
    print("\n--- Test 2: Math Question ---")
    bot.chat("What is 15 multiplied by 7?")  # Using the shorter alias

    # Test 3: Demonstrate stateless behavior
    demonstrate_stateless_behavior()

    # Test 4: Show multiple bots (OOP advantage)
    demonstrate_multiple_bots()

    # Show curl equivalent
    show_curl_equivalent()

    # Interactive mode
    print("\n[INFO] Starting interactive mode...")
    print("[REMINDER] This chat has NO memory. See example 03 for memory.")
    interactive_chat()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    """
    This block runs when the script is executed directly.
    It's the ENTRY POINT of the program.
    """

    # Check if Ollama is accessible before starting
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("[WARNING] Ollama is running but returned unexpected status")
    except requests.exceptions.RequestException:
        print("[ERROR] Cannot connect to Ollama!")
        print("[HINT] Make sure Ollama is running:")
        print("       1. Install from https://ollama.ai")
        print("       2. Run: ollama serve")
        print("       3. Pull model: ollama pull qwen3:8b")
        exit(1)

    # Run the main program
    main()


# =============================================================================
# OOP CONCEPTS DEMONSTRATED
# =============================================================================
"""
KEY OOP CONCEPTS IN THIS FILE:

1. CLASS:
   - Blueprint for creating objects
   - OllamaBot is our class

2. OBJECT/INSTANCE:
   - bot = OllamaBot() creates an instance
   - Each instance has its own data (self.model, self.messages, etc.)

3. CONSTRUCTOR (__init__):
   - Special method that runs when object is created
   - Initializes instance variables

4. INSTANCE METHODS:
   - Functions that belong to the class
   - ask_question(), chat(), reset() are methods
   - Always take 'self' as first parameter

5. INSTANCE VARIABLES:
   - Data that belongs to each object
   - self.model, self.messages, self.base_url
   - Each instance has its own copy

6. ENCAPSULATION:
   - Bundling data and methods together
   - All LLM logic is in one class

7. REUSABILITY:
   - Can create multiple bots easily
   - Can extend the class for new features

WHY OOP FOR AI/LLM CODE:
- Production codebases use OOP
- Easier to maintain and test
- Cleaner code organization
- Industry standard pattern
- Matches real-world software engineering

Compare this to functional/procedural style - OOP is much cleaner!
"""
