# 02 - Agent Frameworks: LangGraph Basics 🕸️

> Learn how to build structured agent workflows using LangGraph

---

## 🎯 Learning Objectives

By the end of this section, you will understand:
- ✅ What LangGraph is and why it's useful
- ✅ State management in agent workflows
- ✅ Creating nodes (functions) and edges (connections)
- ✅ Building conditional workflows
- ✅ When to use frameworks vs raw tool calling

**Time Required:** 4-5 hours

---

## 🤔 Why Use LangGraph?

### The Problem with Raw Code

From section 01, you learned recursive tool calling:

```python
# This works for simple cases
while True:
    response = llm.chat(messages, tools=tools)
    if response.tool_calls:
        execute_tools(response.tool_calls)
        continue
    else:
        break
```

**But what about:**
- 🔄 Complex workflows with conditional branching?
- 💾 Persistent state across conversations?
- 🐛 Debugging multi-step executions?
- 📊 Visualizing agent logic?

**This is where LangGraph helps!**

---

## 🌟 What is LangGraph?

**LangGraph** is a framework for building stateful, multi-step agent workflows.

**Key Concepts:**

1. **State** = Data flowing through your workflow
2. **Nodes** = Functions that process state
3. **Edges** = Connections between nodes
4. **Graph** = Complete workflow from start to end

**Think of it like:**
- State = Variables in your program
- Nodes = Functions you write
- Edges = Function call order
- Graph = Your complete program

---

## 📚 What This Section Covers

### Files in This Directory

```
02-agent-frameworks/
├── README.md                          ← You are here
├── requirements.txt                   ← Dependencies
├── 01_simple_langgraph.py            ← Basic workflow
├── 02_conditional_workflow.py        ← If/else logic
└── 03_tools_with_langgraph.py        ← Combining with tools
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd 02-agent-frameworks
pip install -r requirements.txt
```

### 2. Verify Ollama

```bash
ollama list  # Should see qwen3:8b
```

### 3. Run First Example

```bash
python 01_simple_langgraph.py
```

---

## 📖 LangGraph Fundamentals

### Core Concept 1: State

State is the data that flows through your workflow:

```python
from typing import TypedDict

class AgentState(TypedDict):
    """Data that flows through the graph"""
    question: str    # User's question
    answer: str      # LLM's answer
    tools_used: list # Tools called so far
```

**Think of state like:**
- Global variables that all functions can access
- But safer and more organized!

### Core Concept 2: Nodes

Nodes are just Python functions that process state:

```python
def ask_llm(state: AgentState) -> dict:
    """Node that calls LLM"""
    # 1. Read from state
    question = state["question"]

    # 2. Do work (call LLM)
    answer = call_ollama(question)

    # 3. Return updates to state
    return {"answer": answer}
```

**Node Rules:**
- Takes `state` as input
- Returns `dict` with updates
- Can do anything: LLM calls, tool calls, database queries, etc.

### Core Concept 3: Edges

Edges connect nodes together:

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("ask_llm", ask_llm)
workflow.add_node("formatter", format_output)

# Connect them with edges
workflow.set_entry_point("ask_llm")  # Start here
workflow.add_edge("ask_llm", "formatter")  # Then go here
workflow.add_edge("formatter", END)  # Then end
```

**Flow:**
```
START → ask_llm → formatter → END
```

### Core Concept 4: Graph

The graph is your complete workflow:

```python
# Build graph
workflow = StateGraph(AgentState)
workflow.add_node("node1", func1)
workflow.add_node("node2", func2)
workflow.add_edge("node1", "node2")
workflow.add_edge("node2", END)

# Compile into runnable app
app = workflow.compile()

# Run it!
result = app.invoke({"question": "What is 2+2?"})
```

---

## 🔄 Simple Example Walkthrough

Here's the complete basic example from `01_simple_langgraph.py`:

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END
import requests

# 1. Define State
class State(TypedDict):
    question: str
    answer: str

# 2. Define Node
def ask_llm(state: State) -> dict:
    """Call Ollama LLM"""
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "qwen3:8b",
            "messages": [{"role": "user", "content": state["question"]}],
            "stream": False
        }
    )
    answer = response.json()["message"]["content"]
    return {"answer": answer}

# 3. Build Graph
workflow = StateGraph(State)
workflow.add_node("llm", ask_llm)
workflow.set_entry_point("llm")
workflow.add_edge("llm", END)
app = workflow.compile()

# 4. Run Graph
result = app.invoke({"question": "What is the capital of France?"})
print(result["answer"])
```

**Output:**
```
The capital of France is Paris.
```

---

## 🎯 Conditional Workflows

LangGraph shines when you need branching logic:

```python
def router(state: State) -> str:
    """Decide which path to take"""
    if "weather" in state["question"].lower():
        return "weather_node"
    elif "math" in state["question"].lower():
        return "math_node"
    else:
        return "general_node"

# Add conditional edge
workflow.add_conditional_edges(
    "router",
    router,  # Function that decides
    {
        "weather_node": "weather_node",
        "math_node": "math_node",
        "general_node": "general_node"
    }
)
```

**Flow:**
```
START → router → [weather_node OR math_node OR general_node] → END
                      ↓
             (decided by router function)
```

---

## 🔧 Combining with Tool Calling

You can use LangGraph with the tool calling from section 01:

```python
def tool_calling_node(state: State) -> dict:
    """Node that can call tools"""
    # Call LLM with tools
    response = llm.chat(state["messages"], tools=tools)

    if response.tool_calls:
        # Execute tools
        for tool_call in response.tool_calls:
            result = execute_tool(tool_call)
            state["messages"].append(tool_result)

    return {"messages": state["messages"]}
```

See `03_tools_with_langgraph.py` for complete example.

---

## 📊 When to Use What?

### Use Raw Tool Calling (Section 01):
✅ Simple, linear tasks
✅ Quick prototypes
✅ Learning fundamentals
✅ Single-agent workflows

### Use LangGraph:
✅ Complex workflows with branching
✅ Multi-step processes
✅ Need to visualize logic
✅ Want better debugging
✅ Planning to scale complexity

---

## 🐛 Debugging Tips

### Common Issues

**1. "InvalidUpdateError: Expected node to update..."**
```python
# Problem: Node returns empty dict
def my_node(state: State) -> dict:
    return {}  # ❌ Wrong!

# Solution: Return at least one state update
def my_node(state: State) -> dict:
    return {"answer": "some value"}  # ✅ Correct
```

**2. "Module not found: langgraph"**
```bash
# Solution:
pip install -r requirements.txt
```

**3. Graph seems stuck/slow
```python
# Add debug prints in nodes
def my_node(state: State) -> dict:
    print(f"[DEBUG] Node called with: {state}")
    # ... do work ...
    print(f"[DEBUG] Node returning: {result}")
    return result
```

**4. State not updating
```python
# Make sure you return a dict with the right keys
class State(TypedDict):
    question: str
    answer: str

# This works:
return {"answer": "hello"}  # ✅

# This doesn't:
return {"response": "hello"}  # ❌ Wrong key!
```

---

## 🎯 Key Takeaways

### What You Should Understand:

1. **LangGraph = Structured Workflows**
   - Not magic, just organized code
   - State flows through nodes
   - Edges control the flow

2. **State is Central**
   - Define it with TypedDict
   - Nodes read and update it
   - It's your workflow's memory

3. **Nodes Are Just Functions**
   - Take state, return updates
   - Can do anything inside
   - Keep them focused on one task

4. **Use It When Complexity Grows**
   - Simple task? → Raw code is fine
   - Complex workflow? → LangGraph helps
   - It's a tool, not a requirement

---

## 🚀 Next Steps

### You're Ready For:
✅ [03-embeddings-rag](../03-embeddings-rag) - Teaching agents about your data

### Practice Exercises:

1. **Modify 01_simple_langgraph.py**
   - Add a second node that formats the answer
   - Add error handling node

2. **Build a routing workflow**
   - Route questions to different specialized nodes
   - Math questions → calculator node
   - Weather questions → weather node
   - General questions → LLM node

3. **Combine with section 01**
   - Take the recursive agent from section 01
   - Rebuild it using LangGraph
   - Compare complexity

---

## 📚 Additional Resources

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [LangGraph GitHub Examples](https://github.com/langchain-ai/langgraph/tree/main/examples)
- Section 01 (Tool Calling) - Use tools with LangGraph

---

**Next:** [03-embeddings-rag](../03-embeddings-rag) - Learn embeddings and vector databases →
