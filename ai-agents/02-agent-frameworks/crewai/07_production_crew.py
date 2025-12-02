import os
from crewai import Agent, Task, Crew, Process, LLM

# Disable OpenAI requirement
os.environ["OPENAI_API_KEY"] = "sk-dummy"

# =============================================================================
# 07 - Production Crew: Content Creation Studio
# =============================================================================
#
# This is a complete, production-ready example of a Content Creation Studio.
# We have a full pipeline:
# 1. Researcher: Finds trending topics
# 2. Writer: Drafts the content
# 3. Editor: Polishes the content
# 4. Social Media Manager: Creates promotional tweets
#
# This demonstrates a complex sequential workflow.
# =============================================================================

def main():
    llm = LLM(
        model="ollama/qwen3:4b",
        base_url="http://127.0.0.1:11434"
    )

    # --- AGENTS ---
    
    researcher = Agent(
        role='Trend Researcher',
        goal='Identify the hottest topics in AI right now',
        backstory="You are a data-driven researcher who lives on Twitter and Reddit.",
        verbose=True,
        llm=llm
    )

    writer = Agent(
        role='Content Creator',
        goal='Write engaging blog posts about AI trends',
        backstory="You are a creative writer who can explain complex tech to anyone.",
        verbose=True,
        llm=llm
    )

    editor = Agent(
        role='Senior Editor',
        goal='Ensure all content is perfect and SEO-optimized',
        backstory="You are a meticulous editor. You hate passive voice and typos.",
        verbose=True,
        llm=llm
    )

    social_manager = Agent(
        role='Social Media Manager',
        goal='Promote content on social media',
        backstory="You are a viral marketing expert. You know how to write hooks.",
        verbose=True,
        llm=llm
    )

    # --- TASKS ---

    task1_research = Task(
        description="""Find 3 trending topics in 'Generative AI' for this week.
        For each topic, provide a brief summary and why it's trending.""",
        expected_output="A list of 3 trending topics with summaries.",
        agent=researcher
    )

    task2_write = Task(
        description="""Choose the most interesting topic from the research.
        Write a 400-word blog post about it.
        Include a catchy title and 3 main sections.""",
        expected_output="A complete 400-word blog post in Markdown format.",
        agent=writer
    )

    task3_edit = Task(
        description="""Review the blog post.
        1. Fix any grammatical errors.
        2. Ensure the tone is professional yet accessible.
        3. Add a 'Key Takeaways' section at the end.""",
        expected_output="The final, polished blog post.",
        agent=editor
    )

    task4_social = Task(
        description="""Create a Twitter thread (3 tweets) to promote this blog post.
        Include relevant hashtags and a call to action.""",
        expected_output="A Twitter thread string.",
        agent=social_manager
    )

    # --- CREW ---

    content_crew = Crew(
        agents=[researcher, writer, editor, social_manager],
        tasks=[task1_research, task2_write, task3_edit, task4_social],
        verbose=True,
        process=Process.sequential
    )

    # --- KICKOFF ---
    
    print("\n🎬 Starting Content Creation Studio...")
    result = content_crew.kickoff()

    print("\n\n" + "="*50)
    print("📦 FINAL PRODUCTION OUTPUT")
    print("="*50)
    print(result)

if __name__ == "__main__":
    main()
