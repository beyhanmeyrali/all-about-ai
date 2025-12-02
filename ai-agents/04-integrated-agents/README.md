# Integrated Agents (RAG + CrewAI)

This directory contains examples of **Integrated Agents** that combine the reasoning capabilities of CrewAI with the knowledge retrieval capabilities of our RAG system (Qdrant).

## Prerequisites

1.  **Python 3.12** (use the `.venv` from `02-agent-frameworks/crewai`)
2.  **Ollama** running locally (`qwen3:4b` and `qwen3-embedding:0.6b`)
3.  **Qdrant** running in Docker (`docker start qdrant`)
4.  **Knowledge Base Populated** (Run `03-embeddings-rag/03_ingestion.py` first)

## Scripts

### `01_rag_agent.py`
A simple agent ("Knowledge Specialist") equipped with a custom `KnowledgeBaseTool`.
- **Goal:** Answer questions using internal knowledge.
- **Tool:** Queries Qdrant for relevant context.
- **Process:**
    1.  User asks a question.
    2.  Agent uses the tool to search Qdrant.
    3.  Tool generates embedding via Ollama and queries Qdrant.
    4.  Agent synthesizes the answer from the retrieved context.

## How to Run

```powershell
# 1. Activate the environment (if not already)
..\02-agent-frameworks\crewai\.venv_new\Scripts\activate

# 2. Ensure Qdrant is running
docker ps # Check for qdrant

# 3. Run the agent
$env:PYTHONUTF8=1; python 01_rag_agent.py
```
