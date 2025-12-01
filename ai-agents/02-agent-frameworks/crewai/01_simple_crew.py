import os
from crewai import Agent, Task, Crew, Process
from langchain_ollama import ChatOllama

# =============================================================================
# 01 - Simple Crew: Market Analysis Team
# =============================================================================
#
# This example shows a practical use case: Market Analysis.
# We have two agents working together:
# 1. Market Analyst: Identifies trends
# 2. Investment Advisor: Gives advice based on those trends
#
# Concepts:
# - Context passing (Task 2 uses Task 1's output)
# - Specialized roles
# =============================================================================

def main():
    llm = ChatOllama(
        model="qwen3:8b",
        base_url="http://host.docker.internal:11434",
        temperature=0.7
    )

    # 1. Define Agents
    analyst = Agent(
        role='Market Analyst',
        goal='Analyze the current state of the AI market',
        backstory="""You are a veteran market analyst with 20 years of experience.
        You specialize in the tech sector and AI trends.
        You are concise and data-driven.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    advisor = Agent(
        role='Investment Advisor',
        goal='Recommend investment strategies based on market analysis',
        backstory="""You are a financial advisor who helps clients build wealth.
        You take complex market analysis and turn it into actionable advice.
        You are cautious but optimistic about AI.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # 2. Define Tasks
    # Task 1: Analysis
    analysis_task = Task(
        description="""Analyze the current trends in Artificial Intelligence for 2025.
        Identify 3 key growth areas and 2 potential risks.
        Assume the current year is 2025.""",
        expected_output="A brief market analysis report with 3 growth areas and 2 risks.",
        agent=analyst
    )

    # Task 2: Strategy
    # Note: In sequential process, this task automatically gets the context from previous tasks
    strategy_task = Task(
        description="""Based on the provided market analysis, suggest an investment strategy
        for a retail investor with $10,000.
        Suggest how to split the portfolio percentages based on the growth areas.""",
        expected_output="A clear investment strategy with portfolio allocation percentages.",
        agent=advisor,
        context=[analysis_task] # Explicitly stating dependency (optional in sequential, but good practice)
    )

    # 3. Create Crew
    financial_crew = Crew(
        agents=[analyst, advisor],
        tasks=[analysis_task, strategy_task],
        verbose=True,
        process=Process.sequential
    )

    # 4. Run
    print("\n💼 Starting Market Analysis Crew...")
    result = financial_crew.kickoff()

    print("\n\n" + "="*50)
    print("💰 FINAL INVESTMENT STRATEGY")
    print("="*50)
    print(result)

if __name__ == "__main__":
    main()
