import os
import requests
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool
from qdrant_client import QdrantClient
from typing import Optional

# Disable OpenAI requirement
os.environ["OPENAI_API_KEY"] = "sk-dummy"

# Configuration
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "qwen3-embedding:0.6b"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "ai_agents_knowledge"

def get_embedding(text: str):
    """Generate embedding for the query using Ollama."""
    try:
        response = requests.post(OLLAMA_EMBED_URL, json={"model": EMBED_MODEL, "prompt": text})
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return []

class KnowledgeBaseTool(BaseTool):
    name: str = "Knowledge Base Search"
    description: str = "Useful for searching the internal knowledge base for information about AI Agents, RAG, and related topics."

    def _run(self, query: str) -> str:
        try:
            # Connect to Qdrant
            client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, https=False)
            
            # Generate embedding
            query_vector = get_embedding(query)
            if not query_vector:
                return "Error: Could not generate embedding for query."

            # Search Qdrant
            results = client.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_vector,
                limit=3
            )
            
            if not results:
                return "No relevant information found in the knowledge base."

            # Format results
            context_parts = []
            for hit in results:
                source = hit.payload.get('source', 'Unknown')
                content = hit.payload.get('content', '')
                context_parts.append(f"Source: {source}\nContent: {content}\n")
                
            return "\n".join(context_parts)

        except Exception as e:
            return f"Error accessing knowledge base: {str(e)}. Make sure Qdrant is running."

def main():
    # 1. Setup LLM (using 8b for better stability with tools)
    llm = LLM(
        model="ollama/qwen3:8b",
        base_url="http://127.0.0.1:11434"
    )

    # 2. Define Agent with the RAG Tool
    knowledge_agent = Agent(
        role='Knowledge Specialist',
        goal='Answer questions using the internal knowledge base',
        backstory="You are an expert at retrieving and synthesizing information from the company's knowledge base.",
        verbose=True,
        tools=[KnowledgeBaseTool()],
        llm=llm
    )

    # 3. Define Task
    task = Task(
        description="What is RAG (Retrieval-Augmented Generation)? Search the knowledge base and provide a clear explanation.",
        expected_output="A clear explanation of RAG based on the retrieved context.",
        agent=knowledge_agent
    )

    # 4. Create Crew
    crew = Crew(
        agents=[knowledge_agent],
        tasks=[task],
        verbose=True
    )

    # 5. Kickoff
    print("\n🔍 Starting RAG Agent...")
    result = crew.kickoff()

    print("\n\n" + "="*50)
    print("📝 FINAL ANSWER")
    print("="*50)
    print(result)

if __name__ == "__main__":
    main()
