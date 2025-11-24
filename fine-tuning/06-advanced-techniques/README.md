# REFRAG: Efficient RAG Implementation

Based on the paper: [REFRAG: Improving RAG Efficiency](https://arxiv.org/abs/2509.01092)

## 🎯 What is REFRAG?

REFRAG optimizes Retrieval-Augmented Generation by eliminating unnecessary computations during decoding, achieving:
- **30x faster** time-to-first-token
- **16x larger** effective context length
- **Same performance** as standard RAG

## 🔧 Implementation for K11

### Basic RAG Setup

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class EfficientRAG:
    def __init__(self, model_name="microsoft/DialoGPT-medium"):
        # Load your fine-tuned model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        # Embedding model for retrieval
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Vector database (FAISS)
        self.index = None
        self.documents = []
        
    def build_index(self, documents):
        """Build FAISS index from documents"""
        self.documents = documents
        embeddings = self.embedder.encode(documents)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product
        self.index.add(embeddings.astype('float32'))
        
    def retrieve(self, query, k=5):
        """Retrieve top-k relevant documents"""
        query_embedding = self.embedder.encode([query])
        scores, indices = self.index.search(query_embedding.astype('float32'), k)
        
        retrieved_docs = [self.documents[i] for i in indices[0]]
        return retrieved_docs, scores[0]
    
    def refrag_generate(self, query, max_new_tokens=100):
        """REFRAG-optimized generation"""
        # 1. Retrieve relevant context
        context_docs, scores = self.retrieve(query, k=3)
        
        # 2. REFRAG optimization: Only process high-relevance context
        # Filter by relevance threshold
        threshold = scores.mean()
        filtered_context = [doc for doc, score in zip(context_docs, scores) 
                          if score > threshold]
        
        # 3. Compress context (key insight from REFRAG)
        context = " ".join(filtered_context[:2])  # Limit context length
        
        # 4. Create optimized prompt
        prompt = f"Context: {context}\n\nQuestion: {query}\nAnswer:"
        
        # 5. Generate with optimized context
        inputs = self.tokenizer.encode(prompt, return_tensors="pt", 
                                     truncation=True, max_length=1024)
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=max_new_tokens,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0][inputs.shape[1]:], 
                                       skip_special_tokens=True)
        return response.strip()

# Example usage
def main():
    # Initialize RAG system
    rag = EfficientRAG()
    
    # Sample knowledge base
    documents = [
        "Python is a high-level programming language known for its simplicity.",
        "Machine learning involves training algorithms on data to make predictions.",
        "Deep learning uses neural networks with multiple layers.",
        "Fine-tuning adapts pre-trained models to specific tasks.",
        "RAG combines retrieval with generation for better responses.",
        "REFRAG optimizes RAG by eliminating unnecessary computations.",
    ]
    
    # Build index
    rag.build_index(documents)
    
    # Query with REFRAG optimization
    query = "What is machine learning and how does it work?"
    response = rag.refrag_generate(query)
    print(f"Query: {query}")
    print(f"Response: {response}")

if __name__ == "__main__":
    main()
```

### Advanced: Context Caching

```python
class CachedREFRAG(EfficientRAG):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context_cache = {}
        self.kv_cache = {}  # Key-value cache for attention
        
    def cached_generate(self, query, max_new_tokens=100):
        """REFRAG with KV caching for even faster generation"""
        
        # Check if similar context was used recently
        query_hash = hash(query)
        
        if query_hash in self.context_cache:
            # Reuse cached context computation
            context = self.context_cache[query_hash]
        else:
            # Retrieve and cache
            context_docs, scores = self.retrieve(query, k=3)
            context = " ".join(context_docs[:2])
            self.context_cache[query_hash] = context
        
        prompt = f"Context: {context}\n\nQuestion: {query}\nAnswer:"
        
        # Use past_key_values for faster generation
        inputs = self.tokenizer.encode(prompt, return_tensors="pt")
        
        # Generate with caching
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=max_new_tokens,
                use_cache=True,  # Enable KV caching
                temperature=0.7,
                do_sample=True
            )
        
        response = self.tokenizer.decode(outputs[0][inputs.shape[1]:], 
                                       skip_special_tokens=True)
        return response.strip()
```

### Memory-Efficient Vector DB

```python
import pickle
from pathlib import Path

class MemoryEfficientRAG:
    """Optimized for K11's memory constraints"""
    
    def __init__(self, cache_dir="./rag_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Use smaller, faster models
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')  # 22MB
        
    def save_index(self, filename="vector_index"):
        """Save index to disk to free memory"""
        if self.index is not None:
            faiss.write_index(self.index, str(self.cache_dir / f"{filename}.index"))
            
        with open(self.cache_dir / f"{filename}_docs.pkl", 'wb') as f:
            pickle.dump(self.documents, f)
    
    def load_index(self, filename="vector_index"):
        """Load index from disk"""
        index_path = self.cache_dir / f"{filename}.index"
        docs_path = self.cache_dir / f"{filename}_docs.pkl"
        
        if index_path.exists() and docs_path.exists():
            self.index = faiss.read_index(str(index_path))
            with open(docs_path, 'rb') as f:
                self.documents = pickle.load(f)
            return True
        return False
```

## 🚀 Integration with Your Fine-tuned Models

```python
# Use REFRAG with your fine-tuned models
def integrate_with_finetuned():
    # Load your fine-tuned model from earlier tutorials
    from peft import PeftModel
    
    # Base model
    base_model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
    
    # Your fine-tuned adapter
    model = PeftModel.from_pretrained(base_model, "./your-lora-adapter")
    
    # Create REFRAG system with your model
    rag = EfficientRAG()
    rag.model = model  # Replace with your fine-tuned model
    
    return rag
```

## 💡 K11-Specific Optimizations

1. **Memory Management**: Use smaller embedding models
2. **Batch Processing**: Process multiple queries together
3. **Disk Caching**: Store indexes on fast NVMe storage
4. **AMD GPU**: Use ROCm for embedding computations

## 🎯 Performance Tips

- **Context Length**: Keep retrieved context under 1024 tokens
- **Relevance Filtering**: Only use top 2-3 most relevant documents
- **Caching**: Cache embeddings and KV pairs
- **Quantization**: Use 4-bit quantized models for memory efficiency

This combines beautifully with your fine-tuning work - you can RAG-enable any model you fine-tune!