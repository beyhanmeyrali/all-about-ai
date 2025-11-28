#!/usr/bin/env python3
"""
Example 04: Tools Integration - Give Agents Superpowers
========================================================

Learn how to give agents TOOLS - this is what makes them truly powerful!

What you'll learn:
- What tools are and why they matter
- Creating custom tools with @tool decorator
- Creating tools with Tool class
- Using AgentExecutor with tools
- Multiple tools coordination
- Error handling in tools
- Production tool patterns

This is CRITICAL - tools transform chatbots into agents!

Author: Beyhan MEYRALI
"""

import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_ollama import ChatOllama
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage


# =============================================================================
# PART 1: Simple Tool Functions
# =============================================================================

def get_weather(city: str) -> str:
    """
    Get current weather for a city.

    This is a MOCK tool for demonstration.
    In production, you'd call a real weather API.

    Args:
        city: Name of the city

    Returns:
        Weather information as JSON string
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
        }, indent=2)
    else:
        return json.dumps({"error": f"No weather data for {city}"})


def calculate(expression: str) -> str:
    """
    Calculate a mathematical expression.

    SECURITY NOTE: In production, use a safe eval library!
    This uses Python's eval() which can be dangerous.

    Args:
        expression: Math expression (e.g., "2 + 2", "15 * 7")

    Returns:
        Calculation result as string
    """
    try:
        # WARNING: eval() is dangerous! Use only for demo
        # In production: use ast.literal_eval() or a math parser
        result = eval(expression)
        return json.dumps({
            "expression": expression,
            "result": result
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Cannot calculate: {str(e)}"})


def search_web(query: str) -> str:
    """
    Simulate web search.

    This is a MOCK. In production, use real search APIs
    like SerpAPI, Google Custom Search, or Bing Search.

    Args:
        query: Search query

    Returns:
        Search results as JSON string
    """
    # Mock search database
    search_db = {
        "python": {
            "title": "Python Programming Language",
            "snippet": "Python is a high-level, interpreted programming language known for its simplicity and readability.",
            "url": "https://python.org"
        },
        "ai": {
            "title": "Artificial Intelligence",
            "snippet": "AI refers to computer systems that can perform tasks requiring human intelligence.",
            "url": "https://en.wikipedia.org/wiki/Artificial_intelligence"
        },
        "langchain": {
            "title": "LangChain Framework",
            "snippet": "LangChain is a framework for building applications with large language models.",
            "url": "https://python.langchain.com"
        }
    }

    query_lower = query.lower()

    # Find matching results
    results = []
    for key, data in search_db.items():
        if key in query_lower:
            results.append(data)

    if results:
        return json.dumps({
            "query": query,
            "results": results
        }, indent=2)
    else:
        return json.dumps({
            "query": query,
            "results": [],
            "message": "No results found. Try: 'python', 'ai', or 'langchain'"
        })


# =============================================================================
# PART 2: Create Tools from Functions
# =============================================================================

class ToolCreator:
    """
    Factory class for creating LangChain tools.

    This demonstrates different ways to create tools.
    """

    @staticmethod
    def create_basic_tools() -> List[Tool]:
        """
        Create basic tools using the Tool class.

        This is the simplest way to create tools.

        Returns:
            List of Tool objects
        """
        print("\n[CREATING TOOLS] Using Tool class...")

        tools = [
            Tool(
                name="get_weather",
                func=get_weather,
                description=(
                    "Get current weather for a city. "
                    "Input should be a city name like 'Tokyo' or 'Paris'. "
                    "Returns weather data including temperature and conditions."
                )
            ),
            Tool(
                name="calculate",
                func=calculate,
                description=(
                    "Calculate a mathematical expression. "
                    "Input should be a math expression like '2+2' or '15*7'. "
                    "Returns the calculation result."
                )
            ),
            Tool(
                name="search_web",
                func=search_web,
                description=(
                    "Search the web for information. "
                    "Input should be a search query. "
                    "Returns relevant search results."
                )
            )
        ]

        print(f"[TOOLS] Created {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description[:60]}...")

        return tools


# =============================================================================
# PART 3: Agent with Tools
# =============================================================================

class ToolCallingAgent:
    """
    Agent that can use multiple tools.

    This demonstrates the ReAct (Reasoning + Acting) pattern:
    1. Reason about what to do
    2. Act by calling a tool
    3. Observe the result
    4. Repeat until done

    Attributes:
        llm: The language model
        tools: Available tools
        agent: The ReAct agent
        agent_executor: Executor that runs the agent
    """

    def __init__(self, model: str = "qwen3:8b"):
        """
        Initialize the tool-calling agent.

        Args:
            model: Ollama model name
        """
        print(f"\n[INIT] Creating ToolCallingAgent with {model}...")

        # Create LLM
        self.llm = OllamaLLM(model=model, temperature=0.0)

        # Create tools
        self.tools = ToolCreator.create_basic_tools()

        # Create agent
        self.agent = self._create_agent()

        # Create executor
        self.agent_executor = self._create_executor()

        print("[INIT] ✅ Agent ready with tools!")

    def _create_agent(self):
        """
        Create ReAct agent.

        ReAct = Reasoning + Acting pattern
        The agent reasons about what to do, acts, observes, and repeats.

        Returns:
            Configured agent
        """
        print("[AGENT] Creating ReAct agent...")

        # Create ReAct prompt
        prompt = PromptTemplate.from_template("""Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}""")

        # Create agent
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        return agent

    def _create_executor(self) -> AgentExecutor:
        """
        Create agent executor.

        The executor handles:
        - Running the agent loop
        - Calling tools
        - Error handling
        - Max iterations

        Returns:
            Configured AgentExecutor
        """
        print("[EXECUTOR] Creating AgentExecutor...")

        executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,  # Show thinking process
            max_iterations=10,  # Prevent infinite loops
            handle_parsing_errors=True,  # Graceful error handling
        )

        return executor

    def ask(self, question: str) -> Dict[str, Any]:
        """
        Ask the agent a question.

        The agent will:
        1. Reason about what tool(s) to use
        2. Call the tool(s)
        3. Use the results to answer

        Args:
            question: User's question

        Returns:
            Dictionary with output and intermediate steps
        """
        print("\n" + "="*70)
        print(f"QUESTION: {question}")
        print("="*70)

        try:
            result = self.agent_executor.invoke({"input": question})

            print("\n" + "="*70)
            print("FINAL ANSWER:")
            print("="*70)
            print(result["output"])
            print("="*70)

            return result

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"\n[ERROR] {error_msg}")
            return {"output": error_msg, "error": True}


# =============================================================================
# PART 4: Demos
# =============================================================================

def demo_single_tool():
    """Demo: Agent uses single tool."""
    print("\n" + "="*70)
    print("DEMO 1: Single Tool Usage")
    print("="*70)

    agent = ToolCallingAgent()

    # Question requiring weather tool
    agent.ask("What's the weather like in Tokyo?")


def demo_multiple_tools():
    """Demo: Agent uses multiple tools."""
    print("\n" + "="*70)
    print("DEMO 2: Multiple Tools Usage")
    print("="*70)

    agent = ToolCallingAgent()

    # Question requiring calculator
    agent.ask("What is 456 multiplied by 789?")

    # Question requiring search
    agent.ask("Search for information about Python programming")


def demo_complex_query():
    """Demo: Complex query requiring reasoning."""
    print("\n" + "="*70)
    print("DEMO 3: Complex Query with Multiple Tools")
    print("="*70)

    agent = ToolCallingAgent()

    # Complex question requiring multiple tools
    agent.ask(
        "What's the weather in Paris? "
        "Also calculate what temperature that is in Fahrenheit (use formula: F = C * 9/5 + 32)"
    )


def demo_no_tool_needed():
    """Demo: Question not requiring tools."""
    print("\n" + "="*70)
    print("DEMO 4: Question NOT Requiring Tools")
    print("="*70)

    agent = ToolCallingAgent()

    # Simple question - no tools needed
    agent.ask("What is the capital of France?")


def demo_error_handling():
    """Demo: Tool error handling."""
    print("\n" + "="*70)
    print("DEMO 5: Error Handling")
    print("="*70)

    agent = ToolCallingAgent()

    # Question with non-existent city
    agent.ask("What's the weather in NonExistentCity?")


def main():
    """Main entry point."""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║         Example 04: Tools Integration                             ║
║                                                                   ║
║  This demonstrates:                                              ║
║  • Creating tools from functions                                 ║
║  • Tool class usage                                              ║
║  • ReAct agent pattern (Reasoning + Acting)                     ║
║  • AgentExecutor for tool orchestration                         ║
║  • Error handling in tools                                       ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Run demos
    demo_single_tool()
    demo_multiple_tools()
    demo_complex_query()
    demo_no_tool_needed()
    demo_error_handling()

    # Summary
    print("\n" + "="*70)
    print("✅ COMPLETE!")
    print("="*70)
    print("\n🎓 What you learned:")
    print("  1. How to create tools from Python functions")
    print("  2. Tool class and StructuredTool patterns")
    print("  3. ReAct agent pattern (Reason → Act → Observe)")
    print("  4. AgentExecutor for running agents")
    print("  5. Error handling in tools")
    print("\n📖 Key Concepts:")
    print("  • Tools = Functions agents can call")
    print("  • ReAct = Reasoning + Acting loop")
    print("  • AgentExecutor = Orchestrates tool calls")
    print("  • Tool descriptions = How LLM knows when to use tools")
    print("\n💡 Production Tips:")
    print("  • Use clear, specific tool descriptions")
    print("  • Add error handling to all tools")
    print("  • Set max_iterations to prevent infinite loops")
    print("  • Use structured tools for type safety")
    print("  • Mock tools for testing, real APIs for production")
    print("\n⚠️  Security Warning:")
    print("  • Never use eval() in production!")
    print("  • Validate all tool inputs")
    print("  • Sandbox tool execution")
    print("  • Rate limit API calls")
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
