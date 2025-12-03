import requests
from qdrant_client import QdrantClient

# Configuration
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
EMBED_MODEL = "qwen3-embedding:0.6b"
CHAT_MODEL = "qwen3:8b"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_API_KEY = "qdrant_pass"
COLLECTION_NAME = "ai_agents_knowledge"

def get_embedding(text: str):
    response = requests.post(OLLAMA_EMBED_URL, json={"model": EMBED_MODEL, "prompt": text})
    return response.json()["embedding"]

def retrieve_context(query: str, limit: int = 3) -> str:
    """Retrieve relevant documents from Qdrant and format them as a string."""
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, api_key=QDRANT_API_KEY, https=False)
    
    query_vector = get_embedding(query)
    
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit
    )
    
    context_parts = []
    for hit in results:
        context_parts.append(f"- {hit.payload['content']} (Source: {hit.payload['source']})")
        
    return "\n".join(context_parts)

def generate_answer(query: str, context: str):
    """Generate an answer using the LLM and the retrieved context."""
    
    prompt = f"""You are a helpful AI assistant. Use the following context to answer the user's question.
If the answer is not in the context, say you don't know based on the provided information.

Context:
{context}

User Question: {query}

Answer:"""

    payload = {
        "model": CHAT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    
    print("Generating answer...")
    response = requests.post(OLLAMA_CHAT_URL, json=payload)
    return response.json()["message"]["content"]

def rag_pipeline(query: str):
    print(f"\nUser Query: {query}")
    print("1. Retrieving context...")
    
    context = retrieve_context(query)
    print(f"   Found {len(context.splitlines())} relevant snippets.")
    
    print("2. Generating response...")
    answer = generate_answer(query, context)
    
    print("\n--- Final Answer ---")
    print(answer)
    print("-" * 20)

if __name__ == "__main__":
    # Ensure data is ingested first! (Run 03_ingestion.py)
    rag_pipeline("What is RAG?")
    rag_pipeline("How do agents differ from traditional software?")
