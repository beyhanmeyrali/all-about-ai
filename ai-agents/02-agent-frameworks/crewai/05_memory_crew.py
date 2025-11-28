import os
from crewai import Agent, Task, Crew, Process
from langchain_ollama import ChatOllama

# =============================================================================
# 05 - Crew Memory: Long-Term Context
# =============================================================================
#
# CrewAI has a built-in memory system that allows agents to:
# 1. Remember past executions
# 2. Share knowledge between agents
# 3. Maintain context over long tasks
#
# This requires 'embedder' configuration usually, but for local setup,
# CrewAI uses OpenAI by default for embeddings.
# To use local embeddings, we need to configure 'memory=True' and specific embedder.
#
# For this simple example, we'll demonstrate the CONFIGURATION for memory.
# =============================================================================

def main():
    llm = ChatOllama(
        model="qwen3:8b",
        base_url="http://localhost:11434",
        temperature=0.7
    )

    # 1. Define Agents
    # Memory helps agents recall previous findings.
    
    researcher = Agent(
        role='Deep Researcher',
        goal='Research complex topics and remember details',
        backstory="You are a researcher with a photographic memory.",
        verbose=True,
        memory=True, # Enable memory for this agent
        llm=llm
    )

    writer = Agent(
        role='Writer',
        goal='Write stories based on research',
        backstory="You write compelling narratives.",
        verbose=True,
        memory=True,
        llm=llm
    )

    # 2. Define Tasks
    
    task1 = Task(
        description="Research the history of the 'Transformer' architecture in AI.",
        expected_output="A summary of the Transformer history.",
        agent=researcher
    )

    task2 = Task(
        description="Write a short story about a robot named 'Attention' based on the research.",
        expected_output="A short story.",
        agent=writer
    )

    # 3. Create Crew with Memory
    # We enable memory at the Crew level.
    # Note: In a real local setup, you'd configure the embedding model here.
    # For now, we'll rely on the default (or disable if no API key).
    
    # To truly use local embeddings with CrewAI, you often need:
    # embedder={
    #     "provider": "ollama",
    #     "config": {"model": "nomic-embed-text"}
    # }
    # This support varies by CrewAI version.
    
    crew = Crew(
        agents=[researcher, writer],
        tasks=[task1, task2],
        verbose=True,
        memory=True # <--- ENABLE MEMORY
    )

    # 4. Kickoff
    print("\n🧠 Starting Memory Crew...")
    try:
        result = crew.kickoff()
        print("\n\n" + "="*50)
        print("📝 FINAL RESULT")
        print("="*50)
        print(result)
    except Exception as e:
        print(f"\n[NOTE] Memory features might require an OpenAI API key or specific embedding config.")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
