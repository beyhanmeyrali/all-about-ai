import os
from crewai import Agent, Task, Crew, Process, LLM

# Disable OpenAI requirement
os.environ["OPENAI_API_KEY"] = "sk-dummy"

# =============================================================================
# 03 - Hierarchical Crew: Manager & Workers
# =============================================================================
#
# In a Hierarchical process, a "Manager" agent automatically coordinates the crew.
# The Manager:
# 1. Receives the high-level goal
# 2. Breaks it down into sub-tasks
# 3. Delegates tasks to the most suitable agents
# 4. Reviews and aggregates the results
#
# Note: This requires a "manager_llm" (can be the same as agent llm).
# =============================================================================

def main():
    llm = LLM(
        model="ollama/qwen3:4b",
        base_url="http://127.0.0.1:11434"
    )

    # 1. Define Workers (No Manager here - CrewAI creates one!)
    # We just define the specialists.
    
    researcher = Agent(
        role='Senior Researcher',
        goal='Conduct in-depth research on given topics',
        backstory="You are an expert researcher. You find facts and verify sources.",
        verbose=True,
        allow_delegation=False, # Workers usually don't delegate in this setup
        llm=llm
    )

    writer = Agent(
        role='Senior Writer',
        goal='Write high-quality content based on research',
        backstory="You are a skilled writer. You create engaging and clear content.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    editor = Agent(
        role='Chief Editor',
        goal='Ensure content quality and consistency',
        backstory="You are a strict editor. You check for tone, style, and accuracy.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # 2. Define the High-Level Task
    # In hierarchical mode, we give a complex task that needs coordination.
    
    project_task = Task(
        description="""Produce a comprehensive blog post about 'The Future of Local LLMs'.
        1. Research the current state of local LLMs (Ollama, Llama 3, etc.).
        2. Write a draft blog post (approx 500 words).
        3. Edit the post for clarity and professional tone.
        """,
        expected_output="A polished, ready-to-publish blog post.",
        # We don't assign a specific agent! The Manager will decide.
    )

    # 3. Create the Hierarchical Crew
    crew = Crew(
        agents=[researcher, writer, editor],
        tasks=[project_task],
        verbose=True,
        process=Process.hierarchical, # <--- KEY CHANGE
        manager_llm=llm # The brain of the manager
    )

    # 4. Kickoff
    print("\n👑 Starting Hierarchical Crew...")
    result = crew.kickoff()

    print("\n\n" + "="*50)
    print("📄 FINAL BLOG POST")
    print("="*50)
    print(result)

if __name__ == "__main__":
    main()
