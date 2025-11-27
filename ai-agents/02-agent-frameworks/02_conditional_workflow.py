#!/usr/bin/env python3
"""
Example 2: Conditional Workflow - If/Else Logic in LangGraph
==============================================================

This demonstrates CONDITIONAL routing - how to make decisions
in your workflow based on the data.

What you'll learn:
- Conditional edges (if/else in graphs)
- Router functions (decision logic)
- Multiple paths through a workflow
- When different questions need different handling

DEBUGGING TIPS:
--------------
1. Watch which path is taken:
   - Add print() in router function
   - See which node gets called

2. If routing seems wrong:
   - Check your router function logic
   - Print the state it receives
   - Verify return values match node names

Author: Beyhan MEYRALI
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
import requests
import json

# =============================================================================
# STEP 1: Define State
# =============================================================================

class State(TypedDict):
    """
    State for conditional workflow.

    We'll route questions to different nodes based on content.
    """
    question: str          # User's question
    answer: str            # Final answer
    route_taken: str       # Which path was taken (for debugging)


# =============================================================================
# STEP 2: Define Specialized Nodes
# =============================================================================

def weather_node(state: State) -> dict:
    """
    Node that handles weather questions using a tool.

    This simulates calling a weather API.
    """

    print(f"\n[WEATHER NODE] Handling weather question...")

    # Extract city from question (simple approach)
    question = state["question"].lower()

    # Mock weather data
    weather_db = {
        "tokyo": "25°C, sunny",
        "paris": "18°C, cloudy",
        "london": "15°C, rainy",
        "new york": "20°C, clear",
    }

    # Try to find city in question
    city_found = None
    for city in weather_db.keys():
        if city in question:
            city_found = city
            break

    if city_found:
        weather = weather_db[city_found]
        answer = f"The weather in {city_found.title()} is {weather}."
    else:
        answer = "I can provide weather for: Tokyo, Paris, London, or New York."

    print(f"[WEATHER NODE] Answer: {answer}")

    return {
        "answer": answer,
        "route_taken": "weather"
    }


def math_node(state: State) -> dict:
    """
    Node that handles math questions using LLM.

    For math, we give the LLM specific instructions.
    """

    print(f"\n[MATH NODE] Handling math question...")

    # Add math-specific system prompt
    messages = [
        {
            "role": "system",
            "content": "You are a math expert. Provide clear, step-by-step solutions."
        },
        {
            "role": "user",
            "content": state["question"]
        }
    ]

    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "qwen3:8b",
                "messages": messages,
                "stream": False
            },
            timeout=60
        )

        if response.status_code == 200:
            answer = response.json()["message"]["content"]
            print(f"[MATH NODE] Got answer (truncated): {answer[:80]}...")
        else:
            answer = f"Math API error: {response.status_code}"

    except Exception as e:
        answer = f"Math error: {str(e)}"

    return {
        "answer": answer,
        "route_taken": "math"
    }


def general_node(state: State) -> dict:
    """
    Node that handles general questions using LLM.

    This is the default path for any question that doesn't
    match weather or math.
    """

    print(f"\n[GENERAL NODE] Handling general question...")

    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "qwen3:8b",
                "messages": [{"role": "user", "content": state["question"]}],
                "stream": False
            },
            timeout=60
        )

        if response.status_code == 200:
            answer = response.json()["message"]["content"]
            print(f"[GENERAL NODE] Got answer (truncated): {answer[:80]}...")
        else:
            answer = f"API error: {response.status_code}"

    except Exception as e:
        answer = f"Error: {str(e)}"

    return {
        "answer": answer,
        "route_taken": "general"
    }


# =============================================================================
# STEP 3: Define Router Function (THE KEY PART!)
# =============================================================================

def route_question(state: State) -> Literal["weather", "math", "general"]:
    """
    Router function that decides which node to call.

    This is the "if/else" logic of your graph!

    Args:
        state: Current state with the question

    Returns:
        Name of the node to call next

    How it works:
    - Look at the question
    - Decide which specialized node should handle it
    - Return the node name

    The graph will then call that node!
    """

    question = state["question"].lower()

    print(f"\n[ROUTER] Analyzing question: {state['question']}")

    # Check for weather keywords
    if any(word in question for word in ["weather", "temperature", "forecast", "climate"]):
        print("[ROUTER] Detected WEATHER question → routing to weather_node")
        return "weather"

    # Check for math keywords
    elif any(word in question for word in ["calculate", "multiply", "divide", "plus", "minus", "*", "+", "-", "/", "="]):
        print("[ROUTER] Detected MATH question → routing to math_node")
        return "math"

    # Default to general
    else:
        print("[ROUTER] General question → routing to general_node")
        return "general"


# =============================================================================
# STEP 4: Build the Graph with Conditional Logic
# =============================================================================

def create_graph():
    """
    Build a graph with conditional routing.

    The workflow looks like this:

           START
             ↓
          ROUTER
           / | \
          /  |  \
    weather math general
          \  |  /
           \ | /
            END

    The router function decides which path to take!
    """

    print("\n[GRAPH] Building conditional workflow...")

    # Create graph
    workflow = StateGraph(State)

    # Add all our nodes
    workflow.add_node("weather", weather_node)
    workflow.add_node("math", math_node)
    workflow.add_node("general", general_node)

    # Add a dummy router node that just passes through
    def router_node(state: State) -> dict:
        # Must return at least one state update
        return {"route_taken": "routing..."}

    workflow.add_node("router", router_node)

    # Set entry point (start with router node)
    workflow.set_entry_point("router")

    # Add the router as a conditional edge
    # This is the KEY difference from simple graphs!
    workflow.add_conditional_edges(
        "router",  # Start from router node
        route_question,  # Function that decides which node
        {
            # Map return values to actual nodes
            "weather": "weather",
            "math": "math",
            "general": "general",
        }
    )

    # All paths lead to END
    workflow.add_edge("weather", END)
    workflow.add_edge("math", END)
    workflow.add_edge("general", END)

    # Compile
    app = workflow.compile()

    print("[GRAPH] Conditional workflow built!")
    print("[GRAPH] Routes: router → [weather | math | general] → END")

    return app


# =============================================================================
# STEP 5: Run Examples
# =============================================================================

def run_question(question: str):
    """Run a question through the conditional workflow."""

    print("\n" + "="*70)
    print(f"QUESTION: {question}")
    print("="*70)

    # Create graph
    app = create_graph()

    # Run
    result = app.invoke({
        "question": question,
        "answer": "",
        "route_taken": ""
    })

    # Show results
    print("\n" + "="*70)
    print(f"ROUTE TAKEN: {result['route_taken'].upper()}")
    print("="*70)
    print("ANSWER:")
    print(result["answer"])
    print("="*70)

    return result


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point with various test cases."""

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║      Example 2: Conditional Workflow (If/Else Logic)              ║
║                                                                   ║
║  This demonstrates:                                              ║
║  • Conditional edges (branching)                                 ║
║  • Router functions (decision logic)                             ║
║  • Multiple specialized nodes                                    ║
║  • Dynamic workflow paths                                        ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Test 1: Weather question
    print("\n[TEST 1] Weather Question")
    run_question("What's the weather like in Tokyo?")

    # Test 2: Math question
    print("\n\n[TEST 2] Math Question")
    run_question("Calculate 25 * 4")

    # Test 3: General question
    print("\n\n[TEST 3] General Question")
    run_question("Who was the first person on the moon?")

    # Test 4: Another weather
    print("\n\n[TEST 4] Another Weather Question")
    run_question("How's the climate in Paris today?")

    # Test 5: Complex math
    print("\n\n[TEST 5] Complex Math")
    run_question("If I have 10 apples and give away 3, then buy 5 more, how many do I have?")

    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETE!")
    print("="*70)
    print("\nKey Concepts Demonstrated:")
    print("  • Conditional routing based on question content")
    print("  • Different specialized nodes for different tasks")
    print("  • Router function as decision maker")
    print("  • Dynamic workflow paths")
    print("\nNext Steps:")
    print("  → Try modifying the router logic")
    print("  → Add new specialized nodes (e.g., history, science)")
    print("  → Combine this with tool calling from section 01")
    print("="*70)


if __name__ == "__main__":
    # Check Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("[WARNING] Ollama returned unexpected status")
    except requests.exceptions.RequestException:
        print("[ERROR] Cannot connect to Ollama!")
        print("  Make sure Ollama is running: ollama serve")
        exit(1)

    main()
