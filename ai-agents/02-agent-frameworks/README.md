# 02 - Agent Frameworks: From Zero to Production 🕸️

> Master LangChain, LangGraph, and CrewAI - Build production-grade multi-agent systems

---

## 🎯 What You'll Master

This section covers **three major agent frameworks** used in production:

1. **LangChain** - The foundation (chains, memory, tools)
2. **LangGraph** - Stateful workflows (graphs, persistence, complex logic)
3. **CrewAI** - Multi-agent teams (role-based collaboration)

**By the end**, you'll build production-ready agents that can:
- 🔄 Execute complex multi-step workflows
- 🧠 Maintain conversation memory and state
- 🛠️ Orchestrate multiple tools intelligently
- 👥 Collaborate as multi-agent teams
- 📊 Scale to production environments

**Time Required:** 12-15 hours

---

## 📂 Folder Structure

```
02-agent-frameworks/
├── README.md                          ← You are here
├── requirements.txt                   ← All framework dependencies
│
├── langchain/                         ← LangChain Framework
│   ├── README.md
│   ├── 00_installation.py            ← Setup & verification
│   ├── 01_basic_chain.py             ← Simple LLM chain
│   ├── 02_prompt_templates.py        ← Dynamic prompts
│   ├── 03_chains_with_memory.py      ← Conversation memory
│   ├── 04_tools_integration.py       ← Tool calling
│   ├── 05_sequential_chains.py       ← Multi-step chains
│   ├── 06_router_chains.py           ← Conditional routing
│   └── 07_production_agent.py        ← Complete production example
│
├── langgraph/                         ← LangGraph Framework
│   ├── README.md
│   ├── 00_why_langgraph.py           ← When to use LangGraph
│   ├── 01_simple_langgraph.py        ← Basic workflow ✅
│   ├── 02_conditional_workflow.py    ← Branching logic ✅
│   ├── 03_tools_with_langgraph.py    ← Tool orchestration ✅
│   ├── 04_checkpoints.py             ← State persistence
│   ├── 05_human_in_loop.py           ← Human approval nodes
│   ├── 06_subgraphs.py               ← Nested workflows
│   ├── 07_streaming_events.py        ← Real-time updates
│   └── 08_production_agent.py        ← Enterprise-grade agent
│
├── crewai/                            ← CrewAI Framework
│   ├── README.md
│   ├── 00_crew_basics.py             ← Agents, tasks, crews
│   ├── 01_simple_crew.py             ← First multi-agent system
│   ├── 02_sequential_tasks.py        ← Task dependencies
│   ├── 03_hierarchical_crew.py       ← Manager + workers
│   ├── 04_tools_in_crew.py           ← Shared tool usage
│   ├── 05_memory_crew.py             ← Crew memory systems
│   ├── 06_delegation.py              ← Agent delegation
│   └── 07_production_crew.py         ← Full research team
│
└── comparison/                        ← Framework Comparison
    ├── README.md
    ├── same_task_all_frameworks.py   ← Same task, 3 ways
    ├── performance_comparison.py     ← Speed & resource usage
    └── when_to_use_what.md          ← Decision guide
```

---

## 🚀 Quick Start

### 1. Install All Frameworks

```bash
cd 02-agent-frameworks
pip install -r requirements.txt
```

### 2. Verify Ollama

```bash
# Check Ollama is running
ollama list

# Should see qwen3:8b
# If not: ollama pull qwen3:8b
```

### 3. Choose Your Path

**Path A: Complete Beginner**
```bash
# Start with LangChain basics
cd langchain
python 01_basic_chain.py

# Then move to LangGraph
cd ../langgraph
python 01_simple_langgraph.py

# Finally CrewAI
cd ../crewai
python 01_simple_crew.py
```

**Path B: Quick to Production**
```bash
# Jump to production examples
python langchain/07_production_agent.py
python langgraph/08_production_agent.py
python crewai/07_production_crew.py
```

**Path C: Framework Comparison**
```bash
# See same task in all frameworks
cd comparison
python same_task_all_frameworks.py
```

---

## 🧩 Framework Overview

### LangChain: The Swiss Army Knife

**What it is:**
- General-purpose LLM framework
- Chains, prompts, memory, tools
- Great for simple-to-moderate complexity

**When to use:**
- ✅ Quick prototypes
- ✅ Standard LLM workflows
- ✅ Learning fundamentals
- ✅ Simple sequential tasks

**When NOT to use:**
- ❌ Complex state management needed
- ❌ Conditional branching workflows
- ❌ Need to visualize agent logic

**Example:**
```python
from langchain_ollama import OllamaLLM
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

llm = OllamaLLM(model="qwen3:8b")
prompt = PromptTemplate.from_template("Tell me about {topic}")
chain = LLMChain(llm=llm, prompt=prompt)

result = chain.run(topic="AI agents")
```

---

### LangGraph: Production Workflows

**What it is:**
- State machine framework for agents
- Nodes, edges, conditional routing
- Built on LangChain but more powerful

**When to use:**
- ✅ Complex multi-step workflows
- ✅ Need conditional logic (if/else)
- ✅ State persistence across sessions
- ✅ Production-grade agents
- ✅ Need to debug/visualize flows

**When NOT to use:**
- ❌ Simple single-step tasks
- ❌ Learning basics (too complex)
- ❌ Quick prototypes

**Example:**
```python
from langgraph.graph import StateGraph, END

def agent_node(state):
    # Process state
    return {"answer": "result"}

workflow = StateGraph(State)
workflow.add_node("agent", agent_node)
workflow.set_entry_point("agent")
workflow.add_edge("agent", END)

app = workflow.compile()
result = app.invoke({"question": "Hello"})
```

---

### CrewAI: Multi-Agent Teams

**What it is:**
- Multi-agent collaboration framework
- Role-based agents working together
- Built-in task delegation and management

**When to use:**
- ✅ Multiple specialized agents needed
- ✅ Complex tasks requiring different skills
- ✅ Hierarchical workflows (manager + workers)
- ✅ Agent delegation and collaboration
- ✅ Research, content creation, analysis

**When NOT to use:**
- ❌ Single agent is sufficient
- ❌ Simple linear workflows
- ❌ Need fine-grained control over every step

**Example:**
```python
from crewai import Agent, Task, Crew

researcher = Agent(
    role="Researcher",
    goal="Find information",
    tools=[search_tool]
)

writer = Agent(
    role="Writer",
    goal="Write reports",
    tools=[]
)

task1 = Task(description="Research AI", agent=researcher)
task2 = Task(description="Write report", agent=writer)

crew = Crew(agents=[researcher, writer], tasks=[task1, task2])
result = crew.kickoff()
```

---

## 📊 Framework Comparison

| Feature | LangChain | LangGraph | CrewAI |
|---------|-----------|-----------|--------|
| **Learning Curve** | Easy | Moderate | Moderate |
| **Best For** | Simple chains | Complex workflows | Multi-agent teams |
| **State Management** | Basic | Advanced | Built-in |
| **Conditional Logic** | Limited | Excellent | Good |
| **Multi-Agent** | Manual | Manual | Native |
| **Visualization** | No | Yes | No |
| **Production Ready** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Documentation** | Excellent | Good | Good |
| **Community** | Large | Growing | Growing |

---

## 🎓 Learning Path

### Week 1: Foundations (LangChain)
- **Day 1-2:** Basic chains and prompts
- **Day 3-4:** Memory and conversation
- **Day 5-6:** Tools and sequential chains
- **Day 7:** Build a complete LangChain agent

### Week 2: Advanced Workflows (LangGraph)
- **Day 1-2:** State graphs and nodes
- **Day 3-4:** Conditional edges and routing
- **Day 5-6:** Persistence and streaming
- **Day 7:** Production agent with all features

### Week 3: Multi-Agent Systems (CrewAI)
- **Day 1-2:** Agents, tasks, crews
- **Day 3-4:** Hierarchical teams
- **Day 5-6:** Complex collaboration patterns
- **Day 7:** Build a research team

---

## 🏗️ Progressive Complexity

Each framework section follows this pattern:

```
00_basics.py          ← Hello World level
   ↓
01_simple.py          ← Single feature
   ↓
02_intermediate.py    ← Combine features
   ↓
03_advanced.py        ← Complex patterns
   ↓
04_production.py      ← Enterprise-grade
```

**Learning Philosophy:**
1. **Zero to Hero** - Every concept explained from scratch
2. **Build on Previous** - Each script extends the last
3. **OOP Design** - Professional, reusable code
4. **Fully Tested** - All scripts work with Ollama
5. **Production Ready** - Real-world patterns

---

## 🔧 Common Patterns You'll Master

### Pattern 1: Tool-Calling Agent
- LangChain: `AgentExecutor`
- LangGraph: Conditional loops
- CrewAI: Agent with tools

### Pattern 2: Multi-Step Workflow
- LangChain: `SequentialChain`
- LangGraph: State graph
- CrewAI: Sequential tasks

### Pattern 3: Conditional Routing
- LangChain: `RouterChain`
- LangGraph: Conditional edges
- CrewAI: Manager agent

### Pattern 4: Memory Management
- LangChain: `ConversationBufferMemory`
- LangGraph: State persistence
- CrewAI: Crew memory

---

## 🐛 Debugging Tips

### LangChain Issues
```python
# Enable verbose mode
chain = LLMChain(llm=llm, prompt=prompt, verbose=True)

# See what's being sent to LLM
print(chain.prompt.format(topic="test"))
```

### LangGraph Issues
```python
# Add debug prints in nodes
def my_node(state):
    print(f"[DEBUG] State: {state}")
    result = process(state)
    print(f"[DEBUG] Result: {result}")
    return result
```

### CrewAI Issues
```python
# Enable verbose and full output
crew = Crew(
    agents=[...],
    tasks=[...],
    verbose=True,
    full_output=True
)
```

---

## 🎯 Key Takeaways

### When to Use Each Framework:

**Use LangChain when:**
- Building your first agent
- Simple conversational AI
- Quick prototypes
- Learning the basics

**Use LangGraph when:**
- Complex multi-step workflows
- Need state persistence
- Conditional logic required
- Production deployment
- Want to visualize flows

**Use CrewAI when:**
- Multiple specialized agents
- Task delegation needed
- Hierarchical workflows
- Research/content creation
- Agent collaboration

**Use Multiple Frameworks when:**
- Enterprise applications
- Different components need different patterns
- Maximum flexibility required

---

## 📚 What Each Subfolder Contains

### `/langchain` - Foundation Framework
Complete guide from basic chains to production agents. Master prompts, memory, tools, and sequential workflows.

### `/langgraph` - State Machine Framework
Build complex workflows with state management, conditional routing, persistence, and human-in-the-loop patterns.

### `/crewai` - Multi-Agent Framework
Create collaborative agent teams with roles, tasks, delegation, and hierarchical management.

### `/comparison` - Framework Comparison
See the same tasks implemented in all three frameworks. Understand trade-offs and make informed decisions.

---

## 🚀 Next Steps

After completing this section, you'll be ready for:

1. **[03-embeddings-rag](../03-embeddings-rag)** - Add knowledge retrieval
2. **[04-memory-systems](../04-memory-systems)** - Long-term memory with Letta
3. **[05-voice-gpt](../05-voice-gpt)** - Voice-enabled agents

---

## 📖 Additional Resources

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [Ollama Documentation](https://github.com/ollama/ollama)

---

## 🤝 Project Structure Philosophy

**Why This Structure?**
- 📁 **Framework separation** - Each framework in its own folder
- 🔢 **Progressive numbering** - 00 to 99 for clear ordering
- 🎓 **Zero to hero** - Every framework taught completely
- 🏗️ **OOP design** - Professional, maintainable code
- ✅ **Fully tested** - All scripts run with Ollama

**Best Practices:**
1. Start with framework basics
2. Understand when to use each
3. Build progressively complex examples
4. Compare frameworks with same tasks
5. Choose the right tool for your needs

---

**Ready to begin?** Start with:
- **Beginners:** [langchain/01_basic_chain.py](./langchain/01_basic_chain.py)
- **Intermediate:** [langgraph/01_simple_langgraph.py](./langgraph/01_simple_langgraph.py)
- **Advanced:** [crewai/01_simple_crew.py](./crewai/01_simple_crew.py)

---

*"The right framework makes complex agents simple. The wrong one makes simple agents complex."*
