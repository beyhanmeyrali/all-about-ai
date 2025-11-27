#!/usr/bin/env python3
"""
Example 1: Basic Chat with Ollama
==================================

This is the SIMPLEST possible LLM interaction.
Perfect for understanding the fundamentals.

What you'll learn:
- How to make a basic API call to an LLM
- The request/response structure
- Why LLMs are stateless (no memory between calls)

Author: Beyhan MEYRALI
"""

import requests
import json

# =============================================================================
# CONFIGURATION
# =============================================================================

OLLAMA_BASE_URL = "http://localhost:11434"  # Default Ollama endpoint
MODEL_NAME = "qwen3:8b"  # Best tool-calling model for local agents (2025)


# =============================================================================
# BASIC CHAT FUNCTION
# =============================================================================

def chat_with_llm(user_message):
    """
    Send a single message to the LLM and get a response.

    This is the CORE of all LLM interactions:
    1. Prepare your message
    2. Send HTTP POST request
    3. Parse the response

    Args:
        user_message (str): The message to send to the LLM

    Returns:
        str: The LLM's response
    """

    # Step 1: Prepare the API endpoint
    url = f"{OLLAMA_BASE_URL}/api/chat"

    # Step 2: Prepare the request payload
    # This is the JSON structure Ollama expects
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",  # Who is sending this message
                "content": user_message  # The actual message content
            }
        ],
        "stream": False  # Get complete response at once (not token-by-token)
    }

    # Step 3: Send POST request to Ollama
    print(f"[INFO] Sending message to {MODEL_NAME}...")
    print(f"[USER] {user_message}")

    try:
        response = requests.post(url, json=payload, timeout=60)

        # Step 4: Check if request was successful
        if response.status_code == 200:
            # Parse JSON response
            response_data = response.json()

            # Extract the LLM's message from the response
            # Structure: response['message']['content']
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


# =============================================================================
# DEMONSTRATION: WHY LLMS ARE STATELESS
# =============================================================================

def demonstrate_stateless_behavior():
    """
    This demonstration shows that LLMs don't "remember" previous conversations.
    Each API call is completely independent.
    """

    print("\n" + "="*70)
    print("DEMONSTRATION: LLMs Are Stateless (No Memory)")
    print("="*70)

    # Conversation 1
    print("\n--- Conversation 1 ---")
    chat_with_llm("My name is Alice and I love Python programming")

    # Conversation 2: Asking about previous conversation
    print("\n--- Conversation 2 (separate API call) ---")
    chat_with_llm("What is my name?")

    # Expected result: LLM won't know the name!
    # Why? Because each chat_with_llm() call is independent.
    # The second call doesn't know about the first call.

    print("\n" + "="*70)
    print("EXPLANATION:")
    print("The LLM said it doesn't know your name because each API call")
    print("is completely independent. LLMs don't store data between calls.")
    print("To 'remember', we need to send conversation history (see Example 3)")
    print("="*70)


# =============================================================================
# INTERACTIVE MODE
# =============================================================================

def interactive_chat():
    """
    Simple interactive chat loop.
    Note: This version has NO memory - each message is independent!
    """

    print("\n" + "="*70)
    print("INTERACTIVE MODE - Basic Chat (No Memory)")
    print("="*70)
    print("Type your messages to chat with the LLM")
    print("Commands:")
    print("  'quit' or 'exit' - Exit the program")
    print("  'help' - Show this message")
    print("="*70)

    while True:
        # Get user input
        user_input = input("\n[YOU] ").strip()

        # Handle commands
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("[INFO] Goodbye!")
            break

        if user_input.lower() == 'help':
            print("\nCommands: quit, exit, help")
            print("Note: This chat has NO memory. Each message is independent.")
            continue

        if not user_input:
            print("[INFO] Please enter a message")
            continue

        # Send message to LLM
        chat_with_llm(user_input)

        # IMPORTANT: Notice that we don't save the conversation anywhere!
        # This means the LLM won't remember previous messages.
        # For conversation history, see example 03_conversation_history.py


# =============================================================================
# CURL EQUIVALENT
# =============================================================================

def show_curl_equivalent():
    """
    Show the curl command that does the same thing.
    This helps you understand the HTTP layer.
    """

    print("\n" + "="*70)
    print("CURL EQUIVALENT")
    print("="*70)
    print("""
You can do the same thing with curl (no Python needed!):

curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:3b",
  "messages": [
    {"role": "user", "content": "Hello! What is 2+2?"}
  ],
  "stream": false
}'

This shows that LLM APIs are just HTTP endpoints.
You can call them from ANY language or tool:
- JavaScript: fetch()
- Java: HttpClient
- Go: net/http
- Postman, Insomnia, etc.
    """)
    print("="*70)


# =============================================================================
# MAIN PROGRAM
# =============================================================================

def main():
    """
    Run all demonstrations
    """

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                   Example 1: Basic LLM Chat                       ║
║                                                                   ║
║  Learn:                                                          ║
║  • How to make a simple LLM API call                            ║
║  • Request/response structure                                    ║
║  • Why LLMs are stateless (no memory)                           ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Test 1: Simple question
    print("\n--- Test 1: Simple Question ---")
    chat_with_llm("What is the capital of France?")

    # Test 2: Math question
    print("\n--- Test 2: Math Question ---")
    chat_with_llm("What is 15 multiplied by 7?")

    # Test 3: Demonstrate stateless behavior
    demonstrate_stateless_behavior()

    # Show curl equivalent
    show_curl_equivalent()

    # Interactive mode
    print("\n[INFO] Starting interactive mode...")
    print("[REMINDER] This chat has NO memory. See example 03 for memory.")
    interactive_chat()


if __name__ == "__main__":
    # Check if Ollama is accessible
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
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
