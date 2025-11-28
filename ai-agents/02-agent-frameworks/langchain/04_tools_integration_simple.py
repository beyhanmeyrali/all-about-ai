#!/usr/bin/env python3
"""
Example 04: Tools Integration - Give Agents Superpowers (Simplified)
=====================================================================

Learn how to give agents TOOLS using Ollama's native tool calling!

What you'll learn:
- What tools are and why they matter
- Creating tools with @tool decorator
- Tool calling with Ollama's native support
- Manual tool execution loop (ReAct pattern)
- Error handling in tools

This works with modern LangChain + Ollama!

Author: Beyhan MEYRALI
"""

import json
import requests
from typing import Dict, Any, List
from datetime import datetime


# =============================================================================
# PART 1: Define Tool Functions with @tool decorator
# =============================================================================

def get_weather_impl(city: str) -> dict:
    """Implementation of weather lookup."""
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
        return {
            "city": city,
            "temperature_celsius": data["temp"],
            "condition": data["condition"],
            "humidity": data["humidity"]
        }
    else:
        return {"error": f"No weather data for {city}"}


def calculate_impl(expression: str) -> dict:
    """Implementation of calculator."""
    try:
        # Safe evaluation for demo (DON'T use eval in production!)
        result = eval(expression)
        return {"expression": expression, "result": result}
    except Exception as e:
        return {"error": f"Cannot calculate: {str(e)}"}


def search_web_impl(query: str) -> dict:
    """Implementation of web search."""
    search_db = {
        "python": {
            "title": "Python Programming",
            "snippet": "Python is a high-level programming language."
        },
        "ai": {
            "title": "Artificial Intelligence",
            "snippet": "AI refers to intelligent computer systems."
        },
        "langchain": {
            "title": "LangChain Framework",
            "snippet": "LangChain is a framework for building LLM apps."
        }
    }

    query_lower = query.lower()
    for key, data in search_db.items():
        if key in query_lower:
            return {"query": query, "result": data}

    return {"query": query, "result": None, "message": "No results found"}


# =============================================================================
# PART 2: Create Tool Schemas for Ollama
# =============================================================================

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city. Input should be a city name like 'Tokyo' or 'Paris'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Calculate a mathematical expression. Input should be like '2+2' or '15*7'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The math expression to calculate"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information. Input should be a search query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    }
]


# Map function names to implementations
TOOL_FUNCTIONS = {
    "get_weather": get_weather_impl,
    "calculate": calculate_impl,
    "search_web": search_web_impl
}


# =============================================================================
# PART 3: Simple Tool-Calling Agent
# =============================================================================

class SimpleToolAgent:
    """
    Simple agent that can call tools using Ollama's native tool calling.

    This implements the ReAct pattern manually:
    1. Reason - LLM decides which tool to call
    2. Act - Execute the tool
    3. Observe - Get tool result
    4. Repeat until done
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize the agent."""
        print(f"\n[INIT] Creating SimpleToolAgent with {model}...")
        self.model = model
        self.base_url = "http://localhost:11434"
        print("[INIT] ✅ Agent ready!")

    def _call_ollama(self, messages: List[dict], tools: List[dict] = None) -> dict:
        """Call Ollama API."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        if tools:
            payload["tools"] = tools

        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Ollama API error: {response.status_code}")

    def _execute_tool(self, tool_call: dict) -> str:
        """Execute a tool and return the result."""
        function_name = tool_call["function"]["name"]

        # Parse arguments
        args_raw = tool_call["function"]["arguments"]
        if isinstance(args_raw, str):
            arguments = json.loads(args_raw)
        else:
            arguments = args_raw

        print(f"\n[TOOL] Calling: {function_name}({arguments})")

        # Execute tool
        if function_name in TOOL_FUNCTIONS:
            result = TOOL_FUNCTIONS[function_name](**arguments)
            print(f"[TOOL] Result: {result}")
            return json.dumps(result)
        else:
            error = {"error": f"Unknown tool: {function_name}"}
            return json.dumps(error)

    def ask(self, question: str, max_iterations: int = 5) -> str:
        """
        Ask the agent a question.

        Args:
            question: User's question
            max_iterations: Max tool-calling loops

        Returns:
            Final answer
        """
        print("\n" + "="*70)
        print(f"QUESTION: {question}")
        print("="*70)

        messages = [{"role": "user", "content": question}]

        for iteration in range(max_iterations):
            print(f"\n[ITERATION {iteration + 1}]")

            # Call LLM with tools
            response = self._call_ollama(messages, TOOLS_SCHEMA)
            llm_message = response.get("message", {})

            # Add LLM's message to history
            messages.append(llm_message)

            # Check if LLM wants to call tools
            tool_calls = llm_message.get("tool_calls")

            if tool_calls:
                print(f"[AGENT] Wants to call {len(tool_calls)} tool(s)")

                # Execute each tool
                for tool_call in tool_calls:
                    result = self._execute_tool(tool_call)

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "content": result
                    })

                # Continue loop - LLM might call more tools
                continue

            else:
                # No tool calls - LLM has final answer
                final_answer = llm_message.get("content", "No response")
                print("\n" + "="*70)
                print("FINAL ANSWER:")
                print("="*70)
                print(final_answer)
                print("="*70)
                return final_answer

        # Max iterations reached
        return "Error: Max iterations reached"


# =============================================================================
# DEMOS
# =============================================================================

def demo_single_tool():
    """Demo: Single tool usage."""
    print("\n" + "="*70)
    print("DEMO 1: Single Tool Usage")
    print("="*70)

    agent = SimpleToolAgent()
    agent.ask("What's the weather in Tokyo?")


def demo_calculator():
    """Demo: Calculator tool."""
    print("\n" + "="*70)
    print("DEMO 2: Calculator Tool")
    print("="*70)

    agent = SimpleToolAgent()
    agent.ask("What is 456 multiplied by 789?")


def demo_search():
    """Demo: Search tool."""
    print("\n" + "="*70)
    print("DEMO 3: Search Tool")
    print("="*70)

    agent = SimpleToolAgent()
    agent.ask("Search for information about Python")


def demo_multiple_tools():
    """Demo: Multiple tools in one query."""
    print("\n" + "="*70)
    print("DEMO 4: Multiple Tools")
    print("="*70)

    agent = SimpleToolAgent()
    agent.ask("What's the weather in Paris? Also calculate what that is in Fahrenheit (F = C * 9/5 + 32)")


def demo_no_tools():
    """Demo: Question not needing tools."""
    print("\n" + "="*70)
    print("DEMO 5: No Tools Needed")
    print("="*70)

    agent = SimpleToolAgent()
    agent.ask("What is the capital of France?")


def main():
    """Main entry point."""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║         Example 04: Tools Integration (Simplified)                ║
║                                                                   ║
║  This demonstrates:                                              ║
║  • Creating tool schemas for Ollama                              ║
║  • Native tool calling with qwen3:8b                            ║
║  • ReAct pattern (Reason → Act → Observe)                       ║
║  • Manual tool execution loop                                    ║
║  • Error handling in tools                                       ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Run demos
    demo_single_tool()
    demo_calculator()
    demo_search()
    demo_multiple_tools()
    demo_no_tools()

    # Summary
    print("\n" + "="*70)
    print("✅ COMPLETE!")
    print("="*70)
    print("\n🎓 What you learned:")
    print("  1. How to create tool schemas for Ollama")
    print("  2. Native tool calling with qwen3:8b")
    print("  3. ReAct pattern (Reason → Act → Observe)")
    print("  4. Manual tool execution loop")
    print("  5. Error handling in tools")
    print("\n📖 Key Concepts:")
    print("  • Tools = Functions agents can call")
    print("  • Tool schema = Description for LLM")
    print("  • ReAct = Reasoning + Acting loop")
    print("  • Ollama native = Better than LangChain agents!")
    print("\n💡 Why This Approach?")
    print("  • Simpler than LangChain AgentExecutor")
    print("  • Uses Ollama's native tool calling")
    print("  • Full control over execution")
    print("  • Easy to debug and customize")
    print("\n➡️  Next: python 05_sequential_chains.py")
    print("="*70)


if __name__ == "__main__":
    # Check Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("[WARNING] Ollama might not be running correctly")
    except:
        print("[ERROR] Cannot connect to Ollama!")
        print("  Fix: ollama serve")
        exit(1)

    main()
