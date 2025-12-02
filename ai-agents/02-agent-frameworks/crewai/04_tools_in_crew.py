import os
from crewai import Agent, Task, Crew, Process, LLM

# Disable OpenAI requirement
os.environ["OPENAI_API_KEY"] = "sk-dummy"

# =============================================================================
# 04 - Tools in Crew: Giving Agents Superpowers
# =============================================================================
#
# NOTE: This simplified version demonstrates the concept without custom tools.
# Custom tools require additional setup with CrewAI's tool system.
# For production use, refer to CrewAI documentation for tool integration.
# =============================================================================

def main():
    llm = LLM(
        model="ollama/qwen3:4b",
        base_url="http://127.0.0.1:11434"
    )

    # Agent without custom tools (simplified for demonstration)
    analyst = Agent(
        role='String Analyst',
        goal='Analyze text strings and provide insights',
        backstory="You are an expert at analyzing text. You can count characters and reverse strings mentally.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # Task that the agent can solve without external tools
    task = Task(
        description="""I have a secret word: 'Supercalifragilisticexpialidocious'.
        1. Count how many characters it has.
        2. Tell me what it would look like reversed.
        3. Provide both answers clearly.
        """,
        expected_output="The length and the reversed string.",
        agent=analyst
    )

    # Create Crew
    crew = Crew(
        agents=[analyst],
        tasks=[task],
        verbose=True
    )

    # Kickoff
    print("\n🧙 Starting String Analyst Crew...")
    result = crew.kickoff()

    print("\n\n" + "="*50)
    print("✨ FINAL RESULT")
    print("="*50)
    print(result)

if __name__ == "__main__":
    main()
