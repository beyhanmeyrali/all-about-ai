# LangGraph Framework Tutorial

Complete guide to building production-grade agents with LangGraph, from basics to enterprise systems.

## 📚 Overview of LangGraph

LangGraph is a **low-level orchestration framework** built on top of LangChain, designed for creating **stateful, controllable AI agent workflows**. It models applications as **graphs**, where:
- **Nodes** represent actions (e.g., agents or tools)
- **Edges** define control flow (e.g., sequential, conditional, or cyclic)
- **State** is shared and persisted across executions

This makes it particularly powerful for handling complexity in real-world scenarios, such as **cycles in reasoning** or **collaboration between components**.

### Why LangGraph Exists

Unlike simpler agent frameworks that treat agents as **black boxes**, LangGraph provides **explicit control** over:
- ✅ Execution paths
- ✅ Moderation loops
- ✅ Persistence and checkpointing
- ✅ Human-in-the-loop workflows
- ✅ Multi-agent orchestration

This ensures **reliability in production**. It's available in both **Python** and **JavaScript** and integrates seamlessly with LLMs (e.g., via LangChain) and external tools.

---

## 🔧 Handling Multi-Tool Scenarios

In multi-tool setups, LangGraph treats tools as **callable functions** (e.g., via LangChain's tool-calling mechanism) that an agent can invoke dynamically. A single agent can access multiple tools, but the graph structure allows for **modular handling** to avoid overwhelming the LLM (e.g., a single agent might struggle with 10+ tools across domains).

### Key Components

- **Tools**: Defined as Python functions decorated with `@tool` (from `langchain_core.tools`). Each tool includes a name, description, and schema for the LLM to decide when to call it. Examples include math solvers (e.g., `PythonREPLTool`), web search (e.g., Serper API), or custom functions like data retrieval.

- **Agent Node**: A graph node that runs an LLM (e.g., GPT-4o or Qwen) bound to the tools. The LLM reasons over the state (e.g., user query + prior messages) and outputs either a final response or tool calls.

- **Tool Node**: A dedicated node (e.g., using `langgraph.prebuilt.ToolNode`) that executes the called tools in parallel or sequence, handles errors, and updates the state with results.

- **Conditional Edges**: Routes based on the agent's output—e.g., if tool calls are present, go to the tool node; otherwise, end or route to another node.

- **State Management**: Uses a shared `TypedDict` (e.g., `AgentState = TypedDict("AgentState", {"messages": Annotated[list, add_messages]})`) to track messages, tool outputs, and intermediate results. Checkpointers (e.g., `MemorySaver`) enable persistence across sessions.

### Execution Flow for Multi-Tools

1. **Entry Point**: User input enters the graph (e.g., via `StateGraph.set_entry_point("agent")`).
2. **Agent Reasoning**: The agent node calls the LLM, which decides on tool calls (e.g., "Use web_search for facts and math_solver for calculations").
3. **Tool Execution**: Conditional edge routes to the tool node, which invokes tools (supports parallel calls for efficiency).
4. **Loop Back**: Tool results append to state; edge returns to agent for further reasoning (handles cycles like ReAct: Reason-Act).
5. **Exit**: If no tools needed, route to `END` with final output.

### Example Code Snippet (Single Agent with Multiple Tools)

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent  # High-level helper
# Or build low-level: from langgraph.prebuilt import ToolNode

class AgentState(TypedDict):
    messages: Annotated[list, "add_messages"]  # Accumulates chat history

# Define tools
from langchain_core.tools import tool
@tool
def web_search(query: str) -> str: ...
@tool
def calculator(expression: str) -> str: ...

# High-level: Quick setup
model = ChatOllama(model="qwen3:8b")
tools = [web_search, calculator]
agent = create_react_agent(model, tools, state_modifier="Custom prompt")

# Low-level: Custom graph for more control
graph = StateGraph(AgentState)
graph.add_node("agent", lambda state: {"messages": [model.bind_tools(tools).invoke(state["messages"])]})
graph.add_node("tools", ToolNode(tools))
graph.add_conditional_edges("agent", lambda state: "tools" if state["messages"][-1].tool_calls else END)
graph.add_edge("tools", "agent")
app = graph.compile(checkpointer=MemorySaver())
```

This setup scales to dozens of tools by grouping them (e.g., domain-specific subsets) or using routers.

---

## 👥 Handling Multi-Agent Scenarios

Multi-agent workflows in LangGraph involve multiple independent **"actors"** (each an LLM-powered agent with its own prompt, tools, and logic) connected via a graph. This enables collaboration, such as task delegation or parallel processing, mimicking human teams. **Agents don't share a full scratchpad by default**—state is passed selectively via edges.

### Key Components

- **Individual Agents**: Each is a subgraph or node with custom prompts (e.g., `ChatPromptTemplate`), LLMs, and tools. For example, a "researcher" agent uses search tools, while a "chart_generator" uses code execution.

- **Supervisor/Router Agent**: A central node (itself an agent) that analyzes input/state and routes to specialists (e.g., via tool-calling where "tools" are other agents). It can use prompts like: "Route to math_agent if calculation needed, else web_agent."

- **Handoff Tools**: Custom tools (e.g., `create_handoff_tool(agent_name="Bob")`) for agents to delegate (passes state updates like `Command.update`).

- **Graph Structure**: 
  - **Sequential/Hierarchical**: Agents run in order (e.g., researcher → analyzer).
  - **Parallel**: Multiple edges from supervisor for concurrent execution.
  - **Cyclic**: Loops for refinement (e.g., supervisor recalls an agent).

- **State Management**: Shared global state (e.g., with keys for agent-specific messages) or per-agent scratchpads. Supports moderation (e.g., quality checks) and human-in-the-loop interrupts.

### Execution Flow for Multi-Agents

1. **Input to Supervisor**: User query enters; supervisor decides routing (e.g., "Delegate GDP research to researcher_agent").
2. **Agent Invocation**: Edges route to specialist nodes/subgraphs. Each agent processes (reasoning + tools) and returns updated state.
3. **Coordination**: Supervisor aggregates outputs, decides next steps (e.g., "Now to chart_generator"), or ends if complete.
4. **Collaboration**: Agents can hand off (e.g., researcher passes data to generator) or communicate via shared state.
5. **Persistence**: Checkpointers save state for resuming interrupted workflows.

### Example Code Snippet (Supervisor + Two Agents)

```python
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate

class MultiAgentState(TypedDict):  # Shared state
    messages: Annotated[list, "add_messages"]
    next: str  # For routing

# Supervisor prompt: "You are a supervisor. Route to {researcher|chart_generator} or FINISH."
supervisor_prompt = ChatPromptTemplate.from_template(...)
supervisor = supervisor_prompt | model | (lambda output: {"next": output.content})  # Simplified

# Specialist agents (as nodes)
def researcher_node(state): ...  # Uses search tools
def chart_generator_node(state): ...  # Uses code tools

graph = StateGraph(MultiAgentState)
graph.add_node("supervisor", supervisor)
graph.add_node("researcher", researcher_node)
graph.add_node("chart_generator", chart_generator_node)
graph.set_entry_point("supervisor")

# Conditional routing
def route(state):
    return state["next"] if state["next"] != "FINISH" else END
graph.add_conditional_edges("supervisor", route, {
    "researcher": "researcher",
    "chart_generator": "chart_generator",
    "FINISH": END
})
graph.add_edge("researcher", "supervisor")
graph.add_edge("chart_generator", "supervisor")

app = graph.compile()
```

This creates a loop: supervisor → specialist → back, until "FINISH."

---

## 🚨 Scaling to 10 Agents × 10 Tools (Context Bloat Problem)

When you scale to **10 agents × 10 tools each = 100 tools**, or even just 10 agents with overlapping tools, the biggest risk is **context bloat**: stuffing the LLM prompt with hundreds of tool schemas → high cost, latency, and worst of all, the model gets confused and makes bad tool choices.

### LangGraph's Solution: Proven Strategies

LangGraph itself does **not magically shrink context**, but it gives you the exact building blocks to implement every known technique that avoids bloat. Here are the proven strategies people actually use in production LangGraph systems (2024–2025 best practices):

| Technique                        | How it prevents bloat                                                                 | How you implement it in LangGraph today                                                                 |
|----------------------------------|---------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| 1. One agent → few tools only    | Each agent sees at most 4–8 tools in its prompt                                       | Build 10 separate agent nodes/subgraphs, each bound to its own small tool list                            |
| 2. Supervisor + routing          | Only the supervisor sees the list of agents (not tools). Specialists see their own tools only | Classic "supervisor chain" pattern (see LangGraph multi-agent examples)                                  |
| 3. Dynamic tool retrieval        | Tools are fetched and injected only when needed (like RAG for tools)                 | Use a ToolRetriever node that queries a vector DB of tool descriptions only when uncertainty is high     |
| 4. Hierarchical / nested graphs  | Top-level graph routes to subgraphs; each subgraph has its own isolated context window | Each team (e.g., FinanceTeam, ResearchTeam) is a separate StateGraph compiled as a single node           |
| 5. Tool routing via LLM          | Supervisor decides which *agent* (i.e. which tool subset) to call — no tool schemas sent | Supervisor uses function calling where each "function" is actually a handoff to another agent subgraph   |
| 6. State pruning & summarization| Old messages or tool results are summarized or dropped before looping back           | Add a "compress" node that runs a summarization LLM on state["messages"] before returning to supervisor   |
| 7. Parallel tool execution       | Tools run in ToolNode (outside LLM context); results come back concise                 | ToolNode executes all called tools in parallel and only returns short results, never full schemas again  |

### Real-World Pattern (10+ Agents)

```python
# 1. Supervisor sees only 10 "agent handoff tools", not 100 real tools
handoff_tools = [
    create_handoff_tool("finance_agent"),
    create_handoff_tool("research_agent"),
    create_handoff_tool("legal_agent"),
    # ... 7 more
]
supervisor = supervisor_prompt | llm.bind_tools(handoff_tools)   # ← only 10 schemas!

# 2. Each specialist is its own subgraph with its own 5–10 tools
finance_subgraph = create_finance_team_graph()   # has its own 8 tools, completely separate context
research_subgraph = create_research_team_graph() # has tavily, browser, etc.

# 3. Main graph
graph.add_node("supervisor", supervisor_node)
graph.add_node("finance", finance_subgraph)      # compiled subgraph = one node
graph.add_node("research", research_subgraph)

# Conditional edge from supervisor looks only at which handoff tool was called
graph.add_conditional_edges("supervisor", route_to_agent, {
    "finance_agent": "finance",
    "research_agent": "research",
    "FINISH": END,
})
graph.add_edge("finance", "supervisor")
graph.add_edge("research", "supervisor")
```

**Result:**
- Supervisor prompt size: ~3–5k tokens even with 20 teams  
- Each specialist prompt size: ~4–8k tokens (only its own tools + relevant history)  
- **No LLM ever sees all 100 tools at once**

### Quick Checklist to Keep Context Under Control

- ❌ Never do `llm.bind_tools(all_100_tools)` on any single node  
- ✅ Maximum 8 tools per leaf agent (ideal is 4–6)  
- ✅ Use a supervisor or router that only knows agent names/capabilities  
- ✅ Make heavy teams subgraphs (they become a single node in the parent graph)  
- ✅ Add a compression/summarization node in long cycles  
- ✅ Stream with tokens, not full messages, when possible

---

## 🎯 When to Use LangGraph

## 🎯 When to Use LangGraph

### ✅ LangGraph is Perfect For:

1. **Complex Multi-Step Workflows**
   - Approval pipelines with multiple gates
   - Iterative refinement processes
   - State-dependent routing

2. **Stateful Agents**
   - Long-running conversations
   - Multi-turn reasoning
   - Context preservation across sessions

3. **Cyclic Workflows**
   - Retry logic with feedback
   - Human-in-the-loop iterations
   - Self-improvement loops

4. **Production Systems**
   - Checkpoint-based recovery
   - Audit trails
   - Scalable architectures

### ❌ Not Ideal For:

- Simple linear chains (use LangChain)
- One-shot queries without state
- Basic prompt-response patterns
- Simple tool calling

## 📖 Tutorial Structure

### Part 1: Fundamentals (Scripts 01-03)

**01_simple_langgraph.py** - Core Concepts
- StateGraph basics
- Node and edge definitions
- Simple linear workflows
- State passing and updates

**02_conditional_workflow.py** - Branching Logic
- Conditional edges
- Dynamic routing
- Multi-path workflows
- Decision making

**03_tools_with_langgraph.py** - Tool Integration
- Tool definition and binding
- ReAct pattern with graphs
- Tool execution nodes
- Result aggregation

### Part 2: Advanced Features (Scripts 04-07)

**04_checkpoints.py** - State Persistence ⭐
- MemorySaver for checkpoints
- Multi-thread management
- Time travel and rollback
- Conversation resume
- Export/import functionality

**05_human_in_loop.py** - Approval Workflows ⭐
- Approval gates
- Interactive review systems
- Multi-step approvals
- Risk-based routing
- Feedback collection

**06_subgraphs.py** - Modular Composition ⭐
- Subgraph creation
- Parallel subgraph execution
- Hierarchical architectures
- Microservice patterns
- Service isolation

**07_streaming_events.py** - Real-Time Updates ⭐
- graph.stream() API
- Progress tracking
- Debug streaming
- Production event systems
- Live monitoring

### Part 3: Production (Script 08)

**08_production_agent.py** - Complete System ⭐⭐⭐
- All features combined
- Security subgraph
- Approval workflow
- Tool orchestration
- Error handling
- Metrics and observability
- Production-ready patterns

## 🚀 Quick Start

### Installation Check

```bash
cd /workspace/all-about-ai/ai-agents
source venv/bin/activate
python 02-agent-frameworks/langchain/00_installation.py
```

### Run Your First Graph

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class State(TypedDict):
    message: str

def process(state: State) -> State:
    return {"message": f"Processed: {state['message']}"}

workflow = StateGraph(State)
workflow.add_node("process", process)
workflow.set_entry_point("process")
workflow.add_edge("process", END)

graph = workflow.compile()
result = graph.invoke({"message": "Hello"})
print(result)  # {"message": "Processed: Hello"}
```

## 🎓 Learning Path

### Beginner (Week 1)
1. Run scripts 01-03
2. Understand StateGraph basics
3. Build a simple conversational agent
4. Practice conditional routing

### Intermediate (Week 2)
1. Master checkpoints (04)
2. Implement approval workflows (05)
3. Build with subgraphs (06)
4. Add streaming (07)

### Advanced (Week 3)
1. Study production agent (08)
2. Combine all features
3. Build custom enterprise agent
4. Optimize for production

## 🔑 Key Concepts

### State Management

```python
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    # Simple state - overwrites each time
    current_user: str

    # Accumulated state - appends with reducer
    messages: Annotated[List[str], operator.add]

    # Computed state
    step_count: int
```

### Checkpoints

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# Use thread_id for conversation isolation
config = {"configurable": {"thread_id": "user_123"}}
result = graph.invoke(state, config=config)

# Resume later from same checkpoint
continued = graph.invoke(new_state, config=config)
```

### Conditional Routing

```python
def route(state: State) -> Literal["path_a", "path_b"]:
    return "path_a" if state["score"] > 0.5 else "path_b"

workflow.add_conditional_edges(
    "decision_node",
    route,
    {
        "path_a": "node_a",
        "path_b": "node_b"
    }
)
```

### Streaming

```python
for event in graph.stream(initial_state):
    node_name = list(event.keys())[0]
    node_state = event[node_name]
    print(f"Node {node_name}: {node_state}")
```

## 📊 LangGraph vs. LangChain

| Feature | LangGraph | LangChain |
|---------|-----------|-----------|
| **Architecture** | Graph-based | Chain-based |
| **State** | Explicit, typed | Implicit |
| **Cycles** | Native support | Not supported |
| **Checkpoints** | Built-in | Manual |
| **Complexity** | High learning curve | Easier start |
| **Use Case** | Complex agents | Simple workflows |
| **Flexibility** | Very high | Moderate |
| **Debugging** | Excellent | Good |

## 🛠️ Common Patterns

### Pattern 1: ReAct Agent

```python
workflow.add_node("think", agent_think)
workflow.add_node("act", agent_act)
workflow.add_node("observe", agent_observe)

workflow.add_conditional_edges(
    "think",
    should_continue,
    {
        "act": "act",
        "finish": END
    }
)

workflow.add_edge("act", "observe")
workflow.add_edge("observe", "think")  # Cycle!
```

### Pattern 2: Approval Pipeline

```python
workflow.add_node("propose", create_proposal)
workflow.add_node("review", await_human_review)
workflow.add_node("execute", execute_proposal)

workflow.add_conditional_edges(
    "review",
    check_approval,
    {
        "approved": "execute",
        "rejected": "propose",  # Retry
        "pending": "review"     # Wait
    }
)
```

### Pattern 3: Parallel Processing

```python
# Create parallel subgraphs
search_graph = build_search_subgraph()
analysis_graph = build_analysis_subgraph()

workflow.add_node("search", search_graph)
workflow.add_node("analyze", analysis_graph)
workflow.add_node("merge", merge_results)

# Both run independently
workflow.add_edge("search", "merge")
workflow.add_edge("analyze", "merge")
```

## 🎯 Best Practices

### 1. Type Your State
```python
# Good
class MyState(TypedDict):
    field: str
    count: int

# Better - with annotations
class MyState(TypedDict):
    messages: Annotated[List[str], operator.add]
    metadata: Dict[str, Any]
```

### 2. Use Checkpoints for Long Conversations
```python
# Always use thread_id for multi-user systems
config = {"configurable": {"thread_id": user_id}}
graph.invoke(state, config=config)
```

### 3. Stream for Better UX
```python
for event in graph.stream(state):
    # Send real-time updates to user
    send_progress_update(event)
```

### 4. Handle Errors Gracefully
```python
def node_with_error_handling(state):
    try:
        result = risky_operation()
    except Exception as e:
        state["errors"].append(str(e))
        state["status"] = "error"
        return state

    state["result"] = result
    return state
```

### 5. Use Subgraphs for Modularity
```python
# Build reusable components
auth_subgraph = build_auth_service()
data_subgraph = build_data_service()

# Compose into larger system
workflow.add_node("auth", auth_subgraph)
workflow.add_node("data", data_subgraph)
```

## 🔍 Debugging Tips

### 1. Enable Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. Use Stream for Step-by-Step Inspection
```python
for event in graph.stream(state):
    print(json.dumps(event, indent=2))
```

### 3. Visualize the Graph
```python
from langgraph.graph import Graph

# Get mermaid diagram
print(graph.get_graph().draw_mermaid())
```

### 4. Inspect Checkpoints
```python
state = graph.get_state(config)
print(f"Current values: {state.values}")
print(f"Checkpoint ID: {state.config}")
```

## 📈 Performance Tips

1. **Minimize LLM Calls**: Batch when possible
2. **Use Parallel Subgraphs**: For independent operations
3. **Implement Caching**: For repeated queries
4. **Optimize State Size**: Keep state minimal
5. **Use Async**: For I/O-bound operations

## 🚀 Production Checklist

- [ ] Add comprehensive error handling
- [ ] Implement retry logic with backoff
- [ ] Use persistent checkpointer (not MemorySaver)
- [ ] Add logging and monitoring
- [ ] Implement rate limiting
- [ ] Add input validation
- [ ] Setup metrics collection
- [ ] Configure timeout handling
- [ ] Add security validation
- [ ] Implement audit logging

## 📚 Additional Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph Examples](https://github.com/langchain-ai/langgraph/tree/main/examples)
- [State Management Guide](https://langchain-ai.github.io/langgraph/concepts/low_level/#state)
- [Checkpoint Documentation](https://langchain-ai.github.io/langgraph/concepts/persistence/)

## 🎓 Next Steps

After mastering LangGraph, consider:

1. **CrewAI Framework** (../crewai/)
   - Multi-agent collaboration
   - Role-based agents
   - Task delegation

2. **Framework Comparison** (../comparison/)
   - When to use each framework
   - Migration patterns
   - Performance benchmarks

3. **Production Deployment**
   - Scaling strategies
   - Monitoring setup
   - Cost optimization

## 💡 Tips for Success

1. **Start Simple**: Begin with 01-03, master basics
2. **Build Incrementally**: Add one feature at a time
3. **Test Thoroughly**: Use Ollama for local testing
4. **Read the Code**: Our examples are heavily documented
5. **Experiment**: Modify examples to learn
6. **Combine Features**: Build your own production agent

---

**Ready to build stateful agents?** Start with `01_simple_langgraph.py`! 🚀

For questions or issues, refer to the main [02-agent-frameworks README](../README.md).
