import os
from crewai import Agent, Task, Crew, Process
from langchain_ollama import ChatOllama

# =============================================================================
# 00 - CrewAI Basics: The "Hello World" of Multi-Agent Systems
# =============================================================================
#
# This script demonstrates the fundamental building blocks of CrewAI:
# 1. Agents: The workers
# 2. Tasks: The work to be done
# 3. Crew: The team orchestration
#
# We will use a local Ollama model (qwen3:8b) for all agents.
# =============================================================================

def main():
    # 1. Setup the Local LLM
    # CrewAI uses LangChain's LLM interface
    llm = ChatOllama(
        model="qwen3:8b",
        base_url="http://localhost:11434",
        temperature=0.7
    )

    print("\n🤖 Initializing CrewAI with Local LLM (qwen3:8b)...")

    # 2. Define Agents
    # Agents are the team members. They need a role, goal, and backstory.
    
    # Agent 1: The Researcher
    researcher = Agent(
        role='Tech Researcher',
        goal='Understand the basics of AI Agents',
        backstory="""You are an enthusiastic computer science student 
        who loves explaining complex concepts in simple terms. 
        You are currently learning about AI Agents.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # Agent 2: The Writer
    writer = Agent(
        role='Tech Writer',
        goal='Write a short tweet about AI Agents',
        backstory="""You are a social media influencer in the tech space. 
        You take technical concepts and turn them into engaging, 
        viral tweets with emojis.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # 3. Define Tasks
    # Tasks are specific assignments for agents.
    
    task1 = Task(
        description="""Research what an 'AI Agent' is. 
        Focus on the difference between a standard LLM (chatbot) and an Agent.
        Provide a bulleted list of 3 key differences.""",
        expected_output="A list of 3 key differences between LLMs and Agents.",
        agent=researcher
    )

    task2 = Task(
        description="""Using the research provided, write an engaging tweet 
        (max 280 chars) explaining what an AI Agent is. 
        Use emojis and make it sound exciting!""",
        expected_output="A single tweet string.",
        agent=writer
    )

    # 4. Define the Crew
    # The Crew coordinates the agents and tasks.
    
    crew = Crew(
        agents=[researcher, writer],
        tasks=[task1, task2],
        verbose=True,  # See the internal coordination
        process=Process.sequential  # Tasks are executed one after another
    )

    # 5. Kickoff!
    print("\n🚀 Starting the Crew...")
    result = crew.kickoff()

    print("\n\n" + "="*50)
    print("✅ FINAL RESULT")
    print("="*50)
    print(result)

if __name__ == "__main__":
    main()
