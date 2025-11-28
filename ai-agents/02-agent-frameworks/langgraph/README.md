# LangGraph Framework Tutorial

Complete guide to building production-grade agents with LangGraph, from basics to enterprise systems.

## 📚 Overview

LangGraph is a powerful framework for building stateful, multi-actor applications with LLMs. Unlike simple chains, LangGraph uses graph-based workflows to model complex agent behaviors with:

- **State Machines**: Explicit state management with typed states
- **Checkpoints**: Built-in persistence and time travel
- **Cycles**: Support for iterative and feedback-based workflows
- **Human-in-the-Loop**: Natural approval and review patterns
- **Subgraphs**: Modular composition of workflow components
- **Streaming**: Real-time progress updates

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
