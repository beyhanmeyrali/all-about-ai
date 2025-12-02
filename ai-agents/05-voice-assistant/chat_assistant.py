"""
Interactive Chat Assistant (Text-Based)
Test the enhanced assistant without microphone/speakers
Uses keyboard input instead of voice
"""

import os
import requests
from crewai import Agent, Task, Crew, LLM
from tools_web_search import WebSearchTool
from crewai.tools import BaseTool

# Disable OpenAI requirement
os.environ["OPENAI_API_KEY"] = "sk-dummy"

# Configuration
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "qwen3-embedding:0.6b"


class SimplifiedKnowledgeBaseTool(BaseTool):
    """
    Simplified Knowledge Base tool (without Qdrant dependency)
    Returns predefined answers for common technical questions
    """
    name: str = "Knowledge Base Search"
    description: str = (
        "Search the internal knowledge base for information about AI Agents, RAG, "
        "embeddings, LangChain, LangGraph, CrewAI, and related topics. "
        "Use this for technical documentation and concepts."
    )

    def _run(self, query: str) -> str:
        """Simple knowledge base with predefined answers"""
        query_lower = query.lower()

        # Predefined knowledge
        knowledge = {
            "rag": (
                "RAG (Retrieval-Augmented Generation) is a technique that enhances LLM responses "
                "by retrieving relevant documents from a knowledge base before generating an answer. "
                "It combines the power of vector search with language models to provide accurate, "
                "context-aware responses based on your own data."
            ),
            "embedding": (
                "Embeddings are numerical vector representations of text that capture semantic meaning. "
                "They allow us to measure similarity between pieces of text mathematically. "
                "In RAG systems, embeddings enable semantic search - finding relevant documents "
                "based on meaning rather than just keyword matching."
            ),
            "ai agent": (
                "AI Agents are autonomous systems that can perceive their environment, make decisions, "
                "and take actions to achieve specific goals. In the context of LLMs, agents can use "
                "tools, plan multi-step tasks, and interact with external systems to accomplish complex objectives."
            ),
            "crewai": (
                "CrewAI is a framework for building multi-agent AI systems. It allows you to define "
                "specialized agents with different roles, goals, and tools, which can collaborate "
                "to solve complex tasks through delegation and cooperation."
            ),
            "langchain": (
                "LangChain is a framework for developing applications powered by language models. "
                "It provides tools for chaining LLM calls, integrating with external data sources, "
                "managing memory, and building complex AI workflows."
            ),
            "vector database": (
                "Vector databases like Qdrant store and retrieve high-dimensional embeddings efficiently. "
                "They enable fast similarity search, which is essential for RAG systems to find "
                "relevant documents quickly from large knowledge bases."
            )
        }

        # Search for matching knowledge
        for key, value in knowledge.items():
            if key in query_lower:
                return f"From Knowledge Base:\n{value}"

        return "No specific information found in knowledge base for this query. Try using web search for current information."


class ChatAssistant:
    """Interactive chat assistant with Knowledge Base + Web Search"""

    def __init__(self):
        """Initialize the chat assistant"""
        print("🤖 Initializing Chat Assistant...")
        print("=" * 60)

        # Initialize LLM
        print("📥 Connecting to Ollama (qwen3:8b)...")
        self.llm = LLM(
            model="ollama/qwen3:8b",
            base_url="http://127.0.0.1:11434"
        )

        # Create tools
        print("📥 Loading tools...")
        self.kb_tool = SimplifiedKnowledgeBaseTool()
        self.web_tool = WebSearchTool()

        # Create agent
        print("📥 Creating AI agent...")
        self.agent = Agent(
            role='AI Assistant',
            goal='Answer user questions using knowledge base for technical topics and web search for current information',
            backstory=(
                "You are a helpful AI assistant with access to:\n"
                "1. Knowledge Base - Technical documentation about AI agents, RAG, embeddings, frameworks\n"
                "2. Web Search - Current information, news, weather, prices, real-time data\n\n"
                "Instructions:\n"
                "- For technical questions about AI/ML concepts → use Knowledge Base Search\n"
                "- For current events, news, weather, prices → use Web Search\n"
                "- Provide concise, helpful answers (2-3 sentences)\n"
                "- If you use a tool, briefly mention what you found"
            ),
            verbose=True,
            tools=[self.kb_tool, self.web_tool],
            llm=self.llm,
            allow_delegation=False
        )

        print("=" * 60)
        print("✅ Chat Assistant Ready!")
        print()

    def ask(self, question: str) -> str:
        """Ask a question and get an answer"""
        try:
            task = Task(
                description=f"Answer this question: {question}",
                expected_output="A clear, concise answer to the user's question.",
                agent=self.agent
            )

            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                verbose=True
            )

            result = crew.kickoff()
            return str(result)

        except Exception as e:
            return f"Error: {str(e)}"

    def chat(self):
        """Start interactive chat session"""
        print("\n💬 Interactive Chat Mode")
        print("=" * 60)
        print("Ask me anything! Type 'quit' or 'exit' to stop.")
        print()
        print("Example questions:")
        print("  • 'What is RAG?' (uses Knowledge Base)")
        print("  • 'Latest Python news' (uses Web Search)")
        print("  • 'Explain embeddings' (uses Knowledge Base)")
        print("  • 'Current weather forecast' (uses Web Search)")
        print("=" * 60)
        print()

        conversation_count = 0

        while True:
            try:
                # Get user input
                question = input("\n💬 You: ").strip()

                # Check for exit
                if question.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("\n👋 Goodbye! Thanks for chatting!")
                    break

                if not question:
                    continue

                conversation_count += 1
                print(f"\n🤖 Assistant is thinking...\n")

                # Get answer
                answer = self.ask(question)

                # Display answer
                print(f"\n{'=' * 60}")
                print(f"🤖 Assistant:")
                print(answer)
                print("=" * 60)

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

        print(f"\n📊 Conversation stats: {conversation_count} questions answered")


def main():
    """Main function"""
    print("\n🎙️  Interactive Chat Assistant (Text-Based)\n")

    # Check Ollama
    try:
        print("Checking Ollama connection...")
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama: {len(models)} models available")

            # Check if qwen3:8b is available
            model_names = [m['name'] for m in models]
            if any('qwen3:8b' in name for name in model_names):
                print("✅ qwen3:8b model found")
            else:
                print("⚠️  qwen3:8b model not found. You may need to run: ollama pull qwen3:8b")
        else:
            print(f"❌ Ollama returned status {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("Please start Ollama with: ollama serve")
        return

    print()

    # Create and start assistant
    assistant = ChatAssistant()

    # Start chat
    assistant.chat()


if __name__ == "__main__":
    main()
