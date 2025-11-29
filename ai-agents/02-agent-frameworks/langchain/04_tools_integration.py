#!/usr/bin/env python3
"""
Example 04: Tools Integration - Give Agents Superpowers
========================================================

Learn how to give agents TOOLS - this is what makes them truly powerful!

What you'll learn:
- What tools are and why they matter
- Creating custom tools with @tool decorator
- Binding tools to LLMs (Modern LCEL)
- Executing tool calls
- Building a simple tool-using agent loop

This is CRITICAL - tools transform chatbots into agents!

Author: Beyhan MEYRALI
"""

import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_ollama import ChatOllama
from langchain_core.tools import tool, Tool, StructuredTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

# =============================================================================
# PART 1: Simple Tool Functions
# =============================================================================

def get_weather(city: str) -> str:
    """
    Get current weather for a city.
    
    Args:
        city: Name of the city (e.g., "Tokyo", "Paris")
    """
    # Mock weather database
    weather_db = {
        "tokyo": {"temp": 25, "condition": "sunny", "humidity": 60},
        "paris": {"temp": 18, "condition": "cloudy", "humidity": 75},
        "london": {"temp": 15, "condition": "rainy", "humidity": 85},
        "new york": {"temp": 22, "condition": "clear", "humidity": 50},
        "dubai": {"temp": 35, "condition": "hot", "humidity": 40},
    }

    city_lower = city.lower()
    if city_lower in weather_db:
        data = weather_db[city_lower]
        return json.dumps({
            "city": city,
            "temperature_celsius": data["temp"],
            "condition": data["condition"],
            "humidity": data["humidity"],
            "timestamp": datetime.now().isoformat()
        })
    else:
        return json.dumps({"error": f"No weather data for {city}"})

def calculate(expression: str) -> str:
    """
    Calculate a mathematical expression.
    
    Args:
        expression: Math expression (e.g., "2 + 2", "15 * 7")
    """
    try:
        # WARNING: eval() is dangerous! Use only for demo
        result = eval(expression)
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": f"Cannot calculate: {str(e)}"})

def search_web(query: str) -> str:
    """
    Search the web for information.
    
    Args:
        query: Search query
    """
    # Mock search results
    results = {
        "python": "Python is a high-level programming language...",
        "ai": "Artificial Intelligence is intelligence demonstrated by machines...",
        "langchain": "LangChain is a framework for developing applications powered by LLMs..."
    }
    
    query_lower = query.lower()
    for key, val in results.items():
        if key in query_lower:
            return json.dumps({"snippet": val})
            
    return json.dumps({"snippet": "No results found."})

# =============================================================================
# PART 2: Modern Tool Agent
# =============================================================================

class ModernToolAgent:
    """
    Agent that uses modern LCEL tool binding.
    
    Instead of legacy AgentExecutor, we use:
    1. llm.bind_tools(tools)
    2. Manual execution loop (or LangGraph in production)
    """

    def __init__(self, model: str = "qwen3:8b"):
        print(f"\n[INIT] Creating ModernToolAgent with {model}...")
        
        # 1. Create LLM
        self.llm = ChatOllama(model=model, temperature=0.0)
        
        # 2. Define Tools (using StructuredTool for better schema)
        self.tools = [
            StructuredTool.from_function(
                func=get_weather,
                name="get_weather",
                description="Get current weather for a city"
            ),
            StructuredTool.from_function(
                func=calculate,
                name="calculate",
                description="Calculate math expressions"
            ),
            StructuredTool.from_function(
                func=search_web,
                name="search_web",
                description="Search the web for information"
            )
        ]
        
        # Map for execution
        self.tool_map = {t.name: t for t in self.tools}
        
        # 3. Bind tools to LLM
        # This tells the LLM about the tools and their schemas
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        print("[INIT] ✅ Agent ready with tools!")

    def ask(self, question: str):
        """
        Run the agent loop.
        
        1. Send question to LLM
        2. Check for tool calls
        3. Execute tools if needed
        4. Send results back to LLM
        5. Get final answer
        """
        print("\n" + "="*70)
        print(f"QUESTION: {question}")
        print("="*70)
        
        messages = [HumanMessage(content=question)]
        
        # Step 1: Initial LLM Call
        print("  🤔 Thinking...")
        response = self.llm_with_tools.invoke(messages)
        messages.append(response)
        
        # Step 2: Check for tool calls
        if response.tool_calls:
            print(f"  🛠️  LLM wants to call {len(response.tool_calls)} tool(s):")
            
            # Step 3: Execute tools
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]
                
                print(f"    → Calling {tool_name} with {tool_args}")
                
                if tool_name in self.tool_map:
                    tool_instance = self.tool_map[tool_name]
                    try:
                        # Execute
                        tool_result = tool_instance.invoke(tool_args)
                        print(f"    ✓ Result: {tool_result}")
                        
                        # Add result to messages
                        messages.append(ToolMessage(
                            content=str(tool_result),
                            tool_call_id=tool_id,
                            name=tool_name
                        ))
                    except Exception as e:
                        print(f"    ❌ Error: {e}")
                        messages.append(ToolMessage(
                            content=f"Error: {str(e)}",
                            tool_call_id=tool_id,
                            name=tool_name
                        ))
                else:
                    print(f"    ❌ Unknown tool: {tool_name}")

            # Step 4: Final LLM Call (with tool results)
            print("  🤔 Synthesizing answer...")
            final_response = self.llm_with_tools.invoke(messages)
            print("\nFINAL ANSWER:")
            print(final_response.content)
            return final_response.content
            
        else:
            # No tools needed
            print("\nFINAL ANSWER (No tools used):")
            print(response.content)
            return response.content

# =============================================================================
# DEMOS
# =============================================================================

def main():
    agent = ModernToolAgent()
    
    # Demo 1: Single Tool
    agent.ask("What's the weather in Tokyo?")
    
    # Demo 2: Math
    agent.ask("Calculate 15 * 7 + 10")
    
    # Demo 3: Multi-step (Parallel or Sequential)
    # Note: Basic loop handles parallel calls in one turn. 
    # For multi-turn (A then B), we'd need a while loop (like in 01-tool-calling).
    # This simple implementation handles "Parallel" calls well.
    agent.ask("What's the weather in Paris and London?")

if __name__ == "__main__":
    # Check Ollama
    try:
        requests.get("http://localhost:11434/api/tags", timeout=5)
    except:
        print("Error: Ollama not running!")
        exit(1)
        
    main()
