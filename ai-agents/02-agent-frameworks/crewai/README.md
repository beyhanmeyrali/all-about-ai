# CrewAI: Orchestrating Multi-Agent Teams 🚣‍♂️

> "Talent wins games, but teamwork and intelligence win championships." – Michael Jordan

## 🪟 Windows Users - Docker Setup Required

**Important**: CrewAI has C++ dependencies that are difficult to install on Windows. We've created a **Docker-based solution** that works perfectly!

**📖 See [SETUP.md](./SETUP.md) for complete installation instructions.**

**Quick Start:**
```powershell
# Build the Docker image (first time only)
docker build -t crewai-runner .

# Run any script
.\run-crew.ps1 00_crew_basics.py
```

**Prerequisites:**
1. **Docker Desktop** installed and running
2. **Ollama** running on host (`ollama serve`)
3. Model pulled: `ollama pull qwen3:8b`

The Docker approach avoids Windows build issues while keeping everything local!


CrewAI is a framework designed to orchestrate **role-playing, autonomous AI agents**. By fostering collaborative intelligence, CrewAI empowers agents to work together seamlessly, tackling complex tasks that would be difficult for a single agent to handle.

## 🧠 Core Concepts

### 1. Agents (The Team Members)
Agents are autonomous units programmed to perform tasks, make decisions, and communicate with other agents. Think of them as members of a team, each with specific skills and a particular job to do.
- **Role:** What is their job title? (e.g., "Senior Researcher")
- **Goal:** What are they trying to achieve? (e.g., "Uncover groundbreaking technologies")
- **Backstory:** What is their personality and history? (Helps the LLM stay in character)

### 2. Tasks (The Assignments)
Tasks are specific assignments that agents need to complete.
- **Description:** What needs to be done?
- **Expected Output:** What should the result look like?
- **Agent:** Who is responsible for this task?

### 3. Crew (The Team)
A Crew represents a collaborative group of agents working together to achieve a set of tasks.
- **Process:** How do they work together? (Sequential, Hierarchical)
- **Verbose:** Do you want to see their internal monologue?

## 🚀 Why CrewAI?

While LangChain and LangGraph are great for building *single* powerful agents or defined workflows, CrewAI shines when you need a **team** of specialists.

| Feature | Single Agent | CrewAI (Multi-Agent) |
|---------|--------------|----------------------|
| **Focus** | Generalist | Specialist |
| **Complexity** | Linear thinking | Parallel/Collaborative thinking |
| **Error Correction** | Self-correction only | Peer review & delegation |
| **Creativity** | Limited by one perspective | Diverse perspectives |

## 🛠️ The Local Stack

We will use CrewAI with **Ollama** running locally.

- **LLM:** `qwen3:8b` (via Ollama)
- **Framework:** `crewai`

## 📂 Examples Structure

1. **00_crew_basics.py** - The "Hello World" of multi-agent systems
2. **01_simple_crew.py** - A 2-agent research team
3. **02_sequential_tasks.py** - Passing data between agents
4. **03_hierarchical_crew.py** - Manager delegating to workers
5. **04_tools_in_crew.py** - Giving agents superpowers (tools)
6. **07_production_crew.py** - A complete content creation studio

Let's build your first AI team! 🚀
