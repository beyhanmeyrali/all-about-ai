import os
from crewai import Agent, Task, Crew, Process
from langchain_ollama import ChatOllama

# =============================================================================
# Comparison 03: CrewAI Implementation
# =============================================================================
#
# Task: Research -> Summarize -> Translate
# Approach: Multi-Agent Team
#
# This represents the "Organization" mental model.
# Manager -> Agent A -> Agent B
# =============================================================================

def main():
    # 1. Setup LLM
    llm = ChatOllama(
        model="qwen3:8b",
        base_url="http://localhost:11434",
        temperature=0.7
    )

    # 2. Define Agents
    researcher = Agent(
        role='Researcher',
        goal='Research topics thoroughly',
        backstory="You are a researcher.",
        verbose=True,
        llm=llm
    )

    writer = Agent(
        role='Writer',
        goal='Summarize and translate content',
        backstory="You are a linguist.",
        verbose=True,
        llm=llm
    )

    # 3. Define Tasks
    # CrewAI handles the data passing automatically between sequential tasks!
    
    task1 = Task(
        description="Generate a brief research report about: 'The history of Pizza'. Include 3 key facts.",
        expected_output="A research report.",
        agent=researcher
    )

    task2 = Task(
        description="Summarize the research report into one concise sentence.",
        expected_output="A one-sentence summary.",
        agent=writer
    )

    task3 = Task(
        description="Translate the summary into Spanish.",
        expected_output="The Spanish translation.",
        agent=writer
    )

    # 4. Create Crew
    crew = Crew(
        agents=[researcher, writer],
        tasks=[task1, task2, task3],
        verbose=True,
        process=Process.sequential
    )

    # 5. Run
    print(f"\n👨‍🍳 Running CrewAI Team...\n")
    result = crew.kickoff()

    print("="*50)
    print("FINAL OUTPUT")
    print("="*50)
    print(result)

if __name__ == "__main__":
    main()
