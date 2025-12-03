import requests
import json
import numpy as np
from typing import List

# Configuration
OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL_NAME = "qwen3-embedding:0.6b"  # Or "nomic-embed-text"

def get_embedding(text: str) -> List[float]:
    """
    Generate an embedding vector for a given text using Ollama.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": text
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json()["embedding"]
    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama: {e}")
        return []

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """
    Calculate the cosine similarity between two vectors.
    Returns a value between -1 and 1.
    1 means identical direction (most similar).
    0 means orthogonal (unrelated).
    -1 means opposite direction.
    """
    vec1 = np.array(v1)
    vec2 = np.array(v2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
        
    return dot_product / (norm1 * norm2)

def main():
    print(f"--- Embeddings Demo with {MODEL_NAME} ---\n")
    
    # 1. Basic Embedding Generation
    text = "Artificial Intelligence is transforming the world."
    print(f"Generating embedding for: '{text}'")
    
    vector = get_embedding(text)
    
    if not vector:
        print("Failed to generate embedding. Is Ollama running?")
        return

    print(f"Vector dimension: {len(vector)}")
    print(f"First 5 dimensions: {vector[:5]}...\n")
    
    # 2. Semantic Similarity Demo
    print("--- Semantic Similarity Test ---")
    
    sentences = [
        "The cat sits on the mat.",             # Reference
        "A feline is resting on the rug.",      # Semantically similar
        "The dog chases the ball.",             # Different subject, similar structure
        "I love coding in Python.",             # Completely unrelated
        "Quantum physics is complex."           # Completely unrelated
    ]
    
    reference_sentence = sentences[0]
    reference_vector = get_embedding(reference_sentence)
    
    print(f"Reference: '{reference_sentence}'\n")
    
    results = []
    
    for sentence in sentences[1:]:
        vec = get_embedding(sentence)
        similarity = cosine_similarity(reference_vector, vec)
        results.append((sentence, similarity))
        
    # Sort by similarity (highest first)
    results.sort(key=lambda x: x[1], reverse=True)
    
    for sentence, score in results:
        print(f"Score: {score:.4f} | '{sentence}'")
        
    print("\nObservation:")
    print("- 'Feline on rug' should have the highest score (semantic match).")
    print("- 'Dog chases ball' might be next (structural match).")
    print("- 'Python' and 'Quantum physics' should be lowest.")

if __name__ == "__main__":
    main()
