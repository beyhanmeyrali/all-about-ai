from qdrant_client import QdrantClient
from qdrant_client.http import models
import sys

# Configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_API_KEY = "qdrant_pass"  # As set in docker-compose.yml
COLLECTION_NAME = "ai_agents_knowledge"
VECTOR_SIZE = 1024  # Depends on the model! qwen3-embedding might be 1024 or 768. Check first!

# NOTE: qwen3-embedding:0.6b usually has 1024 dimensions.
# nomic-embed-text has 768 dimensions.
# We will check dynamically in a real app, but here we hardcode for the demo.

def setup_qdrant():
    print(f"Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}...")
    
    try:
        client = QdrantClient(
            host=QDRANT_HOST, 
            port=QDRANT_PORT,
            api_key=QDRANT_API_KEY,
            prefer_grpc=False,  # Use HTTP REST API
            https=False  # Local connection without SSL
        )
        
        # Check health
        collections = client.get_collections()
        print(f"Connected! Found {len(collections.collections)} collections.")
        
        # Check if collection exists
        exists = client.collection_exists(collection_name=COLLECTION_NAME)
        
        if exists:
            print(f"Collection '{COLLECTION_NAME}' already exists.")
            # Optional: client.delete_collection(COLLECTION_NAME)
        else:
            print(f"Creating collection '{COLLECTION_NAME}'...")
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=VECTOR_SIZE,
                    distance=models.Distance.COSINE
                )
            )
            print("Collection created successfully!")
            
        return client

    except Exception as e:
        print(f"Failed to connect to Qdrant: {e}")
        print("Make sure Docker container is running: 'docker compose up -d'")
        return None

if __name__ == "__main__":
    client = setup_qdrant()
    if client:
        print("\nQdrant setup complete. Ready for ingestion.")
