#!/usr/bin/env python3
"""
Example 1: Simple LangGraph Agent
==================================

This is the SIMPLEST possible LangGraph agent.
It shows how to build a workflow with nodes and edges.

What you'll learn:
- How to define state
- How to create nodes (functions)
- How to build a graph
- How to run the graph

DEBUGGING TIPS:
--------------
1. If you get "Module not found: langgraph":
   pip install -r requirements.txt

2. If Ollama fails:
   - Make sure Ollama is running: ollama serve
   - Check model exists: ollama list

3. To debug:
   - Add print() statements in nodes
   - Check state at each step

Author: Beyhan MEYRALI
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END
import requests

# =============================================================================
# STEP 1: Define State
# =============================================================================

class State(TypedDict):
    """
    State that flows through the graph.

    Think of this as the "memory" that gets passed between nodes.
    Each node can read from and update this state.
    """
    question: str  # User's question
    answer: str    # LLM's answer


# =============================================================================
# STEP 2: Define Nodes (Functions)
# =============================================================================

def ask_llm_node(state: State) -> dict:
    """
    Node that calls Ollama LLM.

    A node is just a Python function that:
    - Takes current state as input
    - Does some work
    - Returns updates to state

    Args:
        state: Current state containing question

    Returns:
        Dictionary with answer to add to state
    """

    print(f"\n[NODE] Calling LLM with question: {state['question']}")

    try:
        # Call Ollama API
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "qwen3:8b",
                "messages": [
                    {"role": "user", "content": state["question"]}
                ],
                "stream": False
            },
            timeout=60
        )

        if response.status_code == 200:
            answer = response.json()["message"]["content"]
            print(f"[NODE] Got answer: {answer[:80]}...")
            return {"answer": answer}
        else:
            error = f"API Error: {response.status_code}"
            print(f"[ERROR] {error}")
            return {"answer": error}

    except Exception as e:
        error = f"Error: {str(e)}"
        print(f"[ERROR] {error}")
        return {"answer": error}


# =============================================================================
# STEP 3: Build the Graph
# =============================================================================

def create_graph():
    """
    Build the LangGraph workflow.

    This creates a simple graph:
    START → ask_llm_node → END

    Returns:
        Compiled graph ready to run
    """

    print("\n[GRAPH] Building workflow...")

    # Create graph with our state type
    workflow = StateGraph(State)

    # Add our LLM node
    workflow.add_node("ask_llm", ask_llm_node)

    # Define the flow
    workflow.set_entry_point("ask_llm")  # Start here
    workflow.add_edge("ask_llm", END)     # Then end

    # Compile into runnable app
    app = workflow.compile()

    print("[GRAPH] Workflow built: START → ask_llm → END")

    return app


# =============================================================================
# STEP 4: Run the Graph
# =============================================================================

def run_question(question: str):
    """
    Run the graph with a question.

    Args:
        question: Question to ask
    """

    print("\n" + "="*70)
    print(f"QUESTION: {question}")
    print("="*70)

    # Create graph
    app = create_graph()

    # Run with initial state
    result = app.invoke({"question": question, "answer": ""})

    # Print result
    print("\n" + "="*70)
    print("ANSWER:")
    print("="*70)
    print(result["answer"])
    print("="*70)

    return result


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point."""

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║         Example 1: Simple LangGraph Agent                         ║
║                                                                   ║
║  This demonstrates:                                              ║
║  • Defining state (TypedDict)                                   ║
║  • Creating nodes (functions)                                    ║
║  • Building graphs (workflow)                                    ║
║  • Running graphs (invoke)                                       ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Test 1: Simple question
    print("\n[TEST 1] Simple Question")
    run_question("What is the capital of France?")

    # Test 2: Math question
    print("\n\n[TEST 2] Math Question")
    run_question("What is 15 * 7?")

    # Test 3: Reasoning
    print("\n\n[TEST 3] Reasoning Question")
    run_question("If I have 3 apples and buy 2 more, how many do I have?")

    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETE!")
    print("="*70)
    print("\nKey Concepts:")
    print("  • State = Data flowing through graph")
    print("  • Node = Function that processes state")
    print("  • Edge = Connection between nodes")
    print("  • Graph = Complete workflow")
    print("\nNext: Check out 02_conditional_workflow.py for branching logic")
    print("="*70)


if __name__ == "__main__":
    # Check Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("[WARNING] Ollama returned unexpected status")
    except requests.exceptions.RequestException:
        print("[ERROR] Cannot connect to Ollama!")
        print("  1. Install: https://ollama.ai")
        print("  2. Run: ollama serve")
        print("  3. Pull model: ollama pull qwen3:8b")
        exit(1)

    main()
