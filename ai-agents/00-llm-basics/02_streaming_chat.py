#!/usr/bin/env python3
"""
Simple chat using Ollama with qwen3:4b model.
Basic chat functionality without tool calling.
"""
import requests
import json
from fastapi import FastAPI, HTTPException
import uvicorn

class OllamaBot:
    def __init__(self, model="qwen-direct", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.messages = []
        
        print(f"[OK] Initialized Ollama bot with model: {model}")
        print(f"[OK] Ollama base URL: {base_url}")
        print(f"[OK] Using custom model without thinking output")

    def ask_question(self, question):
        """Send a question to Ollama"""
        try:
            url = f"{self.base_url}/api/chat"
            
            # Add user message to conversation
            self.messages.append({"role": "user", "content": question})
            
            payload = {
                "model": self.model,
                "messages": self.messages,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9
                }
            }
            
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
        """Remove thinking tags and content from response"""
        import re
        # Remove <think>...</think> blocks
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
    return {"message": "Hello World - Ollama Basic Chat", "model": "qwen3:4b"}

async def ollama_chat(query: str):
    try:
        bot = OllamaBot()
        answer = bot.ask_question(query)
        return {"ai_response": answer, "model": "qwen3:4b"}
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