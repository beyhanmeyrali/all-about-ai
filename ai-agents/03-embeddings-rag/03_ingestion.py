import requests
from qdrant_client import QdrantClient
from qdrant_client.http import models
import uuid
import time

# Configuration
OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL_NAME = "qwen3-embedding:0.6b"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_API_KEY = "qdrant_pass"
COLLECTION_NAME = "ai_agents_knowledge"

# Sample Data: "The History of AI Agents" (Fictionalized for demo)
DOCUMENTS = [
    {
        "content": "AI Agents are autonomous systems capable of perceiving their environment and taking actions to achieve goals.",
        "source": "intro_to_ai.txt",
        "topic": "definition"
    },
    {
        "content": "Early AI systems were rule-based, relying on hardcoded logic. Modern agents use LLMs for reasoning.",
        "source": "history.txt",
        "topic": "history"
    },
    {
        "content": "Tool calling allows LLMs to interact with the outside world, such as APIs, databases, and file systems.",
        "source": "capabilities.txt",
        "topic": "tools"
    },
    {
        "content": "RAG (Retrieval-Augmented Generation) connects LLMs to private data by retrieving relevant context before generating an answer.",
        "source": "rag_guide.txt",
        "topic": "rag"
    },
    {
        "content": "Vector databases store data as high-dimensional points, enabling semantic search based on meaning rather than keywords.",
        "source": "vector_db.txt",
        "topic": "infrastructure"
    }
]

def get_embedding(text: str):
    try:
        response = requests.post(OLLAMA_URL, json={"model": MODEL_NAME, "prompt": text})
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        print(f"Embedding error: {e}")
        return None

def ingest_data():
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, api_key=QDRANT_API_KEY, https=False)
    
    print(f"Starting ingestion into '{COLLECTION_NAME}'...")
    
    points = []
    
    for doc in DOCUMENTS:
        print(f"Processing: {doc['topic']}...")
        
        # 1. Generate Embedding
        vector = get_embedding(doc["content"])
        
        if vector:
            # 2. Prepare Point
            point = models.PointStruct(
                id=str(uuid.uuid4()),  # Random UUID
                vector=vector,
                payload=doc  # Store original text and metadata
            )
            points.append(point)
        else:
            print("Skipping due to embedding failure.")
            
    # 3. Upload to Qdrant
    if points:
        operation_info = client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        print(f"\nUpload status: {operation_info.status}")
        print(f"Ingested {len(points)} documents.")
    else:
        print("No points to upload.")

if __name__ == "__main__":
    ingest_data()
