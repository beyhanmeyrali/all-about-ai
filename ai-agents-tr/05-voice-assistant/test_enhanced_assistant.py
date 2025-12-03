"""
Test Enhanced Voice Assistant (without microphone)
Tests the RAG + Web Search capabilities
"""

import os
import requests
from crewai import Agent, Task, Crew, LLM
from qdrant_client import QdrantClient
from tools_web_search import WebSearchTool
from crewai.tools import BaseTool

# Disable OpenAI requirement
os.environ["OPENAI_API_KEY"] = "sk-dummy"

# Configuration
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "qwen3-embedding:0.6b"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_API_KEY = "qdrant_pass"
COLLECTION_NAME = "ai_agents_knowledge"


def get_embedding(text: str):
    """Generate embedding for the query using Ollama."""
    try:
        response = requests.post(OLLAMA_EMBED_URL, json={"model": EMBED_MODEL, "prompt": text})
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        print(f"⚠️  Error getting embedding: {e}")
        return []


class KnowledgeBaseTool(BaseTool):
    """Tool to search the knowledge base"""
    name: str = "Knowledge Base Search"
    description: str = (
        "Search the internal knowledge base for information about AI Agents, RAG, "
        "embeddings, LangChain, LangGraph, CrewAI, and related topics. "
        "Use this for technical documentation and concepts."
    )

    def _run(self, query: str) -> str:
        try:
            client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, api_key=QDRANT_API_KEY, https=False)
            query_vector = get_embedding(query)
            if not query_vector:
                return "Error: Could not generate embedding for query."

            from qdrant_client.models import PointStruct, Distance, VectorParams, models

            results = client.query_points(
                collection_name=COLLECTION_NAME,
                query=query_vector,
                limit=2
            ).points

            if not results:
                return "No relevant information found in the knowledge base."

            context_parts = []
            for hit in results:
                source = hit.payload.get('source', 'Unknown')
                content = hit.payload.get('content', '')
                context_parts.append(f"Source: {source}\n{content[:200]}...")

            return "\n\n".join(context_parts)

        except Exception as e:
            return f"Error: {str(e)}"


def test_tools():
    """Test both tools independently"""
    print("\n" + "=" * 60)
    print("TESTING INDIVIDUAL TOOLS")
    print("=" * 60)

    # Test Knowledge Base Tool
    print("\n1️⃣  Testing Knowledge Base Tool:")
    print("-" * 60)
    kb_tool = KnowledgeBaseTool()
    result = kb_tool._run("What is RAG?")
    print(result)

    # Test Web Search Tool
    print("\n2️⃣  Testing Web Search Tool:")
    print("-" * 60)
    web_tool = WebSearchTool()
    result = web_tool._run("Python programming", max_results=2)
    print(result)


def test_enhanced_agent():
    """Test the enhanced agent with both tools"""
    print("\n" + "=" * 60)
    print("TESTING ENHANCED AGENT")
    print("=" * 60)

    # Initialize LLM
    llm = LLM(
        model="ollama/qwen3:8b",
        base_url="http://127.0.0.1:11434"
    )

    # Create tools
    kb_tool = KnowledgeBaseTool()
    web_tool = WebSearchTool()

    # Create agent
    assistant_agent = Agent(
        role='AI Assistant',
        goal='Answer questions using knowledge base for technical topics and web search for current information',
        backstory=(
            "You are a helpful AI assistant with access to:\n"
            "1. Knowledge Base - Technical documentation about AI agents, RAG, embeddings\n"
            "2. Web Search - Current information, news, real-time data\n"
            "Use the appropriate tool and provide concise answers."
        ),
        verbose=True,
        tools=[kb_tool, web_tool],
        llm=llm
    )

    # Test queries
    test_queries = [
        {
            "query": "What is RAG?",
            "expected_tool": "Knowledge Base",
            "description": "Technical question - should use Knowledge Base"
        },
        {
            "query": "Latest news about Python programming",
            "expected_tool": "Web Search",
            "description": "Current information - should use Web Search"
        }
    ]

    for i, test in enumerate(test_queries, 1):
        print(f"\n{'=' * 60}")
        print(f"TEST {i}: {test['description']}")
        print(f"Query: \"{test['query']}\"")
        print(f"Expected Tool: {test['expected_tool']}")
        print("=" * 60)

        task = Task(
            description=f"Answer this question: {test['query']}",
            expected_output="A clear, concise answer.",
            agent=assistant_agent
        )

        crew = Crew(
            agents=[assistant_agent],
            tasks=[task],
            verbose=True
        )

        print("\n🤖 Agent Processing...\n")
        result = crew.kickoff()
        print(f"\n📝 Answer:\n{result}\n")


if __name__ == "__main__":
    print("\n🧪 Enhanced Voice Assistant Test Suite\n")

    # Check prerequisites
    print("Checking prerequisites...")
    try:
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, api_key=QDRANT_API_KEY, https=False)
        collections = client.get_collections()
        print(f"✅ Qdrant: {len(collections.collections)} collections")

        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        models = response.json().get("models", [])
        print(f"✅ Ollama: {len(models)} models")
    except Exception as e:
        print(f"❌ Prerequisites check failed: {e}")
        exit(1)

    # Run tests
    print("\n" + "=" * 60)
    choice = input("Run (1) Tool Tests, (2) Agent Tests, or (3) Both? [1/2/3]: ")
    print("=" * 60)

    if choice in ["1", "3"]:
        test_tools()

    if choice in ["2", "3"]:
        test_enhanced_agent()

    print("\n✅ Tests complete!\n")
