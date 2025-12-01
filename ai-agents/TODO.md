# Future Development Plan

## Phase 1: CrewAI & Multi-Agent Systems ✅ COMPLETE
- [x] Complete development and testing of CrewAI examples in `02-agent-frameworks/crewai`.
- [x] Implement delegation patterns.
- [x] Implement hierarchical crews.
- [x] Create Docker-based setup for Windows compatibility.
- [x] Document setup process in SETUP.md.
- [x] Create helper script (run-crew.ps1) for easy execution.

## Phase 2: RAG & Vector Database Infrastructure
- [x] Set up **Qdrant** on Windows (using Docker Desktop).
- [x] Verify Qdrant connectivity and persistence.
- [x] Pull and test embedding model: `qwen3-embedding:0.6b` (or `nomic-embed-text` if unavailable).
- [x] Create `03-embeddings-rag` module.
    - [x] Implement basic embedding generation.
    - [x] Implement Qdrant ingestion (loading documents).
    - [x] Implement semantic search / retrieval.

## Phase 3: Integration & Voice Assistant
- [ ] Integrate RAG with CrewAI agents.
- [ ] Build the Main Voice Project using the established stack:
    - **LLM:** Qwen3:8b (via Ollama)
    - **Embeddings:** Qwen3-embedding (via Ollama)
    - **Vector DB:** Qdrant (Docker)
    - **Framework:** CrewAI / LangGraph
    - **Voice:** Whisper (STT) + Coqui/System (TTS)
