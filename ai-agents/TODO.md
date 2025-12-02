# Future Development Plan

## Phase 1: CrewAI & Multi-Agent Systems ✅ COMPLETE
- [x] Complete development and testing of CrewAI examples in `02-agent-frameworks/crewai`.
- [x] Implement delegation patterns.
- [x] Implement hierarchical crews.
- [x] Create native Windows setup (Python 3.12).
- [x] Document setup process in SETUP.md.
- [x] Verify scripts with local Ollama (`qwen3:4b`).

## Phase 2: RAG & Vector Database Infrastructure
- [x] Set up **Qdrant** on Windows (using Docker Desktop).
- [x] Verify Qdrant connectivity and persistence.
- [x] Pull and test embedding model: `qwen3-embedding:0.6b` (or `nomic-embed-text` if unavailable).
- [x] Create `03-embeddings-rag` module.
    - [x] Implement basic embedding generation.
    - [x] Implement Qdrant ingestion (loading documents).
    - [x] Implement semantic search / retrieval.

## Phase 3: Integration & Voice Assistant
- [x] Integrate RAG with CrewAI agents (`04-integrated-agents`).
    - [x] Create `KnowledgeBaseTool` connecting to Qdrant.
    - [x] Create RAG Agent script.
    - [x] Verify integration (Requires Qdrant running).
- [ ] Build the Main Voice Project using the established stack:
    - **LLM:** Qwen3:8b (via Ollama)
    - **Embeddings:** Qwen3-embedding (via Ollama)
    - **Vector DB:** Qdrant (Docker)
    - **Framework:** CrewAI / LangGraph
    - **Voice:** Whisper (STT) + Coqui/System (TTS)
    - **VAD:** Silero VAD (for efficient voice detection)
