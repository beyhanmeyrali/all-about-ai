#!/usr/bin/env python3
"""
Example 02: Advanced Prompt Templates
======================================

Master prompt templates - the foundation of effective AI agents.

What you'll learn:
- Different types of prompt templates
- Variable substitution
- Few-shot prompting
- Chat prompts vs completion prompts
- Best practices for prompt engineering

This builds on 01_basic_chain.py by showing advanced prompting techniques.

Author: Beyhan MEYRALI
"""

from typing import List, Dict, Any
from langchain_ollama import OllamaLLM
from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    FewShotPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_classic.chains import LLMChain


class PromptTemplateExamples:
    """
    Comprehensive examples of different prompt template types.

    This class demonstrates all major prompt template patterns used in production.
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize with an LLM."""
        print(f"\n[INIT] Creating LLM: {model}")
        self.llm = OllamaLLM(model=model, temperature=0.7)

    def example_1_basic_template(self):
        """Basic template with single variable."""
        print("\n" + "="*70)
        print("EXAMPLE 1: Basic Template (Single Variable)")
        print("="*70)

        template = "Tell me a {adjective} fact about {topic}."

        prompt = PromptTemplate(
            template=template,
            input_variables=["adjective", "topic"]
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)

        # Test with different inputs
        result1 = chain.run(adjective="interesting", topic="ocean")
        result2 = chain.run(adjective="surprising", topic="quantum physics")

        print(f"\n✅ Result 1: {result1[:100]}...")
        print(f"✅ Result 2: {result2[:100]}...")

    def example_2_multiline_template(self):
        """Complex multi-line template."""
        print("\n" + "="*70)
        print("EXAMPLE 2: Multi-line Template (Better Structure)")
        print("="*70)

        template = """You are an expert {role}.

Task: {task}

Context:
{context}

Requirements:
1. Be concise
2. Use examples
3. Be practical

Please provide your answer:"""

        prompt = PromptTemplate(
            template=template,
            input_variables=["role", "task", "context"]
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)

        result = chain.run(
            role="Python developer",
            task="Explain list comprehensions",
            context="Teaching beginners who know basic for loops"
        )

        print(f"\n✅ Result: {result[:200]}...")

    def example_3_few_shot_prompting(self):
        """Few-shot learning with examples."""
        print("\n" + "="*70)
        print("EXAMPLE 3: Few-Shot Prompting (Learning from Examples)")
        print("="*70)

        # Define examples
        examples = [
            {
                "input": "happy",
                "output": "joyful, delighted, cheerful"
            },
            {
                "input": "sad",
                "output": "melancholy, sorrowful, dejected"
            },
        ]

        # Create example template
        example_template = """
Input: {input}
Output: {output}
"""

        example_prompt = PromptTemplate(
            template=example_template,
            input_variables=["input", "output"]
        )

        # Create few-shot template
        few_shot_prompt = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix="Give me 3 synonyms for each word:\n",
            suffix="\nInput: {word}\nOutput:",
            input_variables=["word"]
        )

        chain = LLMChain(llm=self.llm, prompt=few_shot_prompt)

        # Test with new word
        result = chain.run(word="angry")

        print("\n[PROMPT SENT]:")
        print(few_shot_prompt.format(word="angry"))
        print(f"\n✅ Result: {result}")

    def example_4_chat_template(self):
        """Chat-style prompts with system and user messages."""
        print("\n" + "="*70)
        print("EXAMPLE 4: Chat Template (System + User Messages)")
        print("="*70)

        chat_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are a {role}. You always respond in {style} style."
            ),
            HumanMessagePromptTemplate.from_template(
                "{user_message}"
            )
        ])

        chain = LLMChain(llm=self.llm, prompt=chat_prompt)

        result = chain.run(
            role="pirate captain",
            style="pirate",
            user_message="What's the weather like today?"
        )

        print(f"\n✅ Result: {result[:200]}...")

    def example_5_conditional_template(self):
        """Template with conditional logic."""
        print("\n" + "="*70)
        print("EXAMPLE 5: Conditional Template (Dynamic Content)")
        print("="*70)

        def create_conditional_prompt(include_examples: bool) -> str:
            """Create prompt with optional examples section."""
            base = "Answer the following question: {question}\n"

            if include_examples:
                base += "\nProvide 2-3 examples in your answer.\n"

            return base

        # With examples
        prompt_with_ex = PromptTemplate(
            template=create_conditional_prompt(True),
            input_variables=["question"]
        )

        # Without examples
        prompt_without_ex = PromptTemplate(
            template=create_conditional_prompt(False),
            input_variables=["question"]
        )

        chain_with = LLMChain(llm=self.llm, prompt=prompt_with_ex)
        chain_without = LLMChain(llm=self.llm, prompt=prompt_without_ex)

        question = "What is recursion in programming?"

        result_with = chain_with.run(question=question)
        result_without = chain_without.run(question=question)

        print(f"\n✅ With examples: {result_with[:150]}...")
        print(f"\n✅ Without examples: {result_without[:150]}...")


class ProductionPromptAgent:
    """
    Production-ready agent with optimized prompts.

    This demonstrates best practices for production prompt engineering.
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize the agent."""
        self.llm = OllamaLLM(model=model, temperature=0.7)

        # Different prompts for different tasks
        self.prompts = {
            "summarize": self._create_summarize_prompt(),
            "extract": self._create_extract_prompt(),
            "classify": self._create_classify_prompt(),
        }

        # Create chains
        self.chains = {
            name: LLMChain(llm=self.llm, prompt=prompt)
            for name, prompt in self.prompts.items()
        }

    def _create_summarize_prompt(self) -> PromptTemplate:
        """Prompt for summarization."""
        template = """Summarize the following text in {num_sentences} sentences.

Text:
{text}

Summary:"""
        return PromptTemplate(
            template=template,
            input_variables=["text", "num_sentences"]
        )

    def _create_extract_prompt(self) -> PromptTemplate:
        """Prompt for information extraction."""
        template = """Extract {information_type} from the following text.

Text:
{text}

Extracted {information_type}:"""
        return PromptTemplate(
            template=template,
            input_variables=["text", "information_type"]
        )

    def _create_classify_prompt(self) -> PromptTemplate:
        """Prompt for classification."""
        template = """Classify the following text into one of these categories:
{categories}

Text:
{text}

Category:"""
        return PromptTemplate(
            template=template,
            input_variables=["text", "categories"]
        )

    def summarize(self, text: str, num_sentences: int = 2) -> str:
        """Summarize text."""
        return self.chains["summarize"].run(
            text=text,
            num_sentences=num_sentences
        )

    def extract(self, text: str, information_type: str) -> str:
        """Extract information from text."""
        return self.chains["extract"].run(
            text=text,
            information_type=information_type
        )

    def classify(self, text: str, categories: List[str]) -> str:
        """Classify text."""
        return self.chains["classify"].run(
            text=text,
            categories=", ".join(categories)
        )


def demo_production_agent():
    """Demonstrate production agent."""
    print("\n" + "="*70)
    print("DEMO: Production Agent with Multiple Prompt Types")
    print("="*70)

    agent = ProductionPromptAgent()

    # Test summarization
    text = """
    Artificial Intelligence (AI) is transforming how we work and live.
    Machine learning algorithms can now recognize patterns in data,
    make predictions, and even create new content. Deep learning,
    a subset of machine learning, uses neural networks to process
    information in ways similar to the human brain.
    """

    print("\n[1] Summarization:")
    summary = agent.summarize(text, num_sentences=2)
    print(f"   {summary}")

    # Test extraction
    print("\n[2] Information Extraction:")
    extracted = agent.extract(text, information_type="key technologies mentioned")
    print(f"   {extracted}")

    # Test classification
    review = "This product is amazing! Best purchase ever!"
    print("\n[3] Classification:")
    category = agent.classify(
        review,
        categories=["positive", "negative", "neutral"]
    )
    print(f"   {category}")


def main():
    """Main entry point."""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║         Example 02: Advanced Prompt Templates                     ║
║                                                                   ║
║  This demonstrates:                                              ║
║  • Basic templates with variables                               ║
║  • Multi-line structured templates                              ║
║  • Few-shot prompting                                           ║
║  • Chat templates (system + user)                               ║
║  • Production-ready prompt patterns                             ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Run examples
    examples = PromptTemplateExamples()
    examples.example_1_basic_template()
    examples.example_2_multiline_template()
    examples.example_3_few_shot_prompting()
    examples.example_4_chat_template()
    examples.example_5_conditional_template()

    # Production demo
    demo_production_agent()

    # Summary
    print("\n" + "="*70)
    print("✅ COMPLETE!")
    print("="*70)
    print("\n🎓 What you learned:")
    print("  1. Basic templates with variable substitution")
    print("  2. Multi-line templates for structure")
    print("  3. Few-shot prompting for better results")
    print("  4. Chat templates (system + user messages)")
    print("  5. Production patterns (summarize, extract, classify)")
    print("\n📖 Best Practices:")
    print("  • Be specific in your prompts")
    print("  • Use examples (few-shot) for complex tasks")
    print("  • Structure prompts with clear sections")
    print("  • Reuse templates for consistency")
    print("\n➡️  Next: python 03_chains_with_memory.py")
    print("="*70)


if __name__ == "__main__":
    main()
