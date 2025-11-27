#!/usr/bin/env python3
"""
Example 2: Streaming Chat with Conversation History
====================================================

Learn how to maintain conversation context and handle responses.

What you'll learn:
- How to maintain conversation history (memory)
- Why conversation history is needed (LLMs are stateless)
- Cleaning LLM responses (removing thinking tags)
- Error handling for API calls

DEBUGGING TIPS FOR NEWBIES:
---------------------------
1. If you get "Connection refused":
   - Make sure Ollama is running: `ollama serve`
   - Check if Ollama is accessible: `curl http://localhost:11434/api/tags`

2. If you get "Model not found":
   - Pull the model first: `ollama pull qwen3:8b`
   - Check available models: `ollama list`

3. If responses are weird or include thinking:
   - The clean_response() method removes <think> tags
   - You can add more cleaning logic in that function

4. To see what's being sent to the LLM:
   - Add: `print(json.dumps(payload, indent=2))` before requests.post()
   - This shows the exact JSON being sent

5. To debug conversation history:
   - Add: `print(f"Messages: {len(self.messages)}")` to see history size
   - Add: `print(self.messages)` to see full conversation

Author: Beyhan MEYRALI
"""
import requests
import json
from fastapi import FastAPI, HTTPException
import uvicorn

class OllamaBot:
    """
    A simple chatbot that maintains conversation history.

    This class demonstrates:
    - Conversation history management (the 'messages' list)
    - API error handling
    - Response cleaning

    Each instance maintains its own conversation history!
    """

    def __init__(self, model="qwen3:8b", base_url="http://localhost:11434"):
        """
        Initialize the chatbot.

        Args:
            model: The Ollama model to use (default: qwen3:8b)
            base_url: Ollama API endpoint

        Debugging: If this fails, check if Ollama is running with `ollama serve`
        """
        self.model = model
        self.base_url = base_url

        # This list stores the conversation history!
        # Each time you ask a question, it gets added here
        # This is how the LLM "remembers" previous messages
        self.messages = []

        print(f"[OK] Initialized Ollama bot with model: {model}")
        print(f"[OK] Ollama base URL: {base_url}")

    def ask_question(self, question):
        """
        Send a question to Ollama and maintain conversation history.

        This method:
        1. Adds your question to conversation history
        2. Sends ALL history to the LLM (this is how it "remembers")
        3. Gets the response
        4. Adds the response to history
        5. Returns the cleaned response

        Debugging: If you get errors here, add print statements to see the payload
        """
        try:
            url = f"{self.base_url}/api/chat"

            # IMPORTANT: Add user message to conversation history
            # This is how we build up the conversation over time
            self.messages.append({"role": "user", "content": question})
            
            # Prepare the payload
            # NOTE: We send ALL messages (entire conversation history)
            # This is why the LLM "remembers" - it sees everything each time!
            payload = {
                "model": self.model,
                "messages": self.messages,  # <- Full conversation history!
                "stream": False,  # Get complete response at once
                "options": {
                    "temperature": 0.1,  # Lower = more focused, Higher = more creative
                    "top_p": 0.9  # Nucleus sampling parameter
                }
            }

            # DEBUGGING: Uncomment to see what's being sent to the LLM
            # print(f"[DEBUG] Payload: {json.dumps(payload, indent=2)}")
            
            print(f"[ASK] Asking: {question}")
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                response_data = response.json()
                ai_response = response_data.get("message", {}).get("content", "")
                
                # Filter out thinking tags from response
                cleaned_response = self.clean_response(ai_response)
                
                # Add assistant response to conversation
                self.messages.append({"role": "assistant", "content": cleaned_response})
                
                # Handle encoding issues on Windows
                try:
                    print(f"[OK] Response: {cleaned_response}")
                except UnicodeEncodeError:
                    # Fallback to ASCII-safe output
                    safe_response = cleaned_response.encode('ascii', 'replace').decode('ascii')
                    print(f"[OK] Response: {safe_response}")
                return cleaned_response
            else:
                error_msg = f"Ollama API Error: {response.status_code} - {response.text}"
                print(f"[ERROR] {error_msg}")
                return error_msg
                
        except Exception as e:
            error_msg = f"Connection error: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return error_msg

    def clean_response(self, response):
        """
        Remove thinking tags and content from response.

        Some models output their "thinking process" in <think> tags.
        We remove these to show only the final answer to the user.

        Example:
            Input:  "<think>Let me calculate...</think>The answer is 4"
            Output: "The answer is 4"

        Debugging: If you see weird output, check if there are other tags to remove
        """
        import re
        # Remove <think>...</think> blocks
        # The 're.DOTALL' flag makes '.' match newlines too
        cleaned = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)

        # Remove any remaining empty lines and extra whitespace
        cleaned = '\n'.join(line.strip() for line in cleaned.split('\n') if line.strip())
        return cleaned.strip()

    def reset_conversation(self):
        """Reset the conversation history"""
        self.messages = []
        print("[INFO] Conversation history reset")


# FastAPI app
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World - Ollama Basic Chat", "model": "qwen3:8b"}

async def ollama_chat(query: str):
    try:
        bot = OllamaBot()
        answer = bot.ask_question(query)
        return {"ai_response": answer, "model": "qwen3:8b"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/{query}")
async def chat_get(query: str):
    return await ollama_chat(query)

def main():
    """Test the basic chat functionality"""
    try:
        bot = OllamaBot()
        
        # Test predefined questions
        print("\n" + "="*50)
        print("RUNNING PREDEFINED TESTS")
        print("="*50)
        
        bot.ask_question("What is the capital of France?")
        bot.ask_question("Tell me a short joke")
        
        print("\n[SUCCESS] Predefined tests completed successfully!")
        
        # Interactive questioning
        print("\n" + "="*50)
        print("INTERACTIVE MODE - Ask your own questions!")
        print("Type 'quit', 'exit' or 'reset' to control the session")
        print("="*50)
        
        while True:
            try:
                user_question = input("\n[YOU] Enter your question: ").strip()
                
                if user_question.lower() in ['quit', 'exit', 'q']:
                    print("[INFO] Exiting interactive mode...")
                    break
                
                if user_question.lower() == 'reset':
                    bot.reset_conversation()
                    continue
                
                if not user_question:
                    print("[INFO] Please enter a question or 'quit' to exit")
                    continue
                
                result = bot.ask_question(user_question)
                # Result is already printed in the ask_question method
                
            except KeyboardInterrupt:
                print("\n[INFO] Interrupted by user. Exiting...")
                break
            except Exception as e:
                print(f"[ERROR] Error processing question: {str(e)}")
                continue
        
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    # Run direct test
    main()
    
    # Uncomment to run FastAPI server
    # uvicorn.run(app, host="0.0.0.0", port=8002)

# Example URLs:
# http://127.0.0.1:8002/chat/tallest%20man%20in%20the%20world
# http://127.0.0.1:8002/chat/weather%20in%20istanbul