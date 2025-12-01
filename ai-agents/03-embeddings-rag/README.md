# 03 - Embeddings & RAG: Teaching LLMs About Your Data 📊

> Learn embeddings, semantic search, and Retrieval-Augmented Generation (RAG) using local tools.

---

## 🎯 Learning Objectives

By the end of this section, you will understand:
- ✅ What embeddings are and how they work
- ✅ Semantic similarity vs keyword search
- ✅ Vector databases (Qdrant via Docker)
- ✅ Building a simple RAG pipeline
- ✅ Document chunking strategies
- ✅ Combining RAG with tool-calling agents

**Time Required:** 5-6 hours

---

## 📚 What This Section Covers

### Files:

```
03-embeddings-rag/
├── README.md                          ← You are here
├── requirements.txt                   ← Python dependencies
├── 01_embeddings_basics.py           ← Intro to embeddings with Ollama
├── 02_qdrant_setup.py                ← Connecting to Qdrant
├── 03_ingestion.py                   ← Loading & embedding documents
├── 04_retrieval.py                   ← Semantic search examples
└── 05_rag_pipeline.py                ← Complete RAG system
```

---

## 🛠️ Setup

1. **Ensure Qdrant is running:**
   ```bash
   # From ai-agents root
   docker compose up -d
   ```

2. **Ensure Embedding Model is pulled:**
   ```bash
   ollama pull qwen3-embedding:0.6b
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
