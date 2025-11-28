#!/usr/bin/env python3
"""
Example 07: Production Agent - Complete System
===============================================

A COMPLETE, production-ready agent combining ALL concepts!

This agent includes:
✅ Tools (weather, calculator, search)
✅ Memory (conversation history)
✅ Routing (intelligent request handling)
✅ Sequential processing (multi-step workflows)
✅ Error handling
✅ Logging
✅ Configuration management
✅ OOP design patterns

This is how you build REAL production agents!

Author: Beyhan MEYRALI
"""

import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from langchain_ollama import OllamaLLM
from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate


# =============================================================================
# PART 1: Tool Definitions
# =============================================================================

class AgentTools:
    """Collection of tools the agent can use."""

    @staticmethod
    def get_weather(city: str) -> dict:
        """Get weather for a city."""
        weather_db = {
            "tokyo": {"temp": 25, "condition": "sunny"},
            "paris": {"temp": 18, "condition": "cloudy"},
            "london": {"temp": 15, "condition": "rainy"},
            "new york": {"temp": 22, "condition": "clear"},
        }
        city_lower = city.lower()
        if city_lower in weather_db:
            return weather_db[city_lower]
        return {"error": f"No data for {city}"}

    @staticmethod
    def calculate(expression: str) -> dict:
        """Calculate a math expression."""
        try:
            result = eval(expression)  # WARNING: Demo only!
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def search_web(query: str) -> dict:
        """Simulate web search."""
        db = {
            "python": "Python is a high-level programming language.",
            "ai": "AI refers to intelligent computer systems.",
        }
        for key, val in db.items():
            if key in query.lower():
                return {"result": val}
        return {"error": "No results"}

    @staticmethod
    def get_tool_schemas() -> List[dict]:
        """Get tool schemas for Ollama."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather for a city",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string"}
                        },
                        "required": ["city"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "Calculate a math expression",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {"type": "string"}
                        },
                        "required": ["expression"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_web",
                    "description": "Search the web",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        },
                        "required": ["query"]
                    }
                }
            }
        ]


# =============================================================================
# PART 2: Production Agent
# =============================================================================

class ProductionAgent:
    """
    Production-ready agent with all features.

    Features:
    - Tool calling
    - Conversation memory
    - Error handling
    - Logging
    - Configuration
    """

    def __init__(
        self,
        model: str = "qwen3:8b",
        memory_size: int = 5,
        max_iterations: int = 5,
        verbose: bool = True
    ):
        """
        Initialize production agent.

        Args:
            model: Ollama model name
            memory_size: Number of conversation turns to remember
            max_iterations: Max tool-calling iterations
            verbose: Enable detailed logging
        """
        print(f"\n[INIT] Creating ProductionAgent...")
        print(f"  Model: {model}")
        print(f"  Memory: {memory_size} turns")
        print(f"  Max iterations: {max_iterations}")

        self.model = model
        self.max_iterations = max_iterations
        self.verbose = verbose

        # Initialize components
        self.tools = AgentTools()
        self.memory = ConversationBufferWindowMemory(k=memory_size)
        self.llm = OllamaLLM(model=model, temperature=0.7)

        # Statistics
        self.stats = {
            "total_requests": 0,
            "tools_called": 0,
            "errors": 0
        }

        print("[INIT] ✅ Production agent ready!")

    def _log(self, message: str, level: str = "INFO"):
        """Log message if verbose."""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}")

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
            "http://localhost:11434/api/chat",
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API error: {response.status_code}")

    def _execute_tool(self, tool_call: dict) -> str:
        """Execute a tool and return result."""
        func_name = tool_call["function"]["name"]
        args_raw = tool_call["function"]["arguments"]

        # Parse arguments
        if isinstance(args_raw, str):
            args = json.loads(args_raw)
        else:
            args = args_raw

        self._log(f"Executing tool: {func_name}({args})")

        # Execute
        if func_name == "get_weather":
            result = self.tools.get_weather(**args)
        elif func_name == "calculate":
            result = self.tools.calculate(**args)
        elif func_name == "search_web":
            result = self.tools.search_web(**args)
        else:
            result = {"error": f"Unknown tool: {func_name}"}

        self.stats["tools_called"] += 1
        return json.dumps(result)

    def chat(self, user_input: str) -> str:
        """
        Main chat method.

        Args:
            user_input: User's message

        Returns:
            Agent's response
        """
        self._log(f"User: {user_input}")
        self.stats["total_requests"] += 1

        # Get conversation history
        history = self.memory.load_memory_variables({})
        messages = []

        # Add history if available
        if history.get("history"):
            # Simple history parsing (in production, use proper format)
            messages.append({
                "role": "system",
                "content": f"Previous conversation:\n{history['history']}"
            })

        # Add current message
        messages.append({"role": "user", "content": user_input})

        # Agent loop with tools
        for iteration in range(self.max_iterations):
            self._log(f"Iteration {iteration + 1}/{self.max_iterations}")

            try:
                # Call LLM
                response = self._call_ollama(
                    messages,
                    self.tools.get_tool_schemas()
                )

                llm_message = response.get("message", {})
                messages.append(llm_message)

                # Check for tool calls
                tool_calls = llm_message.get("tool_calls")

                if tool_calls:
                    self._log(f"LLM requested {len(tool_calls)} tool(s)")

                    # Execute tools
                    for tool_call in tool_calls:
                        result = self._execute_tool(tool_call)
                        messages.append({
                            "role": "tool",
                            "content": result
                        })

                    # Continue loop
                    continue
                else:
                    # No tools - final answer
                    final_answer = llm_message.get("content", "No response")
                    self._log(f"Agent: {final_answer[:50]}...")

                    # Save to memory
                    self.memory.save_context(
                        {"input": user_input},
                        {"output": final_answer}
                    )

                    return final_answer

            except Exception as e:
                self._log(f"Error: {str(e)}", "ERROR")
                self.stats["errors"] += 1
                return f"Error: {str(e)}"

        # Max iterations reached
        return "Error: Max iterations reached without final answer"

    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return self.stats.copy()

    def reset_memory(self):
        """Clear conversation memory."""
        self.memory.clear()
        self._log("Memory cleared")


# =============================================================================
# DEMOS
# =============================================================================

def demo_basic_usage():
    """Demo: Basic conversation."""
    print("\n" + "="*70)
    print("DEMO 1: Basic Conversation with Memory")
    print("="*70)

    agent = ProductionAgent()

    # Multi-turn conversation
    agent.chat("Hello! My name is Alice.")
    agent.chat("What's my name?")
    agent.chat("What's the weather in Tokyo?")


def demo_tool_usage():
    """Demo: Tool calling."""
    print("\n" + "="*70)
    print("DEMO 2: Tool Usage")
    print("="*70)

    agent = ProductionAgent()

    questions = [
        "Calculate 15 * 23",
        "Search for information about Python",
        "What's the weather in Paris?"
    ]

    for q in questions:
        print(f"\n[Q]: {q}")
        answer = agent.chat(q)
        print(f"[A]: {answer[:100]}...")


def demo_complex_query():
    """Demo: Complex multi-tool query."""
    print("\n" + "="*70)
    print("DEMO 3: Complex Multi-Tool Query")
    print("="*70)

    agent = ProductionAgent()

    question = "What's the weather in London? Also calculate what that temperature is in Fahrenheit (F = C * 9/5 + 32)"
    print(f"\n[Q]: {question}")
    answer = agent.chat(question)
    print(f"\n[A]: {answer}")

    # Show stats
    print(f"\n[STATS]: {agent.get_stats()}")


def main():
    """Main entry point."""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║         Example 07: Production Agent - Complete System            ║
║                                                                   ║
║  This demonstrates:                                              ║
║  ✅ Tool calling (weather, calculator, search)                   ║
║  ✅ Conversation memory (remembers context)                      ║
║  ✅ Error handling (graceful failures)                           ║
║  ✅ Logging (detailed execution tracking)                        ║
║  ✅ Statistics (performance metrics)                             ║
║  ✅ OOP design (clean, maintainable code)                        ║
║  ✅ Production patterns (configuration, etc.)                    ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Run demos
    demo_basic_usage()
    demo_tool_usage()
    demo_complex_query()

    # Summary
    print("\n" + "="*70)
    print("✅ COMPLETE! LangChain Section Finished!")
    print("="*70)
    print("\n🎓 What you learned in this section (00-07):")
    print("  00 - Installation and setup verification")
    print("  01 - Basic chains and temperature")
    print("  02 - Advanced prompt templates")
    print("  03 - Conversation memory")
    print("  04 - Tool integration")
    print("  05 - Sequential workflows")
    print("  06 - Routing and branching")
    print("  07 - Production-ready agent (this script)")
    print("\n🎉 You now know LangChain!")
    print("\n📖 Key Production Patterns:")
    print("  • Tool calling for capabilities")
    print("  • Memory for context")
    print("  • Error handling for reliability")
    print("  • Logging for debugging")
    print("  • Stats for monitoring")
    print("  • OOP for maintainability")
    print("\n➡️  Next: Explore LangGraph for even more powerful workflows!")
    print("     Or move to CrewAI for multi-agent systems!")
    print("="*70)


if __name__ == "__main__":
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("[WARNING] Ollama might not be running correctly")
    except:
        print("[ERROR] Cannot connect to Ollama!")
        print("  Fix: ollama serve")
        exit(1)

    main()
