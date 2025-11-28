#!/usr/bin/env python3
"""
Example 05: Sequential Chains - Multi-Step Workflows
=====================================================

Learn how to chain multiple LLM calls together for complex workflows!

What you'll learn:
- Sequential processing (step1 → step2 → step3)
- Data passing between steps
- LCEL (LangChain Expression Language) - Modern approach
- Transform chains for data processing
- Production pipeline patterns

This is how you build REAL multi-step agents!

Author: Beyhan MEYRALI
"""

from typing import Dict, Any, List
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


# =============================================================================
# PART 1: Simple Sequential Chain (LCEL Style)
# =============================================================================

class SimpleSequentialPipeline:
    """
    Simple sequential pipeline using LCEL (LangChain Expression Language).

    This is the MODERN way to chain operations in LangChain 1.1.0+
    Uses the pipe operator (|) to chain components.
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize the pipeline."""
        print(f"\n[INIT] Creating SimpleSequentialPipeline with {model}...")
        self.llm = OllamaLLM(model=model, temperature=0.7)
        print("[INIT] ✅ Pipeline ready!")

    def create_story_pipeline(self):
        """
        Create a 2-step pipeline: Generate idea → Write story

        Returns:
            Runnable chain
        """
        print("\n[PIPELINE] Building story generation pipeline...")

        # Step 1: Generate story idea
        idea_prompt = PromptTemplate.from_template(
            "Generate a creative {genre} story idea in one sentence."
        )

        # Step 2: Expand idea into full story
        story_prompt = PromptTemplate.from_template(
            "Take this story idea and write a short 3-paragraph story:\n\n{idea}"
        )

        # Chain using LCEL (pipe operator)
        # idea_prompt | llm → generates idea
        # Then pass that to story_prompt | llm → generates full story

        chain = (
            idea_prompt
            | self.llm
            | (lambda idea: {"idea": idea})
            | story_prompt
            | self.llm
            | StrOutputParser()
        )

        print("[PIPELINE] ✅ Pipeline: idea_prompt | llm | story_prompt | llm")
        return chain

    def run(self, genre: str) -> str:
        """Run the pipeline."""
        print(f"\n[RUN] Generating {genre} story...")

        chain = self.create_story_pipeline()
        result = chain.invoke({"genre": genre})

        print(f"\n[RESULT] Story generated!")
        return result


# =============================================================================
# PART 2: Multi-Step Data Processing Pipeline
# =============================================================================

class DataProcessingPipeline:
    """
    Multi-step pipeline for data extraction and processing.

    Steps: Extract → Analyze → Summarize
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize pipeline."""
        self.llm = OllamaLLM(model=model, temperature=0.3)

    def create_analysis_pipeline(self):
        """
        Create 3-step analysis pipeline.

        Step 1: Extract key points
        Step 2: Analyze sentiment
        Step 3: Create summary
        """

        # Step 1: Extract key points
        extract_prompt = PromptTemplate.from_template(
            """Extract the key points from this text as a bullet list:

Text: {text}

Key Points:"""
        )

        # Step 2: Analyze sentiment
        sentiment_prompt = PromptTemplate.from_template(
            """Analyze the sentiment of these key points:

{key_points}

Sentiment (positive/negative/neutral):"""
        )

        # Step 3: Create summary
        summary_prompt = PromptTemplate.from_template(
            """Create a final summary:

Key Points: {key_points}
Sentiment: {sentiment}

Summary:"""
        )

        # Build pipeline
        def extract_step(input_dict):
            """Step 1: Extract key points."""
            result = (extract_prompt | self.llm).invoke(input_dict)
            return {"key_points": result, "text": input_dict["text"]}

        def sentiment_step(input_dict):
            """Step 2: Analyze sentiment."""
            result = (sentiment_prompt | self.llm).invoke(input_dict)
            return {
                "key_points": input_dict["key_points"],
                "sentiment": result
            }

        def summary_step(input_dict):
            """Step 3: Create summary."""
            result = (summary_prompt | self.llm | StrOutputParser()).invoke(input_dict)
            return result

        # Chain them together
        from langchain_core.runnables import RunnableLambda

        chain = (
            RunnableLambda(extract_step)
            | RunnableLambda(sentiment_step)
            | RunnableLambda(summary_step)
        )

        return chain

    def analyze(self, text: str) -> str:
        """Analyze text through the pipeline."""
        print("\n[PIPELINE] Running 3-step analysis...")
        print("  Step 1: Extracting key points...")
        print("  Step 2: Analyzing sentiment...")
        print("  Step 3: Creating summary...")

        chain = self.create_analysis_pipeline()
        result = chain.invoke({"text": text})

        return result


# =============================================================================
# PART 3: Production Pipeline with Error Handling
# =============================================================================

class ProductionPipeline:
    """
    Production-grade pipeline with error handling and logging.
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize production pipeline."""
        self.llm = OllamaLLM(model=model, temperature=0.5)

    def create_content_pipeline(self):
        """
        Content creation pipeline: Research → Outline → Write → Edit
        """

        # Step 1: Research
        research_prompt = PromptTemplate.from_template(
            """Research the topic '{topic}' and list 3 key facts.

Facts:"""
        )

        # Step 2: Create outline
        outline_prompt = PromptTemplate.from_template(
            """Based on these facts, create a blog post outline:

{facts}

Outline:"""
        )

        # Step 3: Write content
        write_prompt = PromptTemplate.from_template(
            """Write a blog post following this outline:

{outline}

Blog Post:"""
        )

        # Build pipeline with error handling
        def safe_step(prompt, step_name):
            """Wrapper for safe execution."""
            def execute(input_dict):
                try:
                    print(f"  [{step_name}] Processing...")
                    result = (prompt | self.llm).invoke(input_dict)
                    print(f"  [{step_name}] ✅ Complete")
                    return result
                except Exception as e:
                    print(f"  [{step_name}] ❌ Error: {e}")
                    return f"Error in {step_name}: {str(e)}"
            return execute

        # Chain with error handling
        from langchain_core.runnables import RunnableLambda

        chain = (
            RunnableLambda(lambda x: {"topic": x["topic"]})
            | RunnableLambda(safe_step(research_prompt, "RESEARCH"))
            | (lambda facts: {"facts": facts})
            | RunnableLambda(safe_step(outline_prompt, "OUTLINE"))
            | (lambda outline: {"outline": outline})
            | RunnableLambda(safe_step(write_prompt, "WRITE"))
            | StrOutputParser()
        )

        return chain

    def create_content(self, topic: str) -> str:
        """Create content through the pipeline."""
        print(f"\n[PRODUCTION] Creating content for: {topic}")

        chain = self.create_content_pipeline()
        result = chain.invoke({"topic": topic})

        return result


# =============================================================================
# DEMOS
# =============================================================================

def demo_simple_sequential():
    """Demo: Simple 2-step pipeline."""
    print("\n" + "="*70)
    print("DEMO 1: Simple Sequential Pipeline")
    print("="*70)

    pipeline = SimpleSequentialPipeline()
    story = pipeline.run("science fiction")

    print("\n[STORY]:")
    print("-" * 70)
    print(story)
    print("-" * 70)


def demo_data_processing():
    """Demo: Multi-step data processing."""
    print("\n" + "="*70)
    print("DEMO 2: Data Processing Pipeline")
    print("="*70)

    text = """
    The new AI product launch was a huge success! Customer feedback has been
    overwhelmingly positive. Sales exceeded expectations by 150%. The team
    worked incredibly hard and delivered an amazing result. Some minor bugs
    were reported but quickly fixed.
    """

    pipeline = DataProcessingPipeline()
    summary = pipeline.analyze(text)

    print("\n[SUMMARY]:")
    print("-" * 70)
    print(summary)
    print("-" * 70)


def demo_production_pipeline():
    """Demo: Production pipeline."""
    print("\n" + "="*70)
    print("DEMO 3: Production Content Pipeline")
    print("="*70)

    pipeline = ProductionPipeline()
    content = pipeline.create_content("The benefits of AI agents")

    print("\n[CONTENT]:")
    print("-" * 70)
    print(content)
    print("-" * 70)


def main():
    """Main entry point."""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║         Example 05: Sequential Chains                             ║
║                                                                   ║
║  This demonstrates:                                              ║
║  • LCEL (LangChain Expression Language) - Modern approach       ║
║  • Piping operations with | operator                            ║
║  • Multi-step sequential workflows                              ║
║  • Data transformation between steps                            ║
║  • Production pipeline patterns                                  ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Run demos
    demo_simple_sequential()
    demo_data_processing()
    demo_production_pipeline()

    # Summary
    print("\n" + "="*70)
    print("✅ COMPLETE!")
    print("="*70)
    print("\n🎓 What you learned:")
    print("  1. LCEL (LangChain Expression Language) - Modern chaining")
    print("  2. Pipe operator (|) for sequential operations")
    print("  3. Multi-step workflows (extract → analyze → summarize)")
    print("  4. Data passing between chain steps")
    print("  5. Production patterns with error handling")
    print("\n📖 Key Concepts:")
    print("  • Sequential = One step after another")
    print("  • LCEL = Modern LangChain chaining (not deprecated)")
    print("  • Pipe (|) = Connect components together")
    print("  • Transform = Modify data between steps")
    print("\n💡 LCEL vs Old SequentialChain:")
    print("  OLD (deprecated): SequentialChain([chain1, chain2])")
    print("  NEW (LCEL):       prompt | llm | parser")
    print("  LCEL is simpler, more flexible, and not deprecated!")
    print("\n➡️  Next: python 06_router_chains.py")
    print("="*70)


if __name__ == "__main__":
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("[WARNING] Ollama might not be running correctly")
    except:
        print("[ERROR] Cannot connect to Ollama!")
        print("  Fix: ollama serve")
        exit(1)

    main()
