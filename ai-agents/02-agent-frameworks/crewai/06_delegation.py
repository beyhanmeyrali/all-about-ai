import os
from crewai import Agent, Task, Crew, Process
from langchain_ollama import ChatOllama

# =============================================================================
# 06 - Delegation: Agents Helping Agents
# =============================================================================
#
# One of the most powerful features of CrewAI is DELEGATION.
# If an agent realizes it can't do something, or needs help,
# it can delegate a sub-task to another agent!
#
# This happens automatically if 'allow_delegation=True'.
# =============================================================================

def main():
    llm = ChatOllama(
        model="qwen3:8b",
        base_url="http://host.docker.internal:11434",
        temperature=0.7
    )

    # 1. Define Agents
    
    # The Manager CAN delegate
    manager = Agent(
        role='Project Manager',
        goal='Coordinate the team to solve a riddle',
        backstory="You are a smart manager. You know you can't solve everything alone.",
        verbose=True,
        allow_delegation=True, # <--- CAN DELEGATE
        llm=llm
    )

    # The Specialist CANNOT delegate (they do the work)
    riddle_solver = Agent(
        role='Riddle Master',
        goal='Solve complex riddles',
        backstory="You are an expert at lateral thinking and riddles.",
        verbose=True,
        allow_delegation=False, # <--- WORKER
        llm=llm
    )

    # 2. Define Task
    # We give the task to the MANAGER.
    # The Manager should realize they need the Riddle Master's help.
    
    task = Task(
        description="""Solve this riddle: 
        'I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?'
        
        Once solved, explain the reasoning.
        """,
        expected_output="The answer to the riddle and the explanation.",
        agent=manager # Assigned to Manager
    )

    # 3. Create Crew
    crew = Crew(
        agents=[manager, riddle_solver],
        tasks=[task],
        verbose=True
    )

    # 4. Kickoff
    print("\n🤝 Starting Delegation Crew...")
    result = crew.kickoff()

    print("\n\n" + "="*50)
    print("💡 FINAL ANSWER")
    print("="*50)
    print(result)

if __name__ == "__main__":
    main()
