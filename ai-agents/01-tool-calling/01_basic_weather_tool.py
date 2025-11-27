#!/usr/bin/env python3
"""
Tool calling using Ollama's native tool calling API with qwen3:4b model.
Ollama now supports native function calling similar to OpenAI.
"""
import requests
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

class OllamaToolBot:
    def __init__(self, model="qwen-direct", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.messages = []
        
        # Define tools in Ollama format
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the current weather for a city",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "The name of the city",
                            }
                        },
                        "required": ["city"],
                    },
                },
            },
        ]
        
        print(f"[OK] Initialized Ollama tool bot with model: {model}")
        print(f"[OK] Ollama base URL: {base_url}")
        print(f"[OK] Using custom model without thinking output")
        print(f"[OK] Tools available: get_current_weather")

    def get_current_weather(self, city, unit="celsius"):
        """Mock weather function"""
        weather_data = {
            "tokyo": {"temperature": 25, "condition": "sunny", "humidity": "low"},
            "paris": {"temperature": 18, "condition": "cloudy", "humidity": "moderate"},
            "london": {"temperature": 15, "condition": "rainy", "humidity": "high"},
            "istanbul": {"temperature": 22, "condition": "partly cloudy", "humidity": "moderate"},
            "bursa": {"temperature": -5, "condition": "snowy", "humidity": "low"},
            "new york": {"temperature": 20, "condition": "clear", "humidity": "moderate"},
            "toronto": {"temperature": 16, "condition": "windy", "humidity": "moderate"}
        }
        
        city_lower = city.lower()
        if city_lower in weather_data:
            temp = weather_data[city_lower]["temperature"]
            if unit == "fahrenheit":
                temp = (temp * 9/5) + 32
                unit_symbol = "°F"
            else:
                unit_symbol = "°C"
            
            return json.dumps({
                "city": city,
                "temperature": f"{temp}{unit_symbol}",
                "condition": weather_data[city_lower]["condition"],
                "humidity": weather_data[city_lower]["humidity"],
                "unit": unit
            })
        else:
            return json.dumps({
                "city": city,
                "temperature": "unknown",
                "condition": "data not available",
                "humidity": "unknown"
            })

    def ask_question(self, question):
        """Send a question to Ollama with native tool calling"""
        try:
            url = f"{self.base_url}/api/chat"
            
            # Add user message to conversation
            self.messages.append({"role": "user", "content": question})
            
            # First call with tools
            payload = {
                "model": self.model,
                "messages": self.messages,
                "tools": self.tools,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9
                }
            }
            
            print(f"[ASK] Question: {question}")
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                response_data = response.json()
                message = response_data.get("message", {})
                
                # Add assistant response to conversation
                self.messages.append(message)
                
                # Check if the model wants to use tools
                tool_calls = message.get("tool_calls", [])
                
                if tool_calls:
                    print(f"[TOOL] AI wants to call tools!")
                    
                    for tool_call in tool_calls:
                        # Handle Ollama's tool call format
                        function_data = tool_call.get("function", {})
                        function_name = function_data.get("name")
                        arguments = function_data.get("arguments", {})
                        
                        print(f"[TOOL] Calling: {function_name} with {arguments}")
                        
                        # Execute the tool
                        if function_name == "get_weather":
                            # Handle both 'city' and 'location' parameter names
                            city = arguments.get("city") or arguments.get("location", "")
                            unit = arguments.get("unit", "celsius")
                            result = self.get_current_weather(city, unit)
                            print(f"[TOOL] Result: {result}")
                            
                            # Add tool result to conversation
                            self.messages.append({
                                "role": "tool",
                                "content": result
                            })
                    
                    # Get final response with tool results
                    return self.get_final_response()
                else:
                    # Direct response without tool use
                    content = message.get("content", "")
                    cleaned_content = self.clean_response(content)
                    try:
                        print(f"[OK] Direct response: {cleaned_content}")
                    except UnicodeEncodeError:
                        safe_content = cleaned_content.encode('ascii', 'replace').decode('ascii')
                        print(f"[OK] Direct response: {safe_content}")
                    return cleaned_content
                    
            else:
                error_msg = f"Ollama API Error: {response.status_code} - {response.text}"
                print(f"[ERROR] {error_msg}")
                return error_msg
                
        except Exception as e:
            error_msg = f"Connection error: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return error_msg

    def get_final_response(self):
        """Get AI's final response after tool execution"""
        try:
            url = f"{self.base_url}/api/chat"
            
            payload = {
                "model": self.model,
                "messages": self.messages,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                response_data = response.json()
                final_response = response_data.get("message", {}).get("content", "")
                cleaned_final = self.clean_response(final_response)
                
                self.messages.append({"role": "assistant", "content": cleaned_final})
                try:
                    print(f"[OK] Final response: {cleaned_final}")
                except UnicodeEncodeError:
                    safe_response = cleaned_final.encode('ascii', 'replace').decode('ascii')
                    print(f"[OK] Final response: {safe_response}")
                return cleaned_final
            else:
                return f"Error getting final response: {response.status_code}"
                
        except Exception as e:
            return f"Error in final response: {str(e)}"

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

class Query(BaseModel):
    query: str

@app.get("/")
async def root():
    return {"message": "Hello World - Ollama Native Tool Calling", "model": "qwen3:4b", "tools": ["get_current_weather"]}

async def ollama_tool_chat(query: str):
    try:
        bot = OllamaToolBot()
        answer = bot.ask_question(query)
        return {"ai_response": answer, "model": "qwen3:4b", "tools_available": ["get_current_weather"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/{query}")
async def chat_get(query: str):
    return await ollama_tool_chat(query)

@app.post("/chat")
async def chat_post(query: Query):
    return await ollama_tool_chat(query.query)

def main():
    """Test native tool calling functionality"""
    try:
        bot = OllamaToolBot()
        
        # Test questions that should trigger tool calling
        test_questions = [
            "What is the weather in Toronto?",
            "What's the weather in Tokyo?",
            "How's the weather in Paris today?",
            "Tell me about the weather in Istanbul",
            "What's the capital of France?",  # This should NOT trigger tool calling
            "Is it raining in London?",
            "What's the temperature in New York in fahrenheit?"
        ]
        
        print("\n" + "="*60)
        print("RUNNING NATIVE TOOL CALLING TESTS")
        print("="*60)
        print("Note: This requires Ollama with tool calling support")
        print("Make sure you're running a recent version of Ollama")
        print("="*60)
        
        for question in test_questions:
            print(f"\n[TEST] {question}")
            result = bot.ask_question(question)
            print(f"[RESULT] {result}")
            print("-" * 50)
            bot.reset_conversation()  # Reset for each test
        
        print("\n[SUCCESS] Tool calling tests completed!")
        
        # Interactive questioning
        print("\n" + "="*60)
        print("INTERACTIVE MODE - Ask your own questions!")
        print("Available tool: get_current_weather(city, unit)")
        print("Try questions like:")
        print("  - 'What is the weather in Toronto?'")
        print("  - 'Temperature in Tokyo in fahrenheit?'")
        print("  - 'Is it raining in London?'")
        print("Type 'quit', 'exit' or 'reset' to control the session")
        print("="*60)
        
        bot.reset_conversation()  # Start fresh for interactive mode
        
        while True:
            try:
                user_question = input("\n[YOU] Enter your question: ").strip()
                
                if user_question.lower() in ['quit', 'exit', 'q']:
                    print("[INFO] Exiting interactive mode...")
                    break
                
                if user_question.lower() == 'reset':
                    bot.reset_conversation()
                    print("[INFO] Conversation reset")
                    continue
                
                if not user_question:
                    print("[INFO] Please enter a question or 'quit' to exit")
                    continue
                
                result = bot.ask_question(user_question)
                
            except KeyboardInterrupt:
                print("\n[INFO] Interrupted by user. Exiting...")
                break
            except Exception as e:
                print(f"[ERROR] Error processing question: {str(e)}")
                continue
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        return 1

if __name__ == "__main__":
    # Run direct test
    main()
    
    # Uncomment to run FastAPI server
    # uvicorn.run(app, host="0.0.0.0", port=8002)

# Example URLs when running as server:
# http://127.0.0.1:8002/chat/weather%20in%20toronto
# http://127.0.0.1:8002/chat/temperature%20in%20tokyo