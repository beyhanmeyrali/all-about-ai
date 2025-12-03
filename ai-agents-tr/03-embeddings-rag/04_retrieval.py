import requests
from qdrant_client import QdrantClient
import json

# Configuration
OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL_NAME = "qwen3-embedding:0.6b"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_API_KEY = "qdrant_pass"
COLLECTION_NAME = "ai_agents_knowledge"

def get_embedding(text: str):
    try:
        response = requests.post(OLLAMA_URL, json={"model": MODEL_NAME, "prompt": text})
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        print(f"Embedding error: {e}")
        return None

def search(query: str, limit: int = 3):
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, api_key=QDRANT_API_KEY, https=False)
    
    print(f"\nQuery: '{query}'")
    print("-" * 50)
    
    # 1. Embed Query
    query_vector = get_embedding(query)
    if not query_vector:
        return
        
    # 2. Search Qdrant
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit
    )
    
    # 3. Display Results
    for i, hit in enumerate(results):
        score = hit.score
        content = hit.payload.get("content", "No content")
        source = hit.payload.get("source", "Unknown")
        
        print(f"Result {i+1} (Score: {score:.4f}):")
        print(f"Source: {source}")
        print(f"Content: {content}\n")

if __name__ == "__main__":
    # Test queries
    search("What is an AI agent?")
    search("How do vector databases work?")
    search("Tell me about RAG")
