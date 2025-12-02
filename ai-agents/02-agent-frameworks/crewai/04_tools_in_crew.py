import os
from crewai import Agent, Task, Crew, Process, LLM

# Disable OpenAI requirement
os.environ["OPENAI_API_KEY"] = "sk-dummy"

# =============================================================================
# 04 - Tools in Crew: Giving Agents Superpowers
# =============================================================================
#
# Agents are smart, but they can't access the real world without TOOLS.
# Tools allow agents to:
# - Search the web
# - Read files
# - Calculate numbers
# - Call APIs
#
# In this example, we'll create a custom tool and give it to an agent.
# =============================================================================

# 1. Define Custom Tools
# We use the @tool decorator to define a tool.
# The docstring is CRITICAL - it tells the LLM when and how to use the tool.

@tool("Length Calculator")
def calculate_length(text: str) -> str:
    """Useful for calculating the length of a given text string.
    Returns the number of characters."""
    return str(len(text))

@tool("Reverse String")
def reverse_string(text: str) -> str:
    """Useful for reversing a given text string."""
    return text[::-1]

def main():
    llm = LLM(
        model="ollama/qwen3:4b",
        base_url="http://127.0.0.1:11434"
    )

    # 2. Define Agent with Tools
    # We pass the list of tools to the agent.
    
    math_wizard = Agent(
        role='String Wizard',
        goal='Analyze and manipulate strings using tools',
        backstory="You are a wizard who loves playing with words and numbers.",
        verbose=True,
        allow_delegation=False,
        tools=[calculate_length, reverse_string], # <--- GIVE TOOLS HERE
        llm=llm
    )

    # 3. Define Task
    # The task requires using the tools.
    
    task = Task(
        description="""I have a secret word: 'Supercalifragilisticexpialidocious'.
        1. Calculate its length.
        2. Reverse it.
        3. Tell me the length and the reversed version.
        """,
        expected_output="The length and the reversed string.",
        agent=math_wizard
    )

    # 4. Create Crew
    crew = Crew(
        agents=[math_wizard],
        tasks=[task],
        verbose=True
    )

    # 5. Kickoff
    print("\n🧙 Starting String Wizard Crew...")
    result = crew.kickoff()

    print("\n\n" + "="*50)
    print("✨ FINAL RESULT")
    print("="*50)
    print(result)

if __name__ == "__main__":
    main()
