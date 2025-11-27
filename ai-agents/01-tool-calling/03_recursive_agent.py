#!/usr/bin/env python3
"""
Example 3: Recursive Agent - The Agent Loop
============================================

This is THE key pattern that transforms an LLM into an AGENT!

The recursive agent can:
- Call multiple tools in sequence
- Use output from one tool as input to another
- Solve complex multi-step tasks autonomously

This is what people mean when they say "agentic behavior"!

Author: Beyhan MEYRALI
"""

import requests
import json
from typing import List, Dict, Any, Optional

# =============================================================================
# CONFIGURATION
# =============================================================================

OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "qwen3:8b"  # Best tool-calling model for local agents (2025)

# =============================================================================
# MOCK TOOLS (Simulated Functions)
# =============================================================================

# These are the "real" functions your agent can call.
# In production, these would call actual APIs, databases, etc.

def get_current_weather(city: str) -> str:
    """
    Mock weather API.
    In production, this would call a real weather service.
    """
    weather_db = {
        "tokyo": {"temp": 25, "condition": "sunny", "humidity": "low"},
        "paris": {"temp": 18, "condition": "cloudy", "humidity": "moderate"},
        "london": {"temp": 15, "condition": "rainy", "humidity": "high"},
        "new york": {"temp": 22, "condition": "clear", "humidity": "moderate"},
        "toronto": {"temp": 16, "condition": "partly cloudy", "humidity": "moderate"},
    }

    city_lower = city.lower()
    if city_lower in weather_db:
        data = weather_db[city_lower]
        return json.dumps({
            "city": city,
            "temperature_celsius": data["temp"],
            "condition": data["condition"],
            "humidity": data["humidity"]
        })
    else:
        return json.dumps({"error": f"Weather data not available for {city}"})


def get_my_manager() -> str:
    """
    Get current user's manager information.
    In production, this would query HR system/database.
    """
    return json.dumps({
        "manager_name": "Alice Johnson",
        "manager_email": "alice.johnson@company.com",
        "manager_city": "Paris",
        "manager_department": "Engineering"
    })


def get_team_members(manager_name: str) -> str:
    """
    Get team members for a given manager.
    In production, this would query HR/org chart database.
    """
    teams = {
        "Alice Johnson": [
            {"name": "Bob Smith", "role": "Senior Engineer", "city": "London"},
            {"name": "Carol Williams", "role": "Engineer", "city": "Paris"},
            {"name": "David Brown", "role": "Junior Engineer", "city": "Paris"}
        ],
        "John Doe": [
            {"name": "Eve Davis", "role": "Designer", "city": "Tokyo"},
            {"name": "Frank Miller", "role": "Product Manager", "city": "New York"}
        ]
    }

    if manager_name in teams:
        return json.dumps({"manager": manager_name, "team": teams[manager_name]})
    else:
        return json.dumps({"error": f"No team found for manager {manager_name}"})


def search_web(query: str) -> str:
    """
    Mock web search.
    In production, this would call a real search API (Google, Bing, etc.)
    """
    # Simulated search results
    results = {
        "python programming": "Python is a high-level, interpreted programming language known for its simplicity and readability.",
        "weather tokyo": "Tokyo weather: Currently 25°C, sunny skies expected throughout the week.",
        "ai agents": "AI agents are autonomous systems that can perceive their environment and take actions to achieve goals.",
    }

    query_lower = query.lower()
    for key in results:
        if key in query_lower:
            return json.dumps({"query": query, "result": results[key]})

    return json.dumps({"query": query, "result": "No relevant results found"})


# =============================================================================
# TOOL DEFINITIONS (Schema for LLM)
# =============================================================================

# This tells the LLM what tools are available and how to use them.
# Think of this as the "API documentation" for the LLM.

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather for a specific city. Returns temperature in Celsius, weather condition, and humidity level.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city (e.g., 'Tokyo', 'Paris', 'London')"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_my_manager",
            "description": "Get information about the current user's manager, including name, email, location, and department. Takes no parameters.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_team_members",
            "description": "Get list of team members for a specific manager. Returns array of team members with their roles and locations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "manager_name": {
                        "type": "string",
                        "description": "Full name of the manager (e.g., 'Alice Johnson')"
                    }
                },
                "required": ["manager_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information on any topic. Returns relevant search results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query (e.g., 'Python programming', 'weather in Tokyo')"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# Map function names to actual Python functions
AVAILABLE_FUNCTIONS = {
    "get_current_weather": get_current_weather,
    "get_my_manager": get_my_manager,
    "get_team_members": get_team_members,
    "search_web": search_web
}


# =============================================================================
# TOOL EXECUTION
# =============================================================================

def execute_tool(function_name: str, arguments: Dict[str, Any]) -> str:
    """
    Execute a tool function and return the result.

    This is where the actual tool execution happens.
    The LLM just says "call this function" - we actually run it.

    Args:
        function_name: Name of the function to call
        arguments: Dictionary of arguments to pass

    Returns:
        JSON string with function result or error
    """

    print(f"  [EXECUTE] {function_name}({arguments})")

    # Check if function exists
    if function_name not in AVAILABLE_FUNCTIONS:
        error_result = json.dumps({
            "error": f"Unknown function: {function_name}",
            "available_functions": list(AVAILABLE_FUNCTIONS.keys())
        })
        print(f"  [ERROR] {error_result}")
        return error_result

    try:
        # Get the actual Python function
        function = AVAILABLE_FUNCTIONS[function_name]

        # Call it with the arguments
        result = function(**arguments)

        print(f"  [RESULT] {result}")
        return result

    except Exception as e:
        # Handle any errors during execution
        error_result = json.dumps({"error": f"Error executing {function_name}: {str(e)}"})
        print(f"  [ERROR] {error_result}")
        return error_result


# =============================================================================
# THE RECURSIVE AGENT LOOP
# =============================================================================

def recursive_agent(user_message: str, max_iterations: int = 10, verbose: bool = True) -> str:
    """
    The recursive agent loop - THIS IS THE KEY PATTERN!

    This function:
    1. Sends user message to LLM with available tools
    2. If LLM wants to use tools, executes them
    3. Sends tool results back to LLM
    4. Repeats until LLM has final answer (or max iterations)

    This is what transforms an LLM into an autonomous agent!

    Args:
        user_message: The user's question/request
        max_iterations: Maximum number of LLM calls (prevents infinite loops)
        verbose: Print detailed execution logs

    Returns:
        Final answer from the agent
    """

    if verbose:
        print("\n" + "="*70)
        print("RECURSIVE AGENT EXECUTION")
        print("="*70)
        print(f"[USER] {user_message}")
        print("-"*70)

    # Initialize conversation with user message
    messages = [
        {"role": "user", "content": user_message}
    ]

    url = f"{OLLAMA_BASE_URL}/api/chat"

    # THE AGENT LOOP
    for iteration in range(max_iterations):
        if verbose:
            print(f"\n[ITERATION {iteration + 1}]")

        # Prepare request payload
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "tools": TOOLS,
            "stream": False
        }

        try:
            # Call LLM
            if verbose:
                print("  [LLM] Thinking...")

            response = requests.post(url, json=payload, timeout=60)

            if response.status_code != 200:
                return f"Error: LLM API returned {response.status_code}"

            response_data = response.json()
            message = response_data.get("message", {})

            # Add LLM's response to conversation
            messages.append(message)

            # Check if LLM wants to use tools
            tool_calls = message.get("tool_calls", [])

            if tool_calls:
                # LLM wants to use one or more tools
                if verbose:
                    print(f"  [LLM] Wants to use {len(tool_calls)} tool(s)")

                # Execute each tool the LLM requested
                for tool_call in tool_calls:
                    function_data = tool_call.get("function", {})
                    function_name = function_data.get("name")
                    arguments = function_data.get("arguments", {})

                    # Execute the tool
                    result = execute_tool(function_name, arguments)

                    # Add tool result to conversation
                    # The LLM will see this result in the next iteration
                    messages.append({
                        "role": "tool",
                        "content": result
                    })

                # Continue loop - LLM will process tool results

            else:
                # No tool calls - LLM has reached final answer
                final_answer = message.get("content", "")

                if verbose:
                    print(f"\n[FINAL ANSWER after {iteration + 1} iteration(s)]")
                    print("-"*70)
                    print(final_answer)
                    print("="*70)

                return final_answer

        except requests.exceptions.RequestException as e:
            return f"Error: Connection to LLM failed: {str(e)}"

    # Max iterations reached without final answer
    if verbose:
        print(f"\n[WARNING] Max iterations ({max_iterations}) reached!")

    return "Task too complex - exceeded maximum iterations"


# =============================================================================
# DEMONSTRATION: SIMPLE VS COMPLEX QUERIES
# =============================================================================

def run_demonstrations():
    """
    Run example queries showing increasing complexity.
    Watch how the agent chains tools together!
    """

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║              Recursive Agent - Multi-Step Tool Calling            ║
║                                                                   ║
║  Watch how the agent autonomously chains multiple tool calls!    ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Example 1: Simple single tool call
    print("\n\n" + "#"*70)
    print("# EXAMPLE 1: Simple Query (1 tool call)")
    print("#"*70)
    recursive_agent("What's the weather in Tokyo?")

    # Example 2: Multi-step query
    print("\n\n" + "#"*70)
    print("# EXAMPLE 2: Multi-Step Query (2 tool calls)")
    print("#"*70)
    recursive_agent("What's the weather in my manager's city?")
    # This requires:
    # Step 1: get_my_manager() to find out manager's city
    # Step 2: get_current_weather(city) to get weather for that city

    # Example 3: Complex orchestration
    print("\n\n" + "#"*70)
    print("# EXAMPLE 3: Complex Query (3+ tool calls)")
    print("#"*70)
    recursive_agent("Get my manager's name, then list their team members, and tell me the weather in each team member's city")
    # This requires:
    # Step 1: get_my_manager() → Get manager name
    # Step 2: get_team_members(manager_name) → Get team list
    # Step 3: get_current_weather(city1) → Weather for member 1
    # Step 4: get_current_weather(city2) → Weather for member 2
    # Step 5: get_current_weather(city3) → Weather for member 3

    # Example 4: Query that doesn't need tools
    print("\n\n" + "#"*70)
    print("# EXAMPLE 4: No Tools Needed")
    print("#"*70)
    recursive_agent("What is 2+2?")
    # LLM can answer directly without calling any tools


# =============================================================================
# INTERACTIVE MODE
# =============================================================================

def interactive_mode():
    """
    Interactive agent mode - ask your own questions!
    """

    print("\n" + "="*70)
    print("INTERACTIVE AGENT MODE")
    print("="*70)
    print("Available tools:")
    for tool in TOOLS:
        func = tool["function"]
        print(f"  - {func['name']}: {func['description']}")
    print("\nCommands: 'quit', 'exit', 'help'")
    print("="*70)

    while True:
        user_input = input("\n[YOU] ").strip()

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("[INFO] Goodbye!")
            break

        if user_input.lower() == 'help':
            print("\nAvailable tools:")
            for tool in TOOLS:
                func = tool["function"]
                print(f"  - {func['name']}: {func['description']}")
            continue

        if not user_input:
            continue

        # Run the recursive agent
        recursive_agent(user_input, verbose=True)


# =============================================================================
# MAIN PROGRAM
# =============================================================================

def main():
    """
    Main entry point
    """

    # Check Ollama connection
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code != 200:
            print("[ERROR] Ollama is not responding correctly")
            exit(1)
    except requests.exceptions.RequestException:
        print("[ERROR] Cannot connect to Ollama!")
        print("[HINT] Make sure Ollama is running: ollama serve")
        exit(1)

    # Run demonstrations
    run_demonstrations()

    # Interactive mode
    print("\n\n")
    try:
        interactive_mode()
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user. Goodbye!")


if __name__ == "__main__":
    main()
