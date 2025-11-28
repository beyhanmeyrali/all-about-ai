#!/usr/bin/env python3
"""
Example 3: Tools + LangGraph - Agent Orchestration
===================================================

This combines section 01 (Tool Calling) with LangGraph for
professional agent orchestration.

What you'll learn:
- Using tools within LangGraph nodes
- Recursive tool calling in a structured workflow
- Agent orchestration (multiple tools, multiple steps)
- Error handling and retry logic
- Building production-ready agents

This is the "ADVANCED" level - combining everything!

DEBUGGING TIPS:
--------------
1. Watch tool execution:
   - See which tools get called
   - Check tool results
   - Verify LLM uses results correctly

2. If tools don't get called:
   - Check tool schema
   - Verify LLM supports tool calling
   - Print the LLM response

Author: Beyhan MEYRALI
"""

from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import StateGraph, END
import requests
import json
import operator

# =============================================================================
# STEP 1: Define Tools (from Section 01)
# =============================================================================

def get_weather(city: str) -> str:
    """
    Get weather for a city.

    This is a TOOL that the agent can call.
    """
    weather_db = {
        "tokyo": {"temp": 25, "condition": "sunny"},
        "paris": {"temp": 18, "condition": "cloudy"},
        "london": {"temp": 15, "condition": "rainy"},
        "new york": {"temp": 20, "condition": "clear"},
    }

    city_lower = city.lower()
    if city_lower in weather_db:
        data = weather_db[city_lower]
        return json.dumps({
            "city": city,
            "temperature_celsius": data["temp"],
            "condition": data["condition"]
        })
    else:
        return json.dumps({"error": f"No weather data for {city}"})


def search_web(query: str) -> str:
    """
    Simulate web search.

    This is a TOOL that the agent can call.
    """
    # Mock search results
    search_db = {
        "python": "Python is a high-level programming language created by Guido van Rossum...",
        "ai": "Artificial Intelligence (AI) refers to computer systems that can perform tasks that typically require human intelligence...",
        "langgraph": "LangGraph is a library for building stateful multi-actor applications with LLMs...",
    }

    query_lower = query.lower()
    for key in search_db:
        if key in query_lower:
            return json.dumps({
                "query": query,
                "result": search_db[key]
            })

    return json.dumps({
        "query": query,
        "result": "No results found. Try searching for 'python', 'ai', or 'langgraph'."
    })


# Define tool schemas for LLM
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city. Returns temperature in Celsius and weather condition.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city name (e.g., 'Tokyo', 'Paris')"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information on a topic.",
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

# Map function names to actual functions
AVAILABLE_TOOLS = {
    "get_weather": get_weather,
    "search_web": search_web,
}


# =============================================================================
# STEP 2: Define State
# =============================================================================

class AgentState(TypedDict):
    """
    State for tool-calling agent.

    This tracks the conversation and tool usage.
    """
    messages: Annotated[List[Dict], operator.add]  # Conversation history
    question: str              # Original question
    final_answer: str          # Final answer
    tools_used: List[str]      # Track which tools were called
    iteration: int             # Track iterations (prevent infinite loops)


# =============================================================================
# STEP 3: Define Nodes
# =============================================================================

def agent_node(state: AgentState) -> dict:
    """
    Agent node that can call tools.

    This is the MAIN node that:
    1. Calls LLM with tools available
    2. Executes any tools the LLM wants to use
    3. Continues until LLM has final answer
    """

    print(f"\n[AGENT] Iteration {state['iteration']}")

    messages = state.get("messages", [])

    # Add initial question if no messages yet
    if not messages:
        messages = [{"role": "user", "content": state["question"]}]

    try:
        # Call LLM with tools
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "qwen3:8b",
                "messages": messages,
                "tools": TOOLS,
                "stream": False
            },
            timeout=60
        )

        if response.status_code != 200:
            return {
                "final_answer": f"API Error: {response.status_code}",
                "iteration": state["iteration"] + 1
            }

        response_data = response.json()
        llm_message = response_data.get("message", {})

        # Check if LLM wants to call tools
        tool_calls = llm_message.get("tool_calls", [])

        if tool_calls:
            print(f"[AGENT] LLM wants to call {len(tool_calls)} tool(s)")

            # Execute each tool
            new_messages = [llm_message]  # Add LLM's message with tool calls

            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                arguments_raw = tool_call["function"]["arguments"]

                # Parse arguments if it's a string
                if isinstance(arguments_raw, str):
                    arguments = json.loads(arguments_raw)
                else:
                    arguments = arguments_raw

                print(f"[TOOL] Calling {function_name}({arguments})")

                # Execute the tool
                if function_name in AVAILABLE_TOOLS:
                    result = AVAILABLE_TOOLS[function_name](**arguments)
                    print(f"[TOOL] Result: {result}")

                    # Add tool result to messages
                    new_messages.append({
                        "role": "tool",
                        "content": result
                    })

                    # Track tool usage
                    tools_used = state.get("tools_used", [])
                    tools_used.append(function_name)
                else:
                    new_messages.append({
                        "role": "tool",
                        "content": json.dumps({"error": f"Unknown tool: {function_name}"})
                    })

            return {
                "messages": new_messages,
                "tools_used": tools_used if 'tools_used' in locals() else state.get("tools_used", []),
                "iteration": state["iteration"] + 1
            }

        else:
            # No tool calls - LLM has final answer
            final_answer = llm_message.get("content", "No response")
            print(f"[AGENT] Final answer: {final_answer[:80]}...")

            return {
                "messages": [llm_message],
                "final_answer": final_answer,
                "iteration": state["iteration"] + 1
            }

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"[ERROR] {error_msg}")
        return {
            "final_answer": error_msg,
            "iteration": state["iteration"] + 1
        }


def should_continue(state: AgentState) -> str:
    """
    Router function: Should we continue or end?

    This prevents infinite loops by:
    1. Ending if we have a final answer
    2. Ending if we hit max iterations
    """

    # Check for final answer
    if state.get("final_answer"):
        print("[ROUTER] Have final answer → END")
        return "end"

    # Check iteration limit
    if state["iteration"] >= 10:
        print("[ROUTER] Max iterations reached → END")
        return "end"

    # Continue looping
    print("[ROUTER] Need more processing → CONTINUE")
    return "continue"


# =============================================================================
# STEP 4: Build Graph
# =============================================================================

def create_agent_graph():
    """
    Build the tool-calling agent graph.

    Flow:
    START → agent → [continue back to agent OR end] → END
             ↑_______|

    The agent node can loop multiple times if tools need to be called!
    """

    print("\n[GRAPH] Building tool-calling agent...")

    workflow = StateGraph(AgentState)

    # Add agent node
    workflow.add_node("agent", agent_node)

    # Set entry point
    workflow.set_entry_point("agent")

    # Add conditional edge: loop or end?
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "agent",  # Loop back!
            "end": END
        }
    )

    app = workflow.compile()

    print("[GRAPH] Agent graph built!")
    print("[GRAPH] Flow: agent → [loop OR end]")

    return app


# =============================================================================
# STEP 5: Run Examples
# =============================================================================

def run_agent(question: str):
    """Run the agent with a question."""

    print("\n" + "="*70)
    print(f"QUESTION: {question}")
    print("="*70)

    app = create_agent_graph()

    result = app.invoke({
        "question": question,
        "messages": [],
        "final_answer": "",
        "tools_used": [],
        "iteration": 0
    })

    print("\n" + "="*70)
    print("FINAL ANSWER:")
    print("="*70)
    print(result.get("final_answer", "No answer"))
    print("\n" + "-"*70)
    print(f"Tools used: {', '.join(result.get('tools_used', [])) or 'None'}")
    print(f"Iterations: {result['iteration']}")
    print("="*70)

    return result


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point with test cases."""

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║       Example 3: Tools + LangGraph (Agent Orchestration)          ║
║                                                                   ║
║  This demonstrates:                                              ║
║  • Tool calling within LangGraph                                 ║
║  • Recursive tool execution                                      ║
║  • Agent orchestration                                           ║
║  • Professional agent patterns                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Test 1: Single tool call
    print("\n[TEST 1] Single Tool Call")
    run_agent("What's the weather in Tokyo?")

    # Test 2: Multiple tool calls
    print("\n\n[TEST 2] Multiple Tool Calls")
    run_agent("What's the weather in Paris and London?")

    # Test 3: Web search
    print("\n\n[TEST 3] Web Search Tool")
    run_agent("Search for information about Python programming")

    # Test 4: No tools needed
    print("\n\n[TEST 4] No Tools Needed")
    run_agent("What is 2+2?")

    # Test 5: Complex multi-tool query
    print("\n\n[TEST 5] Complex Multi-Tool Query")
    run_agent("Search for LangGraph and tell me the weather in New York")

    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETE!")
    print("="*70)
    print("\nKey Concepts:")
    print("  ✅ Tools integrated into LangGraph workflow")
    print("  ✅ Recursive tool calling with loop detection")
    print("  ✅ Agent orchestration pattern")
    print("  ✅ Professional error handling")
    print("\nThis is production-ready agent architecture!")
    print("="*70)


if __name__ == "__main__":
    # Check Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("[WARNING] Ollama returned unexpected status")
    except requests.exceptions.RequestException:
        print("[ERROR] Cannot connect to Ollama!")
        exit(1)

    main()
